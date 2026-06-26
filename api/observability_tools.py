from fastapi import APIRouter, Query

router = APIRouter(prefix='/observability', tags=['observability-tools'])


@router.get('/status')
def status():
    return {
        'status': 'online',
        'cloud': '/observability/cloud',
        'cloud_logs': '/observability/cloud/logs',
        'cloud_builds': '/observability/cloud/builds',
        'cloud_runtime': '/observability/cloud/runtime',
        'github': '/observability/github',
        'github_latest_commit': '/observability/github/latest-commit',
        'smoke_tests': '/observability/smoke-test',
    }


@router.get('/cloud')
def cloud():
    try:
        from services.observability_tools.cloud import cloud_status
        return cloud_status()
    except Exception as exc:
        return {'status': 'safe-mode', 'error': str(exc)}


@router.get('/cloud/logs')
def cloud_logs(limit: int = Query(default=20, ge=1, le=100)):
    try:
        from services.observability_tools.cloud import get_recent_logs
        return get_recent_logs(limit=limit)
    except Exception as exc:
        return {'status': 'safe-mode', 'error': str(exc)}


@router.get('/cloud/builds')
def cloud_builds(limit: int = Query(default=10, ge=1, le=50)):
    try:
        from services.observability_tools.cloud import get_recent_builds
        return get_recent_builds(limit=limit)
    except Exception as exc:
        return {'status': 'safe-mode', 'error': str(exc)}


@router.get('/cloud/runtime')
def cloud_runtime():
    try:
        from services.observability_tools.cloud import get_runtime_summary
        return get_runtime_summary()
    except Exception as exc:
        return {'status': 'safe-mode', 'error': str(exc)}


@router.get('/github')
def github():
    try:
        from services.observability_tools.github_checks import github_checks_status
        return github_checks_status()
    except Exception as exc:
        return {'status': 'safe-mode', 'error': str(exc)}


@router.get('/github/latest-commit')
def github_latest_commit():
    try:
        from services.observability_tools.github_checks import github_latest_commit
        return github_latest_commit()
    except Exception as exc:
        return {'status': 'safe-mode', 'error': str(exc)}


@router.post('/smoke-test')
def smoke_test():
    try:
        from services.smoke_tests.foundation import run_smoke_tests
        return run_smoke_tests()
    except Exception as exc:
        return {'status': 'safe-mode', 'error': str(exc)}
