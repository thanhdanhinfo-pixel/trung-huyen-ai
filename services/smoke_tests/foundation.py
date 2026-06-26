import os
from typing import Any, Dict

import requests

SERVER_URL = os.getenv('SERVER_URL', 'https://trung-huyen-ai-779121307308.asia-southeast1.run.app').rstrip('/')

CORE_ENDPOINTS = [
    '/health',
    '/version',
    '/system-status',
    '/observability/status',
    '/command-runner/status',
]


def run_smoke_tests() -> Dict[str, Any]:
    results = []
    ok = True

    for path in CORE_ENDPOINTS:
        url = f'{SERVER_URL}{path}'
        try:
            response = requests.get(url, timeout=15)
            passed = 200 <= response.status_code < 500
            ok = ok and passed
            results.append({
                'path': path,
                'status_code': response.status_code,
                'passed': passed,
            })
        except Exception as exc:
            ok = False
            results.append({
                'path': path,
                'passed': False,
                'error_type': type(exc).__name__,
                'message': str(exc),
            })

    return {
        'status': 'ok' if ok else 'partial_error',
        'server_url': SERVER_URL,
        'results': results,
    }
