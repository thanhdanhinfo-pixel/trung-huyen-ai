from drive import list_recursive, read_by_path


def safe_read(path: str):
    try:
        return read_by_path(path)
    except Exception:
        return None


def bootstrap_system():
    files = list_recursive()

    return {
        "status": "ok",
        "system_name": "TRUNG_HUYEN_AI_OS",

        "system_awareness": safe_read(
            "00_SYSTEM/SYSTEM_AWARENESS.md"
        ),

        "self_state": safe_read(
            "00_SYSTEM/SELF_STATE.md"
        ),

        "capability_registry": safe_read(
            "00_SYSTEM/CAPABILITY_REGISTRY.md"
        ),

        "current_context": safe_read(
            "00_SYSTEM/CURRENT_CONTEXT.md"
        ),

        "active_projects": [
            f["name"]
            for f in files
            if f.get("mimeType")
            == "application/vnd.google-apps.folder"
        ][:20],

        "recent_documents": [
            f["name"]
            for f in files
            if "folder" not in f.get("mimeType", "")
        ][:20],

        "available_tools": [
            "createFolder",
            "createDocument",
            "appendDocument",
            "pingMcp",
            "bootstrapSystem"
        ]
    }
