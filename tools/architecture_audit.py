import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1] 
root_py=len(list(ROOT.glob('*.py')))
dirs=[p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith('.')]
audit={'root_python_files':root_py,'top_level_directories':sorted(dirs),'status':'NEEDS_ROOT_REDUCTION' if root_py>20 else 'GOOD'}
out=ROOT/'artifacts'; out.mkdir(exist_ok=True)
(out/'architecture_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
