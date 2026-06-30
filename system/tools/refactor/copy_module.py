from __future__ import annotations 

import hashlib
import shutil
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_module(source: str, destination: str) -> dict:
    src = Path(source)
    dst = Path(destination)

    if not src.exists():
        raise FileNotFoundError(f"Source not found: {src}")
    if not src.is_file():
        raise ValueError(f"Source is not a file: {src}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    src_hash = sha256(src)
    dst_hash = sha256(dst)
    if src_hash != dst_hash:
        raise RuntimeError("Checksum mismatch after copy")

    return {
        "status": "ok",
        "source": str(src),
        "destination": str(dst),
        "size": dst.stat().st_size,
        "sha256": dst_hash,
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python copy_module.py <source> <destination>")
    print(copy_module(sys.argv[1], sys.argv[2]))
