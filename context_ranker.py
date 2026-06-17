def rank_context(chunks:list):
    return sorted(chunks, key=lambda x: len(x), reverse=True)
