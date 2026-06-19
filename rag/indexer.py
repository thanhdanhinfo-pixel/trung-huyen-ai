from typing import Any, Dict
from uuid import uuid4

from qdrant_client.models import PointStruct

from drive import list_files, read_file_content
from rag.chunker import split_text
from rag.embedding import embed_text
from vectordb import client, ensure_collection, COLLECTION_NAME


def index_drive(limit: int = 10, max_chars_per_file: int = 20000) -> Dict[str, Any]:
    ensure_collection()

    files = list_files(limit=limit)

    indexed_files = 0
    indexed_chunks = 0
    errors = []

    for file in files:
        file_id = file.get("id")
        name = file.get("name")
        link = file.get("webViewLink")
        mime_type = file.get("mimeType")
        modified_time = file.get("modifiedTime")

        try:
            if mime_type == "application/vnd.google-apps.folder":
                continue

            content = read_file_content(file_id=file_id)

            if not content:
                continue

            content = content[:max_chars_per_file]
            chunks = split_text(content)

            points = []

            for i, chunk in enumerate(chunks):
                vector = embed_text(chunk)

                points.append(
                    PointStruct(
                        id=str(uuid4()),
                        vector=vector,
                        payload={
                            "content": chunk,
                            "file_id": file_id,
                            "name": name,
                            "link": link,
                            "mimeType": mime_type,
                            "modifiedTime": modified_time,
                            "chunk_index": i,
                        },
                    )
                )

            if points:
                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points,
                )

                indexed_chunks += len(points)
                indexed_files += 1

        except Exception as exc:
            errors.append({
                "file_id": file_id,
                "name": name,
                "error": str(exc),
            })

    return {
        "status": "ok",
        "indexed_files": indexed_files,
        "indexed_chunks": indexed_chunks,
        "errors": errors,
    }
