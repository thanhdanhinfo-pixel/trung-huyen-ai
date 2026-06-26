"""Compatibility shim to avoid circular imports.
Preferred implementation lives in system.observability.healing.
"""

from importlib import import_module
from typing import Any

_TARGET = 'system.observability.healing'


def __getattr__(name: str) -> Any:
    module = import_module(_TARGET)
    return getattr(module, name)


def health() -> dict:
    try:
        module = import_module(_TARGET)
        if hasattr(module, 'health'):
            return module.health()
        return {'status': 'ok', 'mode': 'lazy-shim'}
    except Exception as exc:
        return {
            'status': 'degraded',
            'error_type': type(exc).__name__,
            'message': str(exc),
        }
