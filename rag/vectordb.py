from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from config import QDRANT_URL, QDRANT_API_KEY

COLLECTION_NAME = "knowledge"

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


def ensure_collection():
    collections = client.get_collections()

    exists = any(
        c.name == COLLECTION_NAME
        for c in collections.collections
    )

    if exists:
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=1536,
            distance=Distance.COSINE,
        ),
    )
