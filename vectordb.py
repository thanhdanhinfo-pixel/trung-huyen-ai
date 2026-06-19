from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION,
)

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


def ensure_collection():
    collections = client.get_collections().collections
    names = [c.name for c in collections]

    if QDRANT_COLLECTION not in names:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE,
            ),
        )

    return True
