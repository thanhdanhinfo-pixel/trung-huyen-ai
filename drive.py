import io 
import json
import os
import unicodedata
from typing import Any, Dict, List, Optional

import google.auth
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from functools import lru_cache
from config import (
    DRIVE_FOLDER_ID,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REFRESH_TOKEN,
)

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
]

GOOGLE_DOC = "application/vnd.google-apps.document"
GOOGLE_SHEET = "application/vnd.google-apps.spreadsheet"
GOOGLE_FOLDER = "application/vnd.google-apps.folder"


def credential_source() -> Dict[str, Any]:
    auth_mode = os.getenv("DRIVE_AUTH_MODE", "service_account").strip().lower()
    return {
        "auth_mode": auth_mode,
        "oauth_configured": bool(
            GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_REFRESH_TOKEN
        ),
        "service_account_configured": bool(GOOGLE_SERVICE_ACCOUNT_JSON),
    }


def _credentials():
    auth_mode = os.getenv("DRIVE_AUTH_MODE", "service_account").strip().lower()

    if auth_mode == "adc":
        credentials, _ = google.auth.default(scopes=SCOPES)
        return credentials

    if auth_mode == "oauth":
        if not (
            GOOGLE_CLIENT_ID
            and GOOGLE_CLIENT_SECRET
            and GOOGLE_REFRESH_TOKEN
        ):
            raise RuntimeError(
                "DRIVE_AUTH_MODE=oauth but OAuth credentials are incomplete."
            )

        return Credentials(
            None,
            refresh_token=GOOGLE_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=SCOPES,
        )

    if auth_mode not in {"service_account", "service-account", "sa"}:
        raise RuntimeError(
            f"Unsupported DRIVE_AUTH_MODE={auth_mode!r}. "
            "Use 'adc', 'service_account' or 'oauth'."
        )

    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON")

    try:
        info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON."
        ) from exc

    return service_account.Credentials.from_service_account_info(
        info,
        scopes=SCOPES,
    )

def get_drive_service():
    return build("drive", "v3", credentials=_credentials(), cache_discovery=False)


def get_docs_service():
    return build("docs", "v1", credentials=_credentials(), cache_discovery=False)


def get_sheets_service():
    return build("sheets", "v4", credentials=_credentials(), cache_discovery=False)


def _root_folder_id(folder_id: Optional[str] = None) -> str:
    fid = (folder_id or "").strip()
    if fid:
        return fid
    if DRIVE_FOLDER_ID:
        return DRIVE_FOLDER_ID
    raise RuntimeError("Missing DRIVE_FOLDER_ID")


def _folder_clause(folder_id: Optional[str] = None) -> str:
    fid = _root_folder_id(folder_id)
    return f" and '{fid}' in parents"


# =====================================
# READ / LIST
# =====================================

def list_files(limit: int = 50, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
    service = get_drive_service()

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


def list_recursive(parent_id: Optional[str] = None, current_path: str = "", limit: Optional[int] = None, _counter: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    service = get_drive_service()
    parent_id = _root_folder_id(parent_id)
    counter = _counter or [0]

    if limit is not None and counter[0] >= limit:
        return []

    query = f"'{parent_id}' in parents and trashed=false"
    items: List[Dict[str, Any]] = []
    page_token = None

    while True:
        result = service.files().list(
            q=query,
            pageSize=100,
            pageToken=page_token,
            fields="nextPageToken,files(id,name,mimeType,webViewLink,modifiedTime)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()

        for item in result.get("files", []):
            if limit is not None and counter[0] >= limit:
                return items

            path = f"{current_path}/{item['name']}".strip("/")
            item["path"] = path
            items.append(item)
            counter[0] += 1

            if item["mimeType"] == GOOGLE_FOLDER:
                items.extend(list_recursive(item["id"], path, limit=limit, _counter=counter))

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    return items


@lru_cache(maxsize=1)
def get_path_index():
    print("BUILDING DRIVE PATH INDEX...")

    items = list_recursive()

    print(f"TOTAL ITEMS: {len(items)}")

    return {
        item["path"]: item
        for item in items
        if item.get("path")
    }


def find_file_by_path(path: str):
    target = path.strip("/")
    return get_path_index().get(target)


def read_by_path(path: str):
    item = find_file_by_path(path)
    if not item:
        return None
    return read_file_content(item["id"])


def read_folder(path: str):

    prefix = path.strip("/") + "/"

    index = get_path_index()

    return [
        item
        for item in index.values()
        if item.get("path", "").startswith(prefix)
    ]

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


def search_and_read(q: str, limit: int = 5, max_chars_per_file: int = 6000) -> List[Dict[str, Any]]:
    query = normalize_text(q)
    query_words = query.split()
    if not query:
        return []

    candidates = list_files_recursive(limit=30)

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


# =====================================
# KNOWLEDGE MAP / TREE SUMMARY
# =====================================

def build_tree_summary(limit: int = 2000) -> Dict[str, Any]:
    """Build a compact top-level summary of Google Drive without reading file contents."""
    from collections import Counter

    items = list_recursive(limit=limit)
    domains = Counter()
    mime_types = Counter()

    for item in items:
        path = item.get("path") or item.get("name") or "ROOT"
        root = path.split("/")[0] if path else "ROOT"
        domains[root] += 1
        mime_types[item.get("mimeType", "unknown")] += 1

    return {
        "status": "ok",
        "mode": "tree_summary",
        "total_entries": len(items),
        "domains": [
            {"name": name, "entries": count}
            for name, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)
        ],
        "mime_types": dict(mime_types),
        "policy": {
            "read_contents": False,
            "purpose": "overview_without_context_overload",
        },
    }


# =====================================
# KNOWLEDGE MAP / TREE SUMMARY
# =====================================

def build_tree_summary(limit: int = 2000) -> Dict[str, Any]:
    """Build a compact top-level summary of Google Drive without reading file contents."""
    from collections import Counter

    items = list_recursive(limit=limit)
    domains = Counter()
    mime_types = Counter()

    for item in items:
        path = item.get("path") or item.get("name") or "ROOT"
        root = path.split("/")[0] if path else "ROOT"
        domains[root] += 1
        mime_types[item.get("mimeType", "unknown")] += 1

    return {
        "status": "ok",
        "mode": "tree_summary",
        "total_entries": len(items),
        "domains": [
            {"name": name, "entries": count}
            for name, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)
        ],
        "mime_types": dict(mime_types),
        "policy": {
            "read_contents": False,
            "purpose": "overview_without_context_overload",
        },
    }
