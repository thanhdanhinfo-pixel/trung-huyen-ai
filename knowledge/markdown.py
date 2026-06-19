import re
import unicodedata


def safe_filename(name: str) -> str:
    # Bỏ dấu tiếng Việt
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")

    # Xóa ký tự đặc biệt
    name = re.sub(r"[^a-zA-Z0-9\s_-]", "", name)

    # Đổi khoảng trắng thành _
    name = "_".join(name.split())

    return name.lower()
