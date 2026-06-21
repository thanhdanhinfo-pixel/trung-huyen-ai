from drive import search_and_read


def load_workspace():
    """
    Đọc AI_STATE và AI_KERNEL từ Google Drive.
    """

    state = search_and_read(
        q="00_AI_STATE",
        limit=1,
        max_chars_per_file=3000,
    )

    kernel = search_and_read(
        q="00_AI_KERNEL",
        limit=1,
        max_chars_per_file=3000,
    )

    return {
        "state": state,
        "kernel": kernel,
    }
def load_workspace():
    state = search_and_read(
        q="00_AI_STATE.md",
        limit=1,
        max_chars_per_file=3000,
    )

    kernel = search_and_read(
        q="00_AI_KERNEL",
        limit=1,
        max_chars_per_file=3000,
    )

    return {
        "status": "ok",
        "state": state,
        "kernel": kernel,
    }
