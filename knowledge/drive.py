from typing import Any, Dict

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaInMemoryUpload

from drive import get_drive_service
from config import DRIVE_FOLDER_ID


def upload_markdown(filename: str, markdown: str) -> Dict[str, Any]:
    """
    Upload một file Markdown lên Google Drive.

    Hàm này không để exception thoát ra ngoài. Mọi lỗi đều được chuẩn hóa
    để API phía trên có thể trả về thông tin rõ ràng thay vì 500 mù.
    """
    try:
        service = get_drive_service()

        metadata = {
            "name": filename,
            "mimeType": "text/markdown",
        }

        if DRIVE_FOLDER_ID:
            metadata["parents"] = [DRIVE_FOLDER_ID]

        media = MediaInMemoryUpload(
            markdown.encode("utf-8"),
            mimetype="text/markdown",
            resumable=False,
        )

        file = (
            service.files()
            .create(
                body=metadata,
                media_body=media,
                fields="id,name,webViewLink",
                supportsAllDrives=True,
            )
            .execute()
        )

        return {
            "status": "ok",
            "stage": "drive_upload",
            "file": file,
        }

    except HttpError as exc:
        return {
            "status": "error",
            "stage": "drive_upload",
            "error_type": "GoogleDriveHttpError",
            "message": str(exc),
            "folder_id": DRIVE_FOLDER_ID,
        }

    except Exception as exc:
        return {
            "status": "error",
            "stage": "drive_upload",
            "error_type": type(exc).__name__,
            "message": str(exc),
            "folder_id": DRIVE_FOLDER_ID,
        }
