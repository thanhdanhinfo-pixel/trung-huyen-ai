DEFAULT_TIMEOUT_SECONDS = 10
MAX_TIMEOUT_SECONDS = 30


def normalize_timeout(seconds: int | None = None) -> int:
    if seconds is None:
        return DEFAULT_TIMEOUT_SECONDS
    return max(1, min(int(seconds), MAX_TIMEOUT_SECONDS))
