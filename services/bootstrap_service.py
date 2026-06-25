from drive import list_recursive


def bootstrap_system():
    files = list_recursive()

    return {
        "status": "ok",
        "system_name": "TRUNG_HUYEN_AI_OS",
        "drive_memory_root": "Google Drive",
        "files": [
            {
                "name": f.get("name"),
                "path": f.get("path"),
                "mimeType": f.get("mimeType"),
                "id": f.get("id"),
            }
            for f in files
        ][:100],
    }
