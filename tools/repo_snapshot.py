from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
IGNORE={'.git','__pycache__','.venv','venv','node_modules'}

def walk(root):
    files=[]
    for p in root.rglob('*'):
        if any(x in p.parts for x in IGNORE):
            continue
        if p.is_file():
            files.append({'path':str(p.relative_to(root)),'ext':p.suffix,'size':p.stat().st_size})
    return files

if __name__=='__main__':
    data=walk(ROOT)
    root_files=[f['path'] for f in data if '/' not in f['path']]
    out={'total_files':len(data),'root_files':root_files,'python_root_files':[x for x in root_files if x.endswith('.py')],'files':data}
    out_dir=ROOT/'artifacts'
    out_dir.mkdir(exist_ok=True)
    (out_dir/'repo_snapshot.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"snapshot: {len(data)} files")
