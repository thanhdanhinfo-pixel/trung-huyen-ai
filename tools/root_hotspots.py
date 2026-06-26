from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
items=[]
for p in ROOT.glob('*.py'):
    items.append({'file':p.name,'size':p.stat().st_size})
items=sorted(items,key=lambda x:x['size'],reverse=True)
out=ROOT/'artifacts'; out.mkdir(exist_ok=True)
(out/'root_hotspots.json').write_text(json.dumps(items,indent=2),encoding='utf-8')