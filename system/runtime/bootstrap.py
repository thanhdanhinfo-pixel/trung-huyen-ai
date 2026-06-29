from __future__ import annotations
import json
from pathlib import Path
from system import system_awareness, digital_twin, observability, event_bus
import yaml
SNAPSHOT_PATH=Path(__file__).parent/'system_snapshot.json'
def boot():
    try:
        task_registry = yaml.safe_load(Path('system/TASK_REGISTRY.yaml').read_text(encoding='utf-8')) or {}
    except Exception:
        task_registry = {}
    snapshot={'awareness':system_awareness.snapshot(),'digital_twin':digital_twin.snapshot(),'observability':observability.system_snapshot(),'task_registry':task_registry,'boot_state':'OPERATIONAL'}
    SNAPSHOT_PATH.parent.mkdir(parents=True,exist_ok=True)
    with open(SNAPSHOT_PATH,'w',encoding='utf-8') as f:
        json.dump(snapshot,f,ensure_ascii=False,indent=2)
    event_bus.publish('BOOT_COMPLETED',{'boot_state':'OPERATIONAL'})
    return snapshot
if __name__=='__main__':
    print(boot())
