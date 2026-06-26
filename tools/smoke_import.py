from __future__ import annotations

import importlib
import traceback

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
