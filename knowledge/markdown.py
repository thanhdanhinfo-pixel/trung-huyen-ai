import re
import unicodedata


def safe_filename(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[^a-zA-Z0-9\s_-]", "", name)
    name = "_".join(name.split())
    return name.lower()
