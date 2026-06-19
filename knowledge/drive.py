from googleapiclient.http import MediaInMemoryUpload

from drive import get_drive_service
from config import DRIVE_FOLDER_ID


def upload_markdown(filename: str, markdown: str):
    """
    Upload một file Markdown lên Google Drive.
    """

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

    return file
