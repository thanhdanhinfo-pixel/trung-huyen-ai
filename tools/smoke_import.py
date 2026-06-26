from __future__ import annotations

import importlib
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

print(f"SMOKE_IMPORT_ROOT={ROOT}")
print(f"SMOKE_IMPORT_CWD={Path.cwd()}")
print(f"SMOKE_IMPORT_SYSPATH0={sys.path[0]}")

MODULES = [
    "services.github_service",
    "services.execution_engine",
    "services.command_runner",
    "api.mcp",
    "mcp",
    "app",
]

failed = False

for module_name in MODULES:
    print(f"=== IMPORT {module_name} ===")
    try:
        importlib.import_module(module_name)
        print(f"OK: {module_name}")
    except Exception:
        failed = True
        print(f"FAIL: {module_name}")
        traceback.print_exc()

if failed:
    raise SystemExit(1)

print("SMOKE_IMPORT_OK")
