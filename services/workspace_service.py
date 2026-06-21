from drive import search_and_read


def load_workspace():
    """
    Bản nhẹ để test Workspace.
    Chỉ đọc AI_STATE trước, chưa đọc AI_KERNEL để tránh chậm/treo.
    """

    state = search_and_read(
        q="00_AI_STATE.md",
        limit=1,
        max_chars_per_file=1000,
    )

    return {
        "status": "ok",
        "mode": "workspace_light",
        "state": state,
        "kernel": [],
    }
    return {
        "status": "ok",
        "state": state,
        "kernel": kernel,
    }
