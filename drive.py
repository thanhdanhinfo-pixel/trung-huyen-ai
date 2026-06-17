import json
from typing import Any, Dict, List

from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import GOOGLE_SERVICE_ACCOUNT_JSON, DRIVE_FOLDER_ID


SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def get_drive_service():
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON environment variable.")

    try:
        info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    except json.JSONDecodeError as exc:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON.") from exc

    credentials = service_account.Credentials.from_service_account_info(
        info,
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=credentials)


def list_files(limit: int = 50) -> List[Dict[str, Any]]:
    service = get_drive_service()

    query_parts = ["trashed = false"]
    if DRIVE_FOLDER_ID:
        query_parts.append(f"'{DRIVE_FOLDER_ID}' in parents")

    result = service.files().list(
        q=" and ".join(query_parts),
        pageSize=limit,
        fields="files(id, name, mimeType, modifiedTime, webViewLink)",
        orderBy="modifiedTime desc",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()

    return result.get("files", [])


def search_files(q: str, limit: int = 20) -> List[Dict[str, Any]]:
    service = get_drive_service()

    safe_q = q.replace("'", "\\'")
    query_parts = [
        "trashed = false",
        f"name contains '{safe_q}'",
    ]
    if DRIVE_FOLDER_ID:
        query_parts.append(f"'{DRIVE_FOLDER_ID}' in parents")

    result = service.files().list(
        q=" and ".join(query_parts),
        pageSize=limit,
        fields="files(id, name, mimeType, modifiedTime, webViewLink)",
        orderBy="modifiedTime desc",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()

    return result.get("files", [])
