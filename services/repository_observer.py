import os
from typing import Any, Dict, List

import requests

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_OWNER = os.getenv('GITHUB_OWNER', 'thanhdanhinfo-pixel')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'trung-huyen-ai')
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'main')

PROTECTED_FILES = [
    'app.py',
    'config.py',
    'drive.py',
    'mcp.py',
    'Dockerfile',
    'cloudbuild.yaml',
    'requirements.txt',
    'api/system_status.py',
    'api/observability_tools.py',
    'api/command_runner.py',
    'api/system_runtime.py',
    'system/self_healing.py',
    'services/github_service.py',
    'services/observability_tools/cloud.py',
    'services/smoke_tests/foundation.py',
]

CORE_FOLDERS = [
    'api',
    'services',
    'system',
    'rag',
    'bootstrap',
    'static',
    'tests',
    'worker',
]


def _headers() -> Dict[str, str]:
    headers = {'Accept': 'application/vnd.github+json'}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'Bearer {GITHUB_TOKEN}'
    return headers


def _repo_url(path: str = '') -> str:
    base = f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents'
    if path:
        return f'{base}/{path}?ref={GITHUB_BRANCH}'
    return f'{base}?ref={GITHUB_BRANCH}'


def list_path(path: str = '') -> Dict[str, Any]:
    try:
        resp = requests.get(_repo_url(path), headers=_headers(), timeout=20)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict):
            data = [data]
        return {
            'status': 'ok',
            'path': path or '/',
            'count': len(data),
            'items': [
                {
                    'name': item.get('name'),
                    'path': item.get('path'),
                    'type': item.get('type'),
                    'size': item.get('size'),
                    'sha': item.get('sha'),
                }
                for item in data
            ],
        }
    except Exception as exc:
        return {'status': 'safe-mode', 'path': path or '/', 'error_type': type(exc).__name__, 'message': str(exc)}


def repository_tree(depth: int = 1) -> Dict[str, Any]:
    depth = max(1, min(int(depth or 1), 3))
    root = list_path('')
    if root.get('status') != 'ok':
        return root

    tree: Dict[str, Any] = {'/': root.get('items', [])}
    if depth >= 2:
        for item in root.get('items', []):
            if item.get('type') == 'dir':
                subtree = list_path(item.get('path'))
                tree[item.get('path')] = subtree.get('items', []) if subtree.get('status') == 'ok' else []

    return {
        'status': 'ok',
        'repo': f'{GITHUB_OWNER}/{GITHUB_REPO}',
        'branch': GITHUB_BRANCH,
        'depth': depth,
        'tree': tree,
    }


def folder_health() -> Dict[str, Any]:
    root = list_path('')
    if root.get('status') != 'ok':
        return root

    items = root.get('items', [])
    dirs = [i for i in items if i.get('type') == 'dir']
    files = [i for i in items if i.get('type') == 'file']
    core_status: List[Dict[str, Any]] = []
    root_names = {i.get('name') for i in items}
    for folder in CORE_FOLDERS:
        core_status.append({'folder': folder, 'present': folder in root_names})

    duplicate_candidates = [
        'scheduler.py', 'health.py', 'admin.py', 'chat.py',
        'orchestrator.py', 'workflow_engine.py',
    ]
    existing_duplicates = [name for name in duplicate_candidates if name in root_names]

    return {
        'status': 'ok',
        'root_dirs': len(dirs),
        'root_files': len(files),
        'core_folders': core_status,
        'duplicate_candidates': existing_duplicates,
        'recommendation': 'review duplicate_candidates before refactor' if existing_duplicates else 'green',
    }


def protected_files() -> Dict[str, Any]:
    return {
        'status': 'ok',
        'policy': 'founder-approval-required',
        'protected_files': PROTECTED_FILES,
        'protected_folders': CORE_FOLDERS,
        'rules': [
            'no mass move without approval',
            'no startup blocking changes',
            'no secret logging',
            'one module per build cycle',
        ],
    }


PY_ROOT_DUPLICATE_CANDIDATES = [
    'scheduler.py', 'health.py', 'admin.py', 'chat.py',
    'orchestrator.py', 'workflow_engine.py', 'runtime_health.py',
]


