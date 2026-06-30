from __future__ import annotations 

import sys
from pathlib import Path


def create_shim(path: str, target_module: str) -> dict:
    shim_path = Path(path)
    if not target_module or not target_module.replace('.', '').replace('_', '').isalnum():
        raise ValueError(f"Invalid target module: {target_module}")

    content = (
        "# Compatibility shim.\n"
        f"# Preferred import: {target_module}\n"
        f"from {target_module} import *\n"
    )
    shim_path.write_text(content, encoding="utf-8")
    return {
        "status": "ok",
        "path": str(shim_path),
        "target_module": target_module,
        "size": shim_path.stat().st_size,
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python create_shim.py <path> <target.module>")
    print(create_shim(sys.argv[1], sys.argv[2]))
