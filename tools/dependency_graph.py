import ast,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1] 
IGNORE={'.git','__pycache__','.venv','venv','node_modules'}
result={}
for p in ROOT.rglob('*.py'):
    if any(x in p.parts for x in IGNORE):
        continue
    try:
        tree=ast.parse(p.read_text(encoding='utf-8'))
        imports=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):
                imports.extend(a.name for a in n.names)
            elif isinstance(n,ast.ImportFrom) and n.module:
                imports.append(n.module)
        result[str(p.relative_to(ROOT))]=sorted(set(imports))
    except Exception:
        result[str(p.relative_to(ROOT))]=['__PARSE_ERROR__']
out=ROOT/'artifacts'; out.mkdir(exist_ok=True)
(out/'dependency_graph.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('dependency graph generated')
