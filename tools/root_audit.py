import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
root_py=[p.name for p in ROOT.glob('*.py')]
audit={'root_python_files':sorted(root_py),'count':len(root_py)}
out=ROOT/'artifacts'; out.mkdir(exist_ok=True)
(out/'root_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(audit['count'])