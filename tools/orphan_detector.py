import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules'}
SKIP_FILES = {'__init__.py', 'setup.py'}

candidates = []

for path in sorted(ROOT.rglob('*.py')):
    rel = path.relative_to(ROOT)
    parts = set(rel.parts)

    if parts & SKIP_DIRS:
        continue
    if path.name in SKIP_FILES:
        continue

    reason = None
    if '_' in path.stem:
        reason = 'root_or_module_name_contains_underscore'

    if reason:
        candidates.append({
            'path': str(rel),
            'name': path.name,
            'reason': reason,
        })

out = ROOT / 'artifacts'
out.mkdir(exist_ok=True)

report = {
    'count': len(candidates),
    'policy': 'candidate_only_no_delete_without_dependency_review',
    'candidates': candidates,
}

(out / 'orphan_modules.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding='utf-8',
)

for item in candidates:
    print(f"{item['path']} | {item['reason']}")

print(f"TOTAL={len(candidates)}")