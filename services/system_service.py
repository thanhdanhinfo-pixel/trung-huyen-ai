from drive import read_by_path
from services.workspace import load_workspace


def self_test():

    result = {}

    try:
        result["workspace"] = load_workspace()
        result["workspace_ok"] = True
    except Exception as e:
        result["workspace_ok"] = False
        result["workspace_error"] = str(e)

    try:
        protocol = read_by_path(
    "09_INFRASTRUCTURE/AI_PROTOCOLS/00_AI_PROTOCOL.md"
        )

        if protocol is None:
            result["protocol_ok"] = False
            result["protocol_error"] = "Protocol not found"
        else:
            result["protocol_ok"] = True
            result["protocol_size"] = len(protocol)

    except Exception as e:
        result["protocol_ok"] = False
        result["protocol_error"] = str(e)

    return {
        "status": "ok",
        "system": result,
    }
