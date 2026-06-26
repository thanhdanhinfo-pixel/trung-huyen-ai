def run_smoke_tests():
    checks = {
        'import_app': 'available_via_command_runner_dry_run',
        'health': 'manual_or_http_check',
        'version': 'manual_or_http_check',
        'drive': 'manual_or_runtime_health',
        'qdrant': 'manual_or_runtime_health',
    }
    return {'status': 'foundation', 'checks': checks}
