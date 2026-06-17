import json
from pathlib import Path

CACHE=Path("storage/cache/document_cache.json")

def save(data):
    CACHE.parent.mkdir(parents=True,exist_ok=True)
    CACHE.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")

def load():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return []
