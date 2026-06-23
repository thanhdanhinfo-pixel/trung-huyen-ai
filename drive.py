import io
import json
import unicodedata
from typing import Any, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from config import (
    DRIVE_FOLDER_ID,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    drive_root_sources,
    master_document_source,
)

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
]

GOOGLE_DOC = "application/vnd.google-apps.document"
GOOGLE_SHEET = "application/vnd.google-apps.spreadsheet"
GOOGLE_FOLDER = "application/vnd.google-apps.folder"


def _credentials():
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON environment variable.")

    try:
        info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    except json.JSONDecodeError as exc:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON.") from exc

    return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)


def get_drive_service():
    return build("drive", "v3", credentials=_credentials(), cache_discovery=False)


def get_docs_service():
    return build("docs", "v1", credentials=_credentials(), cache_discovery=False)


def get_sheets_service():
    return build("sheets", "v4", credentials=_credentials(), cache_discovery=False)


def _configured_drive_roots() -> List[Dict[str, str]]:
    """
    Return configured Drive roots.

    Preferred source: KNOWLEDGE_SOURCES drive entries.
    Backward-compatible fallback: DRIVE_FOLDER_ID.
    """
    roots = drive_root_sources()
    if roots:
        return roots
    if DRIVE_FOLDER_ID:
        return [{"type": "drive", "name": "default", "id": DRIVE_FOLDER_ID}]
    return []


def _root_folder_id(folder_id: Optional[str] = None) -> str:
    fid = (folder_id or "").strip()
    if fid:
        return fid

    roots = _configured_drive_roots()
    if roots:
        return roots[0]["id"]

    raise RuntimeError("Missing DRIVE_FOLDER_ID or KNOWLEDGE_SOURCES drive source.")


def _folder_clause(folder_id: Optional[str] = None) -> str:
    fid = (folder_id or "").strip()
    if not fid:
        roots = _configured_drive_roots()
        if len(roots) == 1:
            fid = roots[0]["id"]
    return f" and '{fid}' in parents" if fid else ""


# =====================================
# READ / LIST
# =====================================

