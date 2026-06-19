from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from config import QDRANT_URL, QDRANT_API_KEY

COLLECTION_NAME = "trung_huyen_brain"

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

def ensure_collection():
    if not QDRANT_URL:
        raise RuntimeError("Missing QDRANT_URL")
    if not QDRANT_API_KEY:
        raise RuntimeError("Missing QDRANT_API_KEY")

    collections = client.get_collections().collections
    names = [c.name for c in collections]

    if COLLECTION_NAME not in names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE,
            ),
        )

    return True
