from services.sync_service import sync_drive
from services.embedding_pipeline import build_embeddings

def run():
    result=sync_drive()
    # TODO: đọc dữ liệu đã đồng bộ để build embedding
    return {
        "status":"ok",
        "sync":result,
        "embedding":"pending"
    }
