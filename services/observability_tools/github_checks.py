import os
from typing import Any, Dict 

import requests

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_OWNER = os.getenv('GITHUB_OWNER', '')
GITHUB_REPO = os.getenv('GITHUB_REPO', '')
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'main')

BASE = f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}'


def _headers() -> Dict[str, str]:
    return {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json',
    }


def github_checks_status() -> Dict[str, Any]:
    if not (GITHUB_TOKEN and GITHUB_OWNER and GITHUB_REPO):
        return {'status': 'safe-mode', 'reason': 'missing_github_config'}

    try:
        branch = requests.get(
            f'{BASE}/branches/{GITHUB_BRANCH}',
            headers=_headers(),
            timeout=15,
        )
        branch.raise_for_status()
        sha = branch.json().get('commit', {}).get('sha')

        checks = requests.get(
            f'{BASE}/commits/{sha}/check-runs',
            headers=_headers(),
            timeout=15,
        )
        checks.raise_for_status()

        return {
            'status': 'ok',
            'branch': GITHUB_BRANCH,
            'commit': sha,
            'check_runs': checks.json().get('check_runs', []),
        }
    except Exception as exc:
        return {
            'status': 'safe-mode',
            'error_type': type(exc).__name__,
            'message': str(exc),
        }


def github_latest_commit() -> Dict[str, Any]:
    if not (GITHUB_TOKEN and GITHUB_OWNER and GITHUB_REPO):
        return {'status': 'safe-mode', 'reason': 'missing_github_config'}

    try:
        branch = requests.get(
            f'{BASE}/branches/{GITHUB_BRANCH}',
            headers=_headers(),
            timeout=15,
        )
        branch.raise_for_status()
        data = branch.json()
        return {
            'status': 'ok',
            'branch': GITHUB_BRANCH,
            'commit': data.get('commit', {}),
        }
    except Exception as exc:
        return {
            'status': 'safe-mode',
            'error_type': type(exc).__name__,
            'message': str(exc),
        }
