def build_citations(documents): 
    refs=[]
    for d in documents:
        refs.append({
            "id":d.get("id"),
            "name":d.get("name"),
            "link":d.get("webViewLink","")
        })
    return refs
