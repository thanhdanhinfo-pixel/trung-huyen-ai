import os
from typing import Any, Dict, List

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('GCP_PROJECT') or 'trung-huyen-ai'
REGION = os.getenv('GOOGLE_CLOUD_REGION') or os.getenv('CLOUD_RUN_REGION') or 'asia-southeast1'
SERVICE_NAME = os.getenv('CLOUD_RUN_SERVICE') or 'trung-huyen-ai'


def cloud_status() -> Dict[str, Any]:
    return {
        'status': 'online',
        'project_id': PROJECT_ID,
        'region': REGION,
        'service_name': SERVICE_NAME,
        'cloud_run_logs': '/observability/cloud/logs',
        'cloud_build_status': '/observability/cloud/builds',
        'runtime': '/observability/cloud/runtime',
        'mode': 'production-safe',
    }


def get_recent_logs(limit: int = 20) -> Dict[str, Any]:
    limit = max(1, min(int(limit or 20), 100))
    try:
        from google.cloud import logging_v2

        client = logging_v2.Client(project=PROJECT_ID)
        log_filter = (
            'resource.type="cloud_run_revision" '
            f'AND resource.labels.service_name="{SERVICE_NAME}" '
            f'AND resource.labels.location="{REGION}"'
        )
        entries = client.list_entries(
            filter_=log_filter,
            page_size=limit,
            order_by=logging_v2.DESCENDING,
        )

        logs: List[Dict[str, Any]] = []
        for entry in entries:
            logs.append({
                'timestamp': str(getattr(entry, 'timestamp', '')),
                'severity': getattr(entry, 'severity', None),
                'log_name': getattr(entry, 'log_name', None),
                'payload': str(getattr(entry, 'payload', ''))[:1200],
                'resource': dict(getattr(entry, 'resource', {}) or {}),
            })
            if len(logs) >= limit:
                break

        return {
            'status': 'ok',
            'project_id': PROJECT_ID,
            'service_name': SERVICE_NAME,
            'region': REGION,
            'count': len(logs),
            'logs': logs,
        }
    except Exception as exc:
        return {
            'status': 'safe-mode',
            'error_type': type(exc).__name__,
            'message': str(exc),
        }


def get_recent_builds(limit: int = 10) -> Dict[str, Any]:
    limit = max(1, min(int(limit or 10), 50))
    try:
        from googleapiclient.discovery import build

        service = build('cloudbuild', 'v1', cache_discovery=False)
        request = service.projects().builds().list(
            projectId=PROJECT_ID,
            pageSize=limit,
        )
        response = request.execute()
        builds = response.get('builds', [])[:limit]

        return {
            'status': 'ok',
            'project_id': PROJECT_ID,
            'count': len(builds),
            'builds': [
                {
                    'id': b.get('id'),
                    'status': b.get('status'),
                    'createTime': b.get('createTime'),
                    'finishTime': b.get('finishTime'),
                    'logUrl': b.get('logUrl'),
                    'substitutions': b.get('substitutions', {}),
                }
                for b in builds
            ],
        }
    except Exception as exc:
        return {
            'status': 'safe-mode',
            'error_type': type(exc).__name__,
            'message': str(exc),
        }


def get_runtime_summary() -> Dict[str, Any]:
    return {
        'status': 'ok',
        'project_id': PROJECT_ID,
        'region': REGION,
        'service_name': SERVICE_NAME,
        'runtime_service_account': os.getenv('K_SERVICE', SERVICE_NAME),
        'revision': os.getenv('K_REVISION'),
        'configuration': os.getenv('K_CONFIGURATION'),
        'secret_backed': {
            'openai_api_key': bool(os.getenv('OPENAI_API_KEY')),
            'qdrant_api_key': bool(os.getenv('QDRANT_API_KEY')),
            'google_service_account_json': bool(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')),
            'drive_folder_id': bool(os.getenv('DRIVE_FOLDER_ID')),
        },
    }
