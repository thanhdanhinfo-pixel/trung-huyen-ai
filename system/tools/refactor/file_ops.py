from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_file(source: str, destination: str, *, overwrite: bool = False) -> dict[str, Any]:
    src = Path(source)
    dst = Path(destination)

    if not src.exists():
        raise FileNotFoundError(f"Source not found: {src}")
    if not src.is_file():
        raise ValueError(f"Source is not a file: {src}")
    if dst.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {dst}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    src_hash = sha256(src)
    dst_hash = sha256(dst)
    if src_hash != dst_hash:
        if dst.exists():
            dst.unlink()
        raise RuntimeError("Checksum mismatch after copy")

    return {
        "status": "ok",
        "operation": "copy_file",
        "source": str(src),
        "destination": str(dst),
        "size": dst.stat().st_size,
        "sha256": dst_hash,
    }


def move_file(source: str, destination: str, *, overwrite: bool = False) -> dict[str, Any]:
    src = Path(source)
    dst = Path(destination)

    if not src.exists():
        raise FileNotFoundError(f"Source not found: {src}")
    if not src.is_file():
        raise ValueError(f"Source is not a file: {src}")
    if dst.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {dst}")

    src_bytes = src.read_bytes()
    src_hash = sha256(src)
    dst_original = dst.read_bytes() if dst.exists() else None
    dst_existed = dst.exists()

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        dst_hash = sha256(dst)
        if src_hash != dst_hash:
            raise RuntimeError("Checksum mismatch after move copy phase")
        src.unlink()
        return {
            "status": "ok",
            "operation": "move_file",
            "source": str(src),
            "destination": str(dst),
            "size": dst.stat().st_size,
            "sha256": dst_hash,
        }
    except Exception:
        src.write_bytes(src_bytes)
        if dst_existed and dst_original is not None:
            dst.write_bytes(dst_original)
        elif dst.exists():
            dst.unlink()
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Safe copy/move file operations with checksum verification.")
    parser.add_argument("operation", choices=["copy", "move"])
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.operation == "copy":
        result = copy_file(args.source, args.destination, overwrite=args.overwrite)
    else:
        result = move_file(args.source, args.destination, overwrite=args.overwrite)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
