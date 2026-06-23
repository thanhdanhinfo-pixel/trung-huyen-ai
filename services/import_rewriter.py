from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from services.github_runtime import github_runtime


@dataclass
class ImportRewriteResult:
    path: str
    changed: bool = False
    replacements: List[Dict[str, str]] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ImportRewriter:
    """Rewrite imports after safe repository moves.

    This service previews and applies text-safe import rewrites. It does not
    move files by itself; SafeMoveEngine owns move orchestration.
    """

    def preview(self, files: List[str], module_moves: Dict[str, str]) -> Dict[str, Any]:
        results = [self._rewrite_file(path, module_moves, commit=False) for path in files]
        return {
            "status": "ok",
            "file_count": len(files),
            "changed_count": sum(1 for result in results if result.changed),
            "results": [result.to_dict() for result in results],
        }

    def apply(self, files: List[str], module_moves: Dict[str, str], message: str = "Rewrite imports after repository move") -> Dict[str, Any]:
        results = []
        failed = 0
        for path in files:
            result = self._rewrite_file(path, module_moves, commit=True, message=message)
            if result.error:
                failed += 1
            results.append(result)
        return {
            "status": "done" if failed == 0 else "partial_failure",
            "file_count": len(files),
            "failed": failed,
            "changed_count": sum(1 for result in results if result.changed),
            "results": [result.to_dict() for result in results],
        }

    def _rewrite_file(
        self,
        path: str,
        module_moves: Dict[str, str],
        commit: bool = False,
        message: str = "Rewrite imports",
    ) -> ImportRewriteResult:
        result = ImportRewriteResult(path=path)
        try:
            current = github_runtime.read_file(path)
            old_content = current.get("content", "")
            ast.parse(old_content)
            new_content = old_content

            replacements = self._build_replacements(module_moves)
            for old, new in replacements.items():
                candidates = {
                    f"import {old}": f"import {new}",
                    f"from {old} import": f"from {new} import",
                }
                for find, replace in candidates.items():
                    if find in new_content:
                        new_content = new_content.replace(find, replace)
                        result.replacements.append({"find": find, "replace": replace})

            result.changed = new_content != old_content
            if result.changed:
                ast.parse(new_content)
                if commit:
                    github_runtime.update_file(
                        path=path,
                        content=new_content,
                        message=f"{message}: {path}",
                        sha=current.get("sha"),
                    )
        except Exception as exc:  # noqa: BLE001
            result.error = f"{type(exc).__name__}: {exc}"
        return result

    def _build_replacements(self, module_moves: Dict[str, str]) -> Dict[str, str]:
        replacements: Dict[str, str] = {}
        for source_path, destination_path in module_moves.items():
            old_module = self._path_to_module(source_path)
            new_module = self._path_to_module(destination_path)
            if old_module != new_module:
                replacements[old_module] = new_module
        return replacements

    def _path_to_module(self, path: str) -> str:
        return path.removesuffix(".py").replace("/", ".")


import_rewriter = ImportRewriter()
