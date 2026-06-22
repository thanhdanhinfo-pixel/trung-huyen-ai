from drive import read_by_path

WORKSPACE_FILES = [
    "09_INFRASTRUCTURE/AI_PROTOCOLS/00_AI_PROTOCOL",
    "07_AI_FACTORY/00_AI_STATE.md",
    "07_AI_FACTORY/00_AI_KERNEL",
]


def load_workspace():
    workspace = {}

    for path in WORKSPACE_FILES:
        try:
            workspace[path] = read_by_path(path)
        except Exception as e:
            workspace[path] = {
                "error": str(e)
            }

    return {
        "status": "ok",
        "workspace": workspace,
    }
