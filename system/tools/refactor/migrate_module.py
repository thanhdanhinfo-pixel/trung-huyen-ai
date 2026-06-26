from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from system.tools.refactor.copy_module import copy_module
from system.tools.refactor.create_shim import create_shim
from system.tools.refactor.verify_imports import verify_imports


def module_name_from_path(path: Path) -> str:
    return '.'.join(path.with_suffix('').parts)


def original_module_from_source(source: Path) -> str:
    return '.'.join(source.with_suffix('').parts)


def migrate_module(source: str, target_dir: str, *, dry_run: bool = False, report_path: str | None = None) -> dict[str, Any]:
    src = Path(source)
    dst = Path(target_dir) / src.name
    target_module = module_name_from_path(dst)
    original_module = original_module_from_source(src)

    report: dict[str, Any] = {
        'status': 'planned' if dry_run else 'running',
        'source': str(src),
        'destination': str(dst),
        'original_module': original_module,
        'target_module': target_module,
        'dry_run': dry_run,
        'steps': [],
    }

    if dry_run:
        report['steps'].append({'step': 'copy', 'status': 'planned'})
        report['steps'].append({'step': 'create_shim', 'status': 'planned'})
        report['steps'].append({'step': 'verify_imports', 'status': 'planned'})
        report['status'] = 'ok'
        _write_report(report, report_path)
        return report

    original_bytes = src.read_bytes() if src.exists() else None
    dst_existed = dst.exists()
    dst_original_bytes = dst.read_bytes() if dst_existed else None

    try:
        copy_info = copy_module(str(src), str(dst))
        report['steps'].append({'step': 'copy', 'status': 'ok', 'result': copy_info})

        shim_info = create_shim(str(src), target_module)
        report['steps'].append({'step': 'create_shim', 'status': 'ok', 'result': shim_info})

        verify_report = verify_imports(original_module, target_module)
        report['steps'].append({'step': 'verify_imports', 'status': verify_report['status'], 'result': verify_report})
        if verify_report['status'] != 'ok':
            raise RuntimeError('Import verification failed')

        report['status'] = 'ok'
        _write_report(report, report_path)
        return report

    except Exception as exc:
        report['status'] = 'error'
        report['error_type'] = type(exc).__name__
        report['message'] = str(exc)
        report['steps'].append({'step': 'rollback', 'status': 'running'})

        if original_bytes is not None:
            src.write_bytes(original_bytes)
        if dst_existed and dst_original_bytes is not None:
            dst.write_bytes(dst_original_bytes)
        elif dst.exists():
            dst.unlink()

        report['steps'][-1] = {'step': 'rollback', 'status': 'ok'}
        _write_report(report, report_path)
        raise


def _write_report(report: dict[str, Any], report_path: str | None) -> None:
    if not report_path:
        return
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Safely migrate a root module into a domain package.')
    parser.add_argument('source')
    parser.add_argument('target_dir')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--report', default=None)
    args = parser.parse_args()

    result = migrate_module(args.source, args.target_dir, dry_run=args.dry_run, report_path=args.report)
    print(json.dumps(result, ensure_ascii=False, indent=2))
