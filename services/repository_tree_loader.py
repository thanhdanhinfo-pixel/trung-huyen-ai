from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from services.github_runtime import github_runtime


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RepositoryTreeLoadResult:
    status: str
    requested_paths: List[str] = field(default_factory=list)
    files: List[Dict[str, Any]] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    loaded_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "loaded_at": self.loaded_at,
            "requested_paths": self.requested_paths,
            "file_count": len(self.files),
            "directory_count": len(self.directories),
            "error_count": len(self.errors),
            "files": self.files,
            "directories": self.directories,
            "errors": self.errors,
        }


@dataclass
class RepositoryTreeLoader:
    """Expand repository paths into recursive GitHub file items.

    System Awareness should receive real repository files, not only top-level
    folder names. This loader stays in the service layer because it depends on
    GitHub Runtime, while Kernel remains provider-neutral.
    """

    max_depth: int = 8
    max_files: int = 500
    ignored_names: set[str] = field(default_factory=lambda: {
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        ".venv",
        "venv",
        "node_modules",
    })

    def load(self, paths: Iterable[str]) -> RepositoryTreeLoadResult:
        requested = [self._clean_path(path) for path in paths if self._clean_path(path)]
        files: List[Dict[str, Any]] = []
        directories: List[str] = []
        errors: List[Dict[str, Any]] = []
        seen_files: set[str] = set()
        seen_dirs: set[str] = set()

        for path in requested:
            self._walk(
                path=path,
                depth=0,
                files=files,
                directories=directories,
                errors=errors,
                seen_files=seen_files,
                seen_dirs=seen_dirs,
            )
            if len(files) >= self.max_files:
                break

        return RepositoryTreeLoadResult(
            status="ok" if not errors else "partial",
            requested_paths=requested,
            files=files,
            directories=directories,
            errors=errors,
        )

    def _walk(
        self,
        path: str,
        depth: int,
        files: List[Dict[str, Any]],
        directories: List[str],
        errors: List[Dict[str, Any]],
        seen_files: set[str],
        seen_dirs: set[str],
    ) -> None:
        if depth > self.max_depth or len(files) >= self.max_files:
            return

        clean = self._clean_path(path)
        if not clean or self._should_ignore(clean):
            return

        try:
            items = github_runtime.list_files(clean)
        except Exception as exc:
            errors.append({"path": clean, "message": str(exc), "type": type(exc).__name__})
            return

        if isinstance(items, dict):
            items = items.get("files", [])

        for item in items or []:
            item_path = self._clean_path(item.get("path") or item.get("name") or "")
            item_type = item.get("type", "file")

            if not item_path or self._should_ignore(item_path):
                continue

            if item_type == "dir":
                if item_path not in seen_dirs:
                    seen_dirs.add(item_path)
                    directories.append(item_path)
                self._walk(
                    path=item_path,
                    depth=depth + 1,
                    files=files,
                    directories=directories,
                    errors=errors,
                    seen_files=seen_files,
                    seen_dirs=seen_dirs,
                )
            elif item_type == "file":
                if item_path not in seen_files:
                    seen_files.add(item_path)
                    files.append(item)
                    if len(files) >= self.max_files:
                        return

    def _clean_path(self, path: str) -> str:
        return str(path or "").strip().replace("\\", "/").strip("/")

    def _should_ignore(self, path: str) -> bool:
        parts = [part for part in path.split("/") if part]
        return any(part in self.ignored_names for part in parts)


repository_tree_loader = RepositoryTreeLoader()