def duplicate_modules() -> Dict[str, Any]:
    root = list_path('')
    api = list_path('api')
    services = list_path('services')
    system = list_path('system')

    groups = {}
    for scope_name, scope in [('root', root), ('api', api), ('services', services), ('system', system)]:
        for item in scope.get('items', []) if scope.get('status') == 'ok' else []:
            name = item.get('name') or ''
            if not name.endswith('.py'):
                continue
            stem = name[:-3]
            groups.setdefault(stem, []).append({'scope': scope_name, 'path': item.get('path'), 'size': item.get('size')})

    duplicates = {k: v for k, v in groups.items() if len(v) > 1}
    root_candidates = [name for name in PY_ROOT_DUPLICATE_CANDIDATES if any(i.get('name') == name for i in root.get('items', []))]

    return {
        'status': 'ok',
        'duplicate_groups': duplicates,
        'root_duplicate_candidates': root_candidates,
        'recommendation': 'manual-review-required' if duplicates or root_candidates else 'green',
    }


def dead_module_candidates() -> Dict[str, Any]:
    root = list_path('')
    if root.get('status') != 'ok':
        return root

    files = [i for i in root.get('items', []) if i.get('type') == 'file' and str(i.get('name', '')).endswith('.py')]
    candidates = []
    for item in files:
        size = item.get('size') or 0
        name = item.get('name') or ''
        if size <= 250 and name not in ['app.py', 'config.py', 'mcp.py']:
            candidates.append({'path': item.get('path'), 'size': size, 'reason': 'tiny-root-module'})

    return {
        'status': 'ok',
        'count': len(candidates),
        'candidates': candidates,
        'policy': 'do-not-delete-without-founder-approval',
    }


def import_dependency_map() -> Dict[str, Any]:
    # Lightweight static map for current architecture. Deep import parsing is planned for L3.
    return {
        'status': 'ok',
        'mode': 'lightweight',
        'nodes': CORE_FOLDERS + ['app.py', 'mcp.py', 'drive.py', 'config.py'],
        'edges': [
            ['app.py', 'api'],
            ['app.py', 'drive.py'],
            ['app.py', 'config.py'],
            ['app.py', 'services'],
            ['api', 'services'],
            ['services', 'github_runtime'],
            ['services', 'observability_tools'],
            ['rag', 'vectordb.py'],
            ['mcp.py', 'drive.py'],
        ],
        'next': 'recursive-python-import-scan',
    }


def architecture_summary() -> Dict[str, Any]:
    health = folder_health()
    duplicates = duplicate_modules()
    dead = dead_module_candidates()
    return {
        'status': 'ok',
        'level': 'repository-observability-l2',
        'folder_health': health,
        'duplicate_modules': duplicates,
        'dead_module_candidates': dead,
        'dependency_map_url': '/system/dependency-map',
        'protected_files_url': '/system/protected-files',
    }


PROTECTED_MODULES = {
    'app.py', 'config.py', 'drive.py', 'mcp.py', 'vectordb.py', 'runtime_health.py',
    'cloudbuild.yaml', 'requirements.txt', 'Dockerfile',
}

ACTIVE_ROOT_MODULES = {
    'agent_orchestrator.py', 'planner_agent.py', 'task_agent.py', 'task_queue.py',
    'workflow_engine.py', 'long_term_memory.py', 'document_cache.py', 'knowledge_graph.py',
}

KNOWN_SHIMS = {
    'chat.py': 'api/chat.py',
    'health.py': 'api/health.py',
    'scheduler.py': 'services/production_scheduler.py',
    'orchestrator.py': 'agent_orchestrator.py',
}


def module_classification() -> Dict[str, Any]:
    root = list_path('')
    if root.get('status') != 'ok':
        return root

    modules = []
    for item in root.get('items', []):
        name = item.get('name') or ''
        if not name.endswith('.py'):
            continue
        size = item.get('size') or 0
        path = item.get('path')
        if name in PROTECTED_MODULES:
            category = 'PROTECTED'
            action = 'do_not_move'
            reason = 'core runtime file'
        elif name in ACTIVE_ROOT_MODULES:
            category = 'ACTIVE'
            action = 'keep_until_dependency_scan'
            reason = 'known active root module'
        elif name in KNOWN_SHIMS:
            category = 'SHIM'
            action = 'verify_imports_then_replace_with_compatibility_shim'
            reason = f'candidate shim for {KNOWN_SHIMS[name]}'
        elif size <= 250:
            category = 'REVIEW'
            action = 'inspect_content_before_decision'
            reason = 'tiny root module'
        else:
            category = 'UNKNOWN_ACTIVE'
            action = 'dependency_scan_required'
            reason = 'non-trivial root module'
        modules.append({'path': path, 'size': size, 'category': category, 'recommended_action': action, 'reason': reason})

    summary = {}
    for m in modules:
        summary[m['category']] = summary.get(m['category'], 0) + 1

    return {
        'status': 'ok',
        'policy': 'classification_only_no_delete',
        'summary': summary,
        'modules': modules,
    }


