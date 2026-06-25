from drive import list_recursive, read_file_content
from config import drive_root_sources

CORE_NAMES = [
    "01_CURRENT_STATE.md",
    "02_CAPABILITY_REGISTRY.md",
    "03_RUNTIME_STATE.md",
    "04_SYSTEM_AWARENESS.md",
    "05_NEXT_OBJECTIVES.md",
    "06_LOAD_SYSTEM_BOOTSTRAP.md",
]


def safe_read_file(file_id):
    try:
        return read_file_content(file_id=file_id)
    except Exception as exc:
        return f"[READ_ERROR] {exc}"


def bootstrap_system():
    roots = drive_root_sources()
    files = list_recursive()

    system_files = [
        f for f in files
        if "00_SYSTEM_STATE" in f.get("path", "")
    ]

    return {
        "status": "ok",
        "system_name": "TRUNG_HUYEN_AI_OS",
        "drive_memory_root": "Google Drive",
        "roots": roots,
        "root_count": len(roots),
        "system_state_files": [
            {
                "name": f.get("name"),
                "path": f.get("path"),
                "mimeType": f.get("mimeType"),
                "id": f.get("id"),
            }
            for f in system_files
        ],
        "available_tools": [
            "pingMcp",
            "createFolder",
            "createDocument",
            "appendDocument",
            "bootstrapSystem",
        ],
    }
