import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1] 
root_py=sorted([p.name for p in ROOT.glob('*.py')])
keep={'app.py'}
candidates=[x for x in root_py if x not in keep]
out=ROOT/'artifacts';out.mkdir(exist_ok=True)
(out/'root_cleanup_candidates.json').write_text(json.dumps({'candidates':candidates},indent=2),encoding='utf-8')
print(len(candidates))