# =============================
# Repository Observability L3
# AST import scan, orphan candidates, safe refactor plan
# =============================

import ast
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed

SCAN_FOLDERS = ['', 'api', 'services', 'system']
MAX_IMPORT_SCAN_WORKERS = int(os.getenv('IMPORT_SCAN_WORKERS', '16'))


def _read_text_file(path: str) -> Dict[str, Any]:
    try:
        resp = requests.get(_repo_url(path), headers=_headers(), timeout=20)
        resp.raise_for_status()
        data = resp.json()
        content = data.get('content', '')
        encoding = data.get('encoding')
        if encoding == 'base64':
            text = base64.b64decode(content).decode('utf-8', errors='replace')
        else:
            text = content or ''
        return {'status': 'ok', 'path': path, 'text': text, 'sha': data.get('sha'), 'size': data.get('size')}
    except Exception as exc:
        return {'status': 'error', 'path': path, 'error_type': type(exc).__name__, 'message': str(exc)}


def _repo_tree_recursive() -> Dict[str, Any]:
    try:
        url = f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/trees/{GITHUB_BRANCH}?recursive=1'
        resp = requests.get(url, headers=_headers(), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return {'status': 'ok', 'tree': data.get('tree', [])}
    except Exception as exc:
        return {'status': 'error', 'error_type': type(exc).__name__, 'message': str(exc), 'tree': []}


def _python_files_for_scan() -> List[Dict[str, Any]]:
    tree_result = _repo_tree_recursive()
    if tree_result.get('status') == 'ok':
        files: List[Dict[str, Any]] = []
        for item in tree_result.get('tree', []):
            path = item.get('path') or ''
            if item.get('type') == 'blob' and path.endswith('.py'):
                files.append({
                    'name': path.split('/')[-1],
                    'path': path,
                    'type': 'file',
                    'size': item.get('size', 0),
                    'sha': item.get('sha'),
                })
        return files

    # Fallback: legacy folder scan if Git tree API is unavailable.
    files: List[Dict[str, Any]] = []
    seen = set()
    for folder in SCAN_FOLDERS:
        listing = list_path(folder)
        if listing.get('status') != 'ok':
            continue
        for item in listing.get('items', []):
            path = item.get('path') or ''
            if item.get('type') == 'file' and path.endswith('.py') and path not in seen:
                files.append(item)
                seen.add(path)
    return files


def _module_name_from_path(path: str) -> str:
    name = path[:-3] if path.endswith('.py') else path
    return name.replace('/', '.')


def import_scan() -> Dict[str, Any]:
    files = _python_files_for_scan()
    modules = {_module_name_from_path(f.get('path', '')): f.get('path') for f in files}
    imported_names = set()
    results = []
    errors = []

    def parse_file(item: Dict[str, Any]) -> Dict[str, Any]:
        path = item.get('path')
        read = _read_text_file(path)
        if read.get('status') != 'ok':
            return {'status': 'error', 'error': read}

        text = read.get('text', '')
        imports = []
        imported = set()
        try:
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.name
                        imports.append(name)
                        imported.add(name)
                        imported.add(name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        imported.add(node.module)
                        imported.add(node.module.split('.')[0])
        except SyntaxError as exc:
            return {'status': 'error', 'error': {'path': path, 'error_type': 'SyntaxError', 'message': str(exc)}}
        except Exception as exc:
            return {'status': 'error', 'error': {'path': path, 'error_type': type(exc).__name__, 'message': str(exc)}}

        return {
            'status': 'ok',
            'imported_names': imported,
            'result': {
                'path': path,
                'module': _module_name_from_path(path),
                'import_count': len(imports),
                'imports': sorted(set(imports)),
            },
        }

    worker_count = max(1, min(MAX_IMPORT_SCAN_WORKERS, 32, len(files) or 1))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_map = {executor.submit(parse_file, item): item for item in files}
        for future in as_completed(future_map):
            parsed = future.result()
            if parsed.get('status') != 'ok':
                errors.append(parsed.get('error'))
                continue
            imported_names.update(parsed.get('imported_names', set()))
            results.append(parsed.get('result'))

    results.sort(key=lambda x: x.get('path', ''))

    referenced_internal = []
    for module, path in modules.items():
        short = module.split('.')[-1]
        if module in imported_names or short in imported_names:
            referenced_internal.append({'module': module, 'path': path})

    return {
        'status': 'ok',
        'mode': 'ast-static-scan',
        'scanned_files': len(files),
        'modules_detected': len(modules),
        'referenced_internal_count': len(referenced_internal),
        'referenced_internal': referenced_internal,
        'files': results,
        'errors': errors,
    }


def orphan_modules() -> Dict[str, Any]:
    scan = import_scan()
    if scan.get('status') != 'ok':
        return scan

    referenced_paths = {item.get('path') for item in scan.get('referenced_internal', [])}
    protected = set(PROTECTED_MODULES)
    active = set(ACTIVE_ROOT_MODULES)
    shims = set(KNOWN_SHIMS.keys())
    candidates = []

    for item in _python_files_for_scan():
        path = item.get('path')
        name = item.get('name')
        if path in referenced_paths:
            continue
        if name in protected:
            category = 'PROTECTED_UNREFERENCED'
            action = 'keep'
        elif name in active:
            category = 'ACTIVE_UNREFERENCED'
            action = 'manual_review_after_runtime_trace'
        elif name in shims:
            category = 'SHIM_UNREFERENCED'
            action = 'candidate_for_compatibility_shim_or_archive'
        elif item.get('size', 0) <= 250 and '/' not in path:
            category = 'REVIEW_ORPHAN_CANDIDATE'
            action = 'inspect_then_archive_candidate'
        else:
            category = 'UNKNOWN_UNREFERENCED'
            action = 'dependency_scan_required'
        candidates.append({'path': path, 'size': item.get('size'), 'category': category, 'recommended_action': action})

    return {
        'status': 'ok',
        'policy': 'analysis_only_no_delete',
        'count': len(candidates),
        'candidates': candidates,
    }


def refactor_plan() -> Dict[str, Any]:
    classification = module_classification()
    orphans = orphan_modules()
    shim_modules = [m for m in classification.get('modules', []) if m.get('category') == 'SHIM']
    review_orphans = [m for m in orphans.get('candidates', []) if m.get('category') in ['SHIM_UNREFERENCED', 'REVIEW_ORPHAN_CANDIDATE']]

    return {
        'status': 'ok',
        'mode': 'proposal-only',
        'policy': 'founder-approval-required-before-any-move-or-delete',
        'phase_1_safe_actions': [
            {'action': 'convert_to_compatibility_shim', 'targets': shim_modules},
            {'action': 'inspect_review_orphans', 'targets': review_orphans[:25]},
        ],
        'blocked_actions': [
            'delete_files',
            'mass_move_root_modules',
            'modify_protected_files_without_explicit_approval',
        ],
        'next_endpoint': '/system/refactor-plan',
    }


# =============================
# Repository Observability Performance Cache
# Keeps full scan accuracy while avoiding repeated GitHub reads.
# =============================

from datetime import datetime, timedelta

_IMPORT_SCAN_CACHE: Dict[str, Any] | None = None
_IMPORT_SCAN_AT: datetime | None = None
_IMPORT_SCAN_TTL = timedelta(minutes=5)
_import_scan_uncached = import_scan


def import_scan(force: bool = False) -> Dict[str, Any]:
    global _IMPORT_SCAN_CACHE, _IMPORT_SCAN_AT

    now = datetime.utcnow()
    if (
        not force
        and _IMPORT_SCAN_CACHE is not None
        and _IMPORT_SCAN_AT is not None
        and now - _IMPORT_SCAN_AT < _IMPORT_SCAN_TTL
    ):
        cached = dict(_IMPORT_SCAN_CACHE)
        cached['cache'] = {
            'hit': True,
            'cached_at': _IMPORT_SCAN_AT.isoformat() + 'Z',
            'ttl_seconds': int(_IMPORT_SCAN_TTL.total_seconds()),
        }
        return cached

    result = _import_scan_uncached()
    _IMPORT_SCAN_CACHE = result
    _IMPORT_SCAN_AT = now

    enriched = dict(result)
    enriched['cache'] = {
        'hit': False,
        'cached_at': _IMPORT_SCAN_AT.isoformat() + 'Z',
        'ttl_seconds': int(_IMPORT_SCAN_TTL.total_seconds()),
    }
    _IMPORT_SCAN_CACHE = enriched
    return enriched


def clear_import_scan_cache() -> Dict[str, Any]:
    global _IMPORT_SCAN_CACHE, _IMPORT_SCAN_AT
    _IMPORT_SCAN_CACHE = None
    _IMPORT_SCAN_AT = None
    return {'status': 'ok', 'cache': 'cleared'}
