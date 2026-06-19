from typing import Dict, Any

from drive import list_files, read_file_content
from rag.chunker import split_text
from rag.embedding import embed_text
from rag.vectordb import collection


def index_drive(limit: int = 10, max_chars_per_file: int = 20000) -> Dict[str, Any]:
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

            for i, chunk in enumerate(chunks):
                vector = embed_text(chunk)
                chunk_id = f"{file_id}_{i}"

                collection.upsert(
                    ids=[chunk_id],
                    embeddings=[vector],
                    documents=[chunk],
                    metadatas=[{
                        "file_id": file_id,
                        "name": name,
                        "link": link,
                        "mimeType": mime_type,
                        "modifiedTime": modified_time,
                        "chunk_index": i,
                    }]
                )

                indexed_chunks += 1

            indexed_files += 1

        except Exception as exc:
            errors.append({
                "file_id": file_id,
                "name": name,
                "error": str(exc)
            })

    return {
        "status": "ok",
        "indexed_files": indexed_files,
        "indexed_chunks": indexed_chunks,
        "errors": errors,
    }
