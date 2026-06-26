from __future__ import annotations

import json
from pathlib import Path

from system import system_awareness, digital_twin, observability

SNAPSHOT_PATH = Path(__file__).parent / 'runtime' / 'system_snapshot.json'


def boot():
    snapshot = {
        'awareness': system_awareness.snapshot(),
        'digital_twin': digital_twin.snapshot(),
        'observability': observability.system_snapshot(),
        'boot_state': 'OPERATIONAL',
    }

    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SNAPSHOT_PATH, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    return snapshot


if __name__ == '__main__':
    print(boot())
