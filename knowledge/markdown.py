import re
import unicodedata


def safe_filename(name: str) -> str:
    """
    Chuyển tiêu đề thành tên file an toàn.
    Ví dụ:
    "Vai trò từng thư mục" -> "vai_tro_tung_thu_muc"
    """

    # Bỏ dấu tiếng Việt
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")

    # Chữ thường
    name = name.lower()

    # Thay khoảng trắng bằng _
    name = re.sub(r"\s+", "_", name)

    # Xóa ký tự đặc biệt
    name = re.sub(r"[^a-z0-9_]", "", name)

    # Gộp nhiều dấu _
    name = re.sub(r"_+", "_", name)

    # Bỏ _ ở đầu/cuối
    name = name.strip("_")

    return name    filename = filename.strip("_")

    return filename
