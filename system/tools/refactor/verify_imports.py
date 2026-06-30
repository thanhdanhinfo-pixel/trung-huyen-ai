from __future__ import annotations 

import importlib
import json
import sys
from typing import Any


def public_symbols(module: Any) -> list[str]:
    if hasattr(module, "__all__"):
        return sorted(str(x) for x in module.__all__)
    return sorted(k for k in vars(module).keys() if not k.startswith("_"))


def verify_imports(*modules: str) -> dict:
    results = []
    for name in modules:
        try:
            module = importlib.import_module(name)
            results.append({
                "module": name,
                "status": "ok",
                "public_symbols": public_symbols(module),
            })
        except Exception as exc:
            results.append({
                "module": name,
                "status": "error",
                "error_type": type(exc).__name__,
                "message": str(exc),
            })
    overall = "ok" if all(r["status"] == "ok" for r in results) else "error"
    return {"status": overall, "results": results}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python verify_imports.py <module> [module...]")
    report = verify_imports(*sys.argv[1:])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "ok":
        raise SystemExit(1)
