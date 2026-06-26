import os

def run_smoke_tests():
    checks={
        'openai': bool(os.getenv('OPENAI_API_KEY')),
        'qdrant': bool(os.getenv('QDRANT_API_KEY')) and bool(os.getenv('QDRANT_URL')),
        'drive': bool(os.getenv('DRIVE_FOLDER_ID')),
        'github': bool(os.getenv('GITHUB_TOKEN')),
        'secrets': True,
    }
    return {'status':'ok' if all(checks.values()) else 'degraded','checks':checks}