def list_files(limit: int = 50, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
    service = get_drive_service()

    if not folder_id and len(_configured_drive_roots()) > 1:
        results: List[Dict[str, Any]] = []
        per_root_limit = max(limit, 1)
        for source in _configured_drive_roots():
            for item in list_files(limit=per_root_limit, folder_id=source["id"]):
                enriched = dict(item)
                enriched["source"] = source.get("name")
                enriched["source_id"] = source.get("id")
                results.append(enriched)
                if len(results) >= limit:
                    return results
        return results

    result = service.files().list(
        q=f"trashed = false{_folder_clause(folder_id)}",
        pageSize=limit,
        fields="files(id, name, mimeType, modifiedTime, webViewLink, size)",
        orderBy="modifiedTime desc",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    return result.get("files", [])


def list_files_recursive(folder_id: Optional[str] = None, limit: int = 300) -> List[Dict[str, Any]]:
    if not folder_id and len(_configured_drive_roots()) > 1:
        results: List[Dict[str, Any]] = []
        for source in _configured_drive_roots():
            remaining = limit - len(results)
            if remaining <= 0:
                break
            for item in list_files_recursive(folder_id=source["id"], limit=remaining):
                enriched = dict(item)
                enriched["source"] = source.get("name")
                enriched["source_id"] = source.get("id")
                results.append(enriched)
                if len(results) >= limit:
                    break
        return results

    service = get_drive_service()
    root_id = _root_folder_id(folder_id)
    results: List[Dict[str, Any]] = []

    def walk(fid: str):
        nonlocal results
        if len(results) >= limit:
            return

        page_token = None
        while True:
            response = service.files().list(
                q=f"trashed = false and '{fid}' in parents",
                pageSize=100,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink, size)",
                orderBy="modifiedTime desc",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            ).execute()

            for item in response.get("files", []):
                if len(results) >= limit:
                    return
                results.append(item)
                if item.get("mimeType") == GOOGLE_FOLDER:
                    walk(item["id"])

            page_token = response.get("nextPageToken")
            if not page_token:
                break

    walk(root_id)
    return results


def list_recursive(parent_id: Optional[str] = None, current_path: str = "") -> List[Dict[str, Any]]:
    if not parent_id and not current_path and len(_configured_drive_roots()) > 1:
        items: List[Dict[str, Any]] = []
        for source in _configured_drive_roots():
            source_name = source.get("name") or "source"
            source_root = {
                "id": source["id"],
                "name": source_name,
                "path": source_name,
                "mimeType": GOOGLE_FOLDER,
                "source": source_name,
                "source_id": source["id"],
            }
            items.append(source_root)
            for child in list_recursive(source["id"], source_name):
                enriched = dict(child)
                enriched["source"] = source_name
                enriched["source_id"] = source["id"]
                items.append(enriched)
        master = master_document_source()
        if master:
            try:
                metadata = get_file_metadata(master["id"])
                metadata["path"] = master.get("name", "master")
                metadata["source"] = master.get("name", "master")
                metadata["source_id"] = master.get("id")
                items.append(metadata)
            except Exception as exc:
                items.append({
                    "id": master["id"],
                    "name": master.get("name", "master"),
                    "path": master.get("name", "master"),
                    "mimeType": GOOGLE_DOC,
                    "source": master.get("name", "master"),
                    "source_id": master.get("id"),
                    "read_error": str(exc),
                })
        return items

    service = get_drive_service()
    parent_id = _root_folder_id(parent_id)
    query = f"'{parent_id}' in parents and trashed=false"
    result = service.files().list(
        q=query,
        fields="files(id,name,mimeType,webViewLink,modifiedTime)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()

    items: List[Dict[str, Any]] = []
    for item in result.get("files", []):
        path = f"{current_path}/{item['name']}".strip("/")
        item["path"] = path
        items.append(item)
        if item["mimeType"] == GOOGLE_FOLDER:
            items.extend(list_recursive(item["id"], path))
    return items


def find_file_by_path(path: str):
    target = path.strip("/")
    for item in list_recursive():
        if item.get("path") == target:
            return item
    return None


def read_by_path(path: str):
    item = find_file_by_path(path)
    if not item:
        return None
    return read_file_content(item["id"])


def read_folder(path: str):
    prefix = path.strip("/") + "/"
    return [item for item in list_recursive() if item.get("path", "").startswith(prefix)]


def get_file_metadata(file_id: str) -> Dict[str, Any]:
    return get_drive_service().files().get(
        fileId=file_id,
        fields="id, name, mimeType, modifiedTime, webViewLink, size, parents",
        supportsAllDrives=True,
    ).execute()


# =====================================
# WRITE / MANAGE
# =====================================

def create_folder(name: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
    service = get_drive_service()
    metadata = {
        "name": name,
        "mimeType": GOOGLE_FOLDER,
        "parents": [_root_folder_id(parent_id)],
    }
    return service.files().create(
        body=metadata,
        fields="id, name, mimeType, webViewLink, parents",
        supportsAllDrives=True,
    ).execute()


def create_google_doc(name: str, content: str = "", parent_id: Optional[str] = None) -> Dict[str, Any]:
    service = get_drive_service()
    metadata = {
        "name": name,
        "mimeType": GOOGLE_DOC,
        "parents": [_root_folder_id(parent_id)],
    }
    doc = service.files().create(
        body=metadata,
        fields="id, name, mimeType, webViewLink, parents",
        supportsAllDrives=True,
    ).execute()

    if content:
        append_google_doc(doc["id"], content)
    return doc


def move_file(file_id: str, new_parent_id: str) -> Dict[str, Any]:
    service = get_drive_service()
    metadata = service.files().get(
        fileId=file_id,
        fields="parents",
        supportsAllDrives=True,
    ).execute()
    previous_parents = ",".join(metadata.get("parents", []))
    return service.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=previous_parents,
        fields="id, name, parents, webViewLink",
        supportsAllDrives=True,
    ).execute()


def rename_file(file_id: str, name: str) -> Dict[str, Any]:
    return get_drive_service().files().update(
        fileId=file_id,
        body={"name": name},
        fields="id, name, mimeType, webViewLink",
        supportsAllDrives=True,
    ).execute()


def grant_permission(file_id: str, email: str, role: str = "reader") -> Dict[str, Any]:
    body = {
        "type": "user",
        "role": role,
        "emailAddress": email,
    }
    return get_drive_service().permissions().create(
        fileId=file_id,
        body=body,
        fields="id, type, role, emailAddress",
        supportsAllDrives=True,
        sendNotificationEmail=False,
    ).execute()


# =====================================
# READ CONTENT
# =====================================

def read_google_doc(file_id: str) -> str:
    doc = get_docs_service().documents().get(documentId=file_id).execute()
    parts: List[str] = []
    for element in doc.get("body", {}).get("content", []):
        paragraph = element.get("paragraph")
        if not paragraph:
            continue
        for item in paragraph.get("elements", []):
            text_run = item.get("textRun")
            if text_run:
                parts.append(text_run.get("content", ""))
    return "".join(parts).strip()


def read_google_sheet(file_id: str, max_rows_per_sheet: int = 200) -> str:
    sheets = get_sheets_service()
    metadata = sheets.spreadsheets().get(spreadsheetId=file_id).execute()
    titles = [sheet["properties"]["title"] for sheet in metadata.get("sheets", [])]

    output: List[str] = []
    for title in titles:
        values = sheets.spreadsheets().values().get(
            spreadsheetId=file_id,
            range=f"'{title}'!A1:Z{max_rows_per_sheet}",
        ).execute().get("values", [])

        output.append(f"# Sheet: {title}")
        for row in values:
            output.append(" | ".join(str(cell) for cell in row))
        output.append("")

    return "\n".join(output).strip()


def download_file_bytes(file_id: str) -> bytes:
    request = get_drive_service().files().get_media(fileId=file_id, supportsAllDrives=True)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return fh.getvalue()


def download_text_file(file_id: str) -> str:
    return download_file_bytes(file_id).decode("utf-8", errors="replace").strip()


def read_pdf_bytes(data: bytes) -> str:
    try:
        import fitz
        doc = fitz.open(stream=data, filetype="pdf")
        return "\n".join(page.get_text() for page in doc).strip()
    except Exception:
        return ""


def read_docx_bytes(data: bytes) -> str:
    try:
        from docx import Document
        document = Document(io.BytesIO(data))
        return "\n".join(p.text for p in document.paragraphs).strip()
    except Exception:
        return ""


def read_excel_bytes(data: bytes) -> str:
    try:
        import pandas as pd
        sheets = pd.read_excel(io.BytesIO(data), sheet_name=None)
        output = []
        for name, df in sheets.items():
            output.append(f"# Sheet: {name}")
            output.append(df.to_string(index=False))
        return "\n\n".join(output).strip()
    except Exception:
        return ""


def read_file_content(file_id: str, mime_type: Optional[str] = None) -> str:
    metadata = get_file_metadata(file_id)
    actual_mime = mime_type or metadata.get("mimeType", "")
    name = metadata.get("name", "").lower()

    if actual_mime == GOOGLE_FOLDER:
        return ""
    if actual_mime == GOOGLE_DOC:
        return read_google_doc(file_id)
    if actual_mime == GOOGLE_SHEET:
        return read_google_sheet(file_id)
    if actual_mime.startswith("text/") or name.endswith((".txt", ".md", ".csv", ".json")):
        return download_text_file(file_id)

    data = download_file_bytes(file_id)
    if actual_mime == "application/pdf" or name.endswith(".pdf"):
        return read_pdf_bytes(data)
    if name.endswith(".docx"):
        return read_docx_bytes(data)
    if name.endswith((".xlsx", ".xls")):
        return read_excel_bytes(data)
    return ""


# =====================================
# SEARCH
# =====================================

def normalize_text(value: str) -> str:
    value = (value or "").lower()
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = value.replace("_", " ").replace("-", " ").replace(".", " ")
    return " ".join(value.split())


def make_snippet(text: str, query: str, size: int = 1200) -> str:
    if not text:
        return ""
    lower_text = text.lower()
    lower_query = query.lower().strip()
    index = lower_text.find(lower_query)
    if index == -1:
        return text[:size]
    start = max(index - size // 3, 0)
    end = min(index + size, len(text))
    return text[start:end].strip()


def score_document(query: str, query_words: List[str], name: str, text: str) -> int:
    score = 0
    if name.startswith("00 "):
        score += 300
    if "gioi thieu" in name:
        score += 300
    if "gioi thieu he quan sat" in name:
        score += 5000
    if "he quan sat" in name:
        score += 3000
    if query == name:
        score += 1000
    elif query in name:
        score += 700
    if query_words and all(word in name for word in query_words):
        score += 500
    if query:
        score += text.count(query) * 10
    for word in query_words:
        if word in name:
            score += 30
        score += text.count(word)
    return score


def search_files(q: str, limit: int = 20):
    query = normalize_text(q)
    query_words = query.split()
    results = []
    for item in list_files_recursive(limit=300):
        name = normalize_text(item.get("name", ""))
        if query in name or all(word in name for word in query_words):
            results.append(item)
    return results[:limit]


def _master_doc_result() -> Optional[Dict[str, Any]]:
    master = master_document_source()
    if not master:
        return None
    try:
        metadata = get_file_metadata(master["id"])
        metadata["source"] = master.get("name", "master")
        metadata["source_id"] = master.get("id")
        return metadata
    except Exception:
        return {
            "id": master["id"],
            "name": master.get("name", "master"),
            "mimeType": GOOGLE_DOC,
            "source": master.get("name", "master"),
            "source_id": master.get("id"),
        }


def search_and_read(q: str, limit: int = 5, max_chars_per_file: int = 6000) -> List[Dict[str, Any]]:
    query = normalize_text(q)
    query_words = query.split()
    if not query:
        return []

    candidates = list_files_recursive(limit=300)
    master_candidate = _master_doc_result()
    if master_candidate:
        candidates.append(master_candidate)

    scored_results: List[Dict[str, Any]] = []
    seen_ids = set()
    for file in candidates:
        if file.get("mimeType") == GOOGLE_FOLDER:
            continue
        if file.get("id") in seen_ids:
            continue
        seen_ids.add(file.get("id"))

        raw_name = file.get("name") or ""
        name = normalize_text(raw_name)
        try:
            content = read_file_content(file["id"], file.get("mimeType"))
        except Exception as exc:
            file["read_error"] = str(exc)
            content = ""

        text = normalize_text(content or "")
        score = score_document(query, query_words, name, text)
        if score > 0:
            result = dict(file)
            result["score"] = score
            result["snippet"] = make_snippet(content, q, size=min(max_chars_per_file, 1200))
            result["content"] = content[:max_chars_per_file]
            scored_results.append(result)

    scored_results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored_results[:limit]


def append_google_doc(file_id: str, content: str) -> dict:
    docs = get_docs_service()
    document = docs.documents().get(documentId=file_id).execute()
    end_index = document["body"]["content"][-1]["endIndex"] - 1

    docs.documents().batchUpdate(
        documentId=file_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": end_index},
                        "text": "\n" + content,
                    }
                }
            ]
        },
    ).execute()

    return {"status": "ok", "file_id": file_id, "action": "append_google_doc"}
