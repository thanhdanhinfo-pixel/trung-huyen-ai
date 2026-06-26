from __future__ import annotations

import sys
from pathlib import Path

from system.tools.refactor.copy_module import copy_module
from system.tools.refactor.create_shim import create_shim


def module_name_from_path(path: Path) -> str:
    return '.'.join(path.with_suffix('').parts)


def migrate_module(source: str, target_dir: str) -> dict:
    src = Path(source)
    dst = Path(target_dir) / src.name

    copy_info = copy_module(str(src), str(dst))
    target_module = module_name_from_path(dst)
    shim_info = create_shim(str(src), target_module)

    return {
        'status': 'ok',
        'copied': copy_info,
        'shim': shim_info,
        'target_module': target_module,
    }


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: python migrate_module.py <source> <target_dir>')
    print(migrate_module(sys.argv[1], sys.argv[2]))
