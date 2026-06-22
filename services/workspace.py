from drive import read_by_path

WORKSPACE_FILES = [
    "09_INFRASTRUCTURE/AI_PROTOCOLS/00_AI_PROTOCOL.md",
    "09_INFRASTRUCTURE/AI_STATE/00_AI_STATE.md",
    "09_INFRASTRUCTURE/AI_KERNEL/00_AI_KERNEL.md",
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
