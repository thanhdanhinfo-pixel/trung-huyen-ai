from fastapi import APIRouter, Query
import os

router = APIRouter(prefix='/observability', tags=['observability-tools'])

@router.get('/status')
def status():
    return {
        'status': 'online',
        'cloud': '/observability/cloud',
        'cloud_logs': '/observability/cloud/logs',
        'cloud_builds': '/observability/cloud/builds',
        'cloud_runtime': '/observability/cloud/runtime',
        'cloud_revisions': '/observability/cloud/revisions',
        'errors': '/observability/errors',
        'github': '/observability/github',
        'github_latest_commit': '/observability/github/latest-commit',
        'smoke_tests': '/observability/smoke-test',
    }

@router.get('/cloud')
def cloud():
    from services.observability_tools.cloud import cloud_status
    return cloud_status()

@router.get('/cloud/logs')
def cloud_logs(limit:int=Query(default=20,ge=1,le=100)):
    from services.observability_tools.cloud import get_recent_logs
    return get_recent_logs(limit=limit)

@router.get('/cloud/builds')
def cloud_builds(limit:int=Query(default=10,ge=1,le=50)):
    from services.observability_tools.cloud import get_recent_builds
    return get_recent_builds(limit=limit)

@router.get('/cloud/runtime')
def cloud_runtime():
    from services.observability_tools.cloud import get_runtime_summary
    return get_runtime_summary()

@router.get('/cloud/revisions')
def cloud_revisions():
    return {
        'status':'ok',
        'current_revision': os.getenv('K_REVISION'),
        'configuration': os.getenv('K_CONFIGURATION'),
        'service':'trung-huyen-ai',
        'rollback_ready': True
    }

@router.get('/errors')
def errors():
    return {
        'status':'enabled',
        'source':'cloud-logging',
        'logs':'/observability/cloud/logs?limit=100',
        'error_reporting':'planned-v3.1'
    }

@router.get('/github')
def github():
    try:
        from services.observability_tools.github_checks import github_checks_status
        return github_checks_status()
    except Exception as exc:
        return {'status':'safe-mode','error':str(exc)}

@router.get('/github/latest-commit')
def github_latest_commit():
    try:
        from services.observability_tools.github_checks import github_latest_commit
        return github_latest_commit()
    except Exception as exc:
        return {'status':'safe-mode','error':str(exc)}

@router.post('/smoke-test')
def smoke_test():
    from services.smoke_tests.foundation import run_smoke_tests
    return run_smoke_tests()
