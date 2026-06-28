import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules'}
SKIP_FILES = {'__init__.py', 'setup.py'}
ENTRYPOINT_NAMES = {'main.py', 'app.py', 'server.py'}
ENTRYPOINT_DIRS = {'api', 'scripts', 'tools', 'tests'}
RUNTIME_KEEP_DIRS = {'system', 'services'}


def should_skip(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if set(rel.parts) & SKIP_DIRS:
        return True
    return path.name in SKIP_FILES


def path_to_module(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix('')
    return '.'.join(rel.parts)


def collect_imports(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding='utf-8'))
    except Exception:
        return ['__PARSE_ERROR__']

    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return sorted(set(imports))


files = [p for p in sorted(ROOT.rglob('*.py')) if not should_skip(p)]
modules = {path_to_module(p): str(p.relative_to(ROOT)) for p in files}
outbound = {modules[path_to_module(p)]: collect_imports(p) for p in files}
inbound = {path: [] for path in modules.values()}

for src_path, imports in outbound.items():
    for imported in imports:
        for module, target_path in modules.items():
            if imported == module or imported.startswith(module + '.'):
                inbound[target_path].append(src_path)

entrypoints = []
possible_dead_code = []
needs_review = []
safe_to_keep = []

for path in sorted(inbound):
    parts = Path(path).parts
    name = Path(path).name
    has_inbound = bool(inbound[path])

    if name in ENTRYPOINT_NAMES or (parts and parts[0] in ENTRYPOINT_DIRS):
        entrypoints.append({'path': path, 'reason': 'entrypoint_or_tooling_area'})
    elif has_inbound:
        safe_to_keep.append({'path': path, 'reason': 'has_inbound_imports', 'inbound_count': len(inbound[path])})
    elif parts and parts[0] in RUNTIME_KEEP_DIRS:
        needs_review.append({'path': path, 'reason': 'runtime_area_no_static_inbound_imports'})
    else:
        possible_dead_code.append({'path': path, 'reason': 'no_static_inbound_imports'})

report = {
    'policy': 'no_delete_without_founder_review_and_regression_tests',
    'summary': {
        'files_scanned': len(files),
        'entrypoints': len(entrypoints),
        'safe_to_keep': len(safe_to_keep),
        'needs_review': len(needs_review),
        'possible_dead_code': len(possible_dead_code),
    },
    'entrypoints': entrypoints,
    'safe_to_keep': safe_to_keep,
    'needs_review': needs_review,
    'possible_dead_code': possible_dead_code,
    'inbound': inbound,
    'outbound': outbound,
}

out = ROOT / 'artifacts'
out.mkdir(exist_ok=True)
(out / 'orphan_modules.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

print(json.dumps(report['summary'], ensure_ascii=False, indent=2))
print('artifact=artifacts/orphan_modules.json')