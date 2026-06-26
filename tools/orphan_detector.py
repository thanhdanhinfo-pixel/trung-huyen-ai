import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
orphans=[p.name for p in ROOT.glob('*.py') if '_' in p.stem]
out=ROOT/'artifacts'; out.mkdir(exist_ok=True)
(out/'orphan_modules.json').write_text(json.dumps({'candidates':orphans},ensure_ascii=False,indent=2),encoding='utf-8')
print(len(orphans))