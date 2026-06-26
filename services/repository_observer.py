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
