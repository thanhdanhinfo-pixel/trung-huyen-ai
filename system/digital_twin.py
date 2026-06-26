from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Dict, List

import yaml


class DigitalTwin:
    """Runtime interface for TRUNG_HUYEN_AI_OS digital twin state."""

    BASE = Path(__file__).parent
    FILE_NAME = 'DIGITAL_TWIN.yaml'

    def __init__(self, path: str | None = None):
        self.path = Path(path) if path else self.BASE / self.FILE_NAME

    def load(self) -> Dict[str, Any]:
        with open(self.path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def save(self, data: Dict[str, Any]) -> None:
        with open(self.path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

    def snapshot(self) -> Dict[str, Any]:
        data = self.load()
        return {
            'system_name': data.get('system_name'),
            'status': data.get('status'),
            'identity': data.get('identity', {}),
            'runtime': data.get('runtime', {}),
            'health': data.get('health', {}),
            'next_required_steps': self.predict_next_steps(),
        }

    def health(self) -> Dict[str, Any]:
        return self.load().get('health', {})

    def update_health(self, component: str, state: str) -> Dict[str, Any]:
        data = self.load()
        health = data.setdefault('health', {})
        health[component] = state
        data['last_updated'] = str(date.today())
        self.save(data)
        return health

    def append_evolution(self, event: str, event_date: str | None = None) -> List[Dict[str, str]]:
        data = self.load()
        history = data.setdefault('evolution_history', [])
        history.append({'date': event_date or str(date.today()), 'event': event})
        data['last_updated'] = str(date.today())
        self.save(data)
        return history

    def predict_next_steps(self) -> List[str]:
        data = self.load()
        return data.get('predictions', {}).get('next_required_steps', [])


digital_twin = DigitalTwin()
