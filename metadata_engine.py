def build_metadata(document:dict):
    return {
        "id":document.get("id"),
        "name":document.get("name"),
        "mimeType":document.get("mimeType"),
        "modifiedTime":document.get("modifiedTime"),
        "size":len(document.get("content",""))
    }
