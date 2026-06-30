from pathlib import Path
ROOT=Path(__file__).resolve().parents[1] 
MAX_DEPTH=2
lines=[]
for p in sorted(ROOT.iterdir()):
    lines.append(p.name+('/' if p.is_dir() else ''))
    if p.is_dir():
        try:
            for c in sorted(p.iterdir()):
                lines.append(f'  └── {c.name}'+('/' if c.is_dir() else ''))
        except Exception:
            pass
out=ROOT/'artifacts'; out.mkdir(exist_ok=True)
(out/'REPO_TREE.txt').write_text('\n'.join(lines),encoding='utf-8')
print('tree generated')
