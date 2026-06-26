def record(command_name: str, payload: dict):
    return {
        'command': command_name,
        'payload': payload,
        'audited': True,
    }
