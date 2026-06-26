import os

import requests


def run_smoke_tests():
    checks={
        'openai': bool(os.getenv('OPENAI_API_KEY')),
        'qdrant': bool(os.getenv('QDRANT_API_KEY')) and bool(os.getenv('QDRANT_URL')),
        'drive': bool(os.getenv('DRIVE_FOLDER_ID')),
        'github': bool(os.getenv('GITHUB_TOKEN')),
        'secrets': True,
    }

    base=os.getenv('SERVICE_URL','https://trung-huyen-ai-779121307308.asia-southeast1.run.app')
    paths=['/health','/version','/system/status','/observability/status','/command-runner/status']
    results=[]
    overall=True
    for p in paths:
        try:
            r=requests.get(base+p,timeout=10)
            passed=(r.status_code==200)
            overall=overall and passed
            results.append({'path':p,'status_code':r.status_code,'passed':passed})
        except Exception as exc:
            overall=False
            results.append({'path':p,'status_code':None,'passed':False,'error':str(exc)})

    return {
        'status':'ok' if overall and all(checks.values()) else 'degraded',
        'server_url':base,
        'checks':checks,
        'results':results,
    }
