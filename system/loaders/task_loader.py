from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import yaml

TASK_REGISTRY_PATH = Path('system/TASK_REGISTRY.yaml')


def load_task_registry() -> Dict[str, Any]:
    if not TASK_REGISTRY_PATH.exists():
        return {}
    return yaml.safe_load(TASK_REGISTRY_PATH.read_text(encoding='utf-8')) or {}


def current_active_task() -> Dict[str, Any]:
    return load_task_registry().get('current_active_task', {})


def unfinished_tasks() -> List[Dict[str, Any]]:
    data = load_task_registry()
    waiting = data.get('waiting_tasks', []) or []
    current = data.get('current_active_task', {}) or {}
    if current and current.get('status') not in ('done','completed','closed'):
        return [current, *waiting]
    return waiting
