from rag.embedding import embed_text
from rag.vectordb import collection


def search_knowledge(query: str, limit: int = 5):
    vector = embed_text(query)

    result = collection.query(
        query_embeddings=[vector],
        n_results=limit
    )

    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    output = []

    for doc, meta, distance in zip(docs, metas, distances):
        output.append({
            "score": distance,
            "content": doc,
            "metadata": meta
        })

    return output
