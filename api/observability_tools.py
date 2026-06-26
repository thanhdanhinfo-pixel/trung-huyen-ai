from fastapi import APIRouter

router = APIRouter(prefix='/observability', tags=['observability-tools'])

@router.get('/status')
def status():
    return {
        'status': 'foundation',
        'cloud': '/observability/cloud',
        'github': '/observability/github',
        'smoke_tests': '/observability/smoke-test',
    }

@router.get('/cloud')
def cloud():
    try:
        from services.observability_tools.cloud import cloud_status
        return cloud_status()
    except Exception as exc:
        return {'status': 'safe-mode', 'error': str(exc)}

@router.get('/github')
def github():
    try:
        from services.observability_tools.github_checks import github_checks_status
        return github_checks_status()
    except Exception as exc:
        return {'status': 'safe-mode', 'error': str(exc)}

@router.post('/smoke-test')
def smoke_test():
    try:
        from services.smoke_tests.foundation import run_smoke_tests
        return run_smoke_tests()
    except Exception as exc:
        return {'status': 'safe-mode', 'error': str(exc)}
