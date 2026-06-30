from pathlib import Path 
import json
ROOT=Path(__file__).resolve().parents[1]
manifest={}
for p in ROOT.iterdir():
    if p.name.startswith('.'): continue
    if p.is_dir():
        manifest[p.name]=sorted([x.name for x in p.iterdir()][:200])
    else:
        manifest[p.name]='FILE'
out=ROOT/'artifacts'; out.mkdir(exist_ok=True)
(out/'repo_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('manifest exported')
