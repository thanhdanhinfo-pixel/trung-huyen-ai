from rag.embedding import embed_text
from vectordb import client, COLLECTION_NAME, ensure_collection


def search_knowledge(query: str, limit: int = 5):
    ensure_collection()

    vector = embed_text(query)

    result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=limit,
        with_payload=True,
    )

    output = []

    for item in result.points:
        payload = item.payload or {}

        output.append({
            "score": item.score,
            "content": payload.get("content"),
            "metadata": {
                "file_id": payload.get("file_id"),
                "name": payload.get("name"),
                "link": payload.get("link"),
                "mimeType": payload.get("mimeType"),
                "modifiedTime": payload.get("modifiedTime"),
                "chunk_index": payload.get("chunk_index"),
            }
        })

    return output
