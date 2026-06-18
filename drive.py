import unicodedata
import io
import json
from typing import Any, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from config import GOOGLE_SERVICE_ACCOUNT_JSON, DRIVE_FOLDER_ID

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
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


def _folder_clause(folder_id: Optional[str] = None) -> str:
    fid = (folder_id or DRIVE_FOLDER_ID or "").strip()
    return f" and '{fid}' in parents" if fid else ""


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


def search_files(q: str, limit: int = 20, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
    service = get_drive_service()
    safe_q = q.replace("'", "\\'")
    result = service.files().list(
        q=f"trashed = false and name contains '{safe_q}'{_folder_clause(folder_id)}",
        pageSize=limit,
        fields="files(id, name, mimeType, modifiedTime, webViewLink, size)",
        orderBy="modifiedTime desc",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    return result.get("files", [])


def get_file_metadata(file_id: str) -> Dict[str, Any]:
    return get_drive_service().files().get(
        fileId=file_id,
        fields="id, name, mimeType, modifiedTime, webViewLink, size",
        supportsAllDrives=True,
    ).execute()


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
    titles = [s["properties"]["title"] for s in metadata.get("sheets", [])]

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


def list_files_recursive(folder_id: Optional[str] = None, limit: int = 300) -> List[Dict[str, Any]]:
    service = get_drive_service()
    root_id = folder_id or DRIVE_FOLDER_ID
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

    if root_id:
        walk(root_id)

    return results

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

def normalize_text(value: str) -> str:
    value = (value or "").lower()
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = value.replace("_", " ").replace("-", " ")
    return " ".join(value.split())
    
def search_and_read(q: str, limit: int = 5, max_chars_per_file: int = 6000) -> List[Dict[str, Any]]:
                   query = normalize_text(q)
                   query_words = query.split()

    if not query:
       return []

    all_files = list_files_recursive(limit=300)
    scored_results: List[Dict[str, Any]] = []

    for file in all_files:
        if file.get("mimeType") == GOOGLE_FOLDER:
            continue

        raw_name = file.get("name") or ""
        name = normalize_text(raw_name)

        try:
            content = read_file_content(file["id"], file.get("mimeType"))
        except Exception as exc:
            file["read_error"] = str(exc)
            content = ""

        text = normalize_text(content or "")

        score = 0

        if query == name:
           score += 1000
        elif query in name:
             score += 700

        if query_words and all(word in name for word in query_words):
           score += 500

        if name.startswith("00 "):
           score += 300

        if "giới thiệu" in name:
           score += 300

           score += text.count(query) * 10

           for word in query.split():
               if word in name:
                  score += 30
                  score += text.count(word)

        if score > 0:
            file["score"] = score
            file["snippet"] = make_snippet(content, q, size=min(max_chars_per_file, 1200))
            file["content"] = content[:max_chars_per_file]
            scored_results.append(file)   
            
        scored_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return scored_results[:limit]
