def validate(answer:str, sources:list):
    return {
        "valid": bool(sources),
        "source_count": len(sources),
        "answer": answer
    }
