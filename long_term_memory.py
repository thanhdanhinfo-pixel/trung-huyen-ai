import json
from pathlib import Path 

DB = Path("storage/memory/long_term_memory.json")


class LongTermMemory:
    def __init__(self):
        self.items = self.load()

    def save(self, item):
        self.items.append(item)
        self._write()
        return len(self.items)

    def all(self):
        return self.items

    def clear(self):
        self.items = []
        self._write()

    def _write(self):
        DB.parent.mkdir(parents=True, exist_ok=True)
        DB.write_text(
            json.dumps(self.items, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def load(self):
        if DB.exists():
            try:
                return json.loads(DB.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []
