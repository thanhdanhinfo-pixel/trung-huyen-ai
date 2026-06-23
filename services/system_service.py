from drive import read_by_path
from services.workspace import load_workspace

SYSTEM_CORE_FILES = {
    "protocol": "09_INFRASTRUCTURE/AI_PROTOCOLS/00_AI_PROTOCOL",
}


def self_test():
    result = {}
    try:
        result["workspace"] = load_workspace()
        result["workspace_ok"] = True
    except Exception as e:
        result["workspace_ok"] = False
        result["workspace_error"] = str(e)

    try:
        protocol = read_by_path(SYSTEM_CORE_FILES["protocol"])
        if protocol is None:
            result["protocol_ok"] = False
            result["protocol_error"] = "Protocol not found"
        else:
            result["protocol_ok"] = True
            result["protocol_size"] = len(protocol)
        result["protocol_path"] = SYSTEM_CORE_FILES["protocol"]
    except Exception as e:
        result["protocol_ok"] = False
        result["protocol_error"] = str(e)
        result["protocol_path"] = SYSTEM_CORE_FILES["protocol"]

    return {"status": "ok", "system": result}
