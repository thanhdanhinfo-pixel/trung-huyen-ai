def build_context(documents:list)->str: 
    parts=[]
    for d in documents:
        parts.append(f"# {d.get('name','')}\n{d.get('content','')}")
    return "\n\n".join(parts)
