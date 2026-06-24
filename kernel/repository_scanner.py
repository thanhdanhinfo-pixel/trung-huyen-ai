from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RepositoryScanResult:
    """A repository tree scan result used by DiscoveryEngine."""

    status: str
    scanned_at: str = field(default_factory=utc_now)
    paths: List[str] = field(default_factory=list)
    ignored_paths: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "scanned_at": self.scanned_at,
            "path_count": len(self.paths),
            "ignored_count": len(self.ignored_paths),
            "paths": self.paths,
            "ignored_paths": self.ignored_paths,
            "metadata": self.metadata,
        }


@dataclass
class RepositoryScanner:
    ignored_prefixes: List[str] = field(default_factory=lambda: [
        ".git/",
        "__pycache__/",
        ".pytest_cache/",
        ".mypy_cache/",
        "node_modules/",
        "venv/",
        ".venv/",
    ])
    ignored_suffixes: List[str] = field(default_factory=lambda: [
        ".pyc",
        ".pyo",
        ".DS_Store",
        ".gitkeep",
    ])
    last_scan: RepositoryScanResult | None = None

    def scan_paths(self, paths: Iterable[str]) -> RepositoryScanResult:
        normalized: List[str] = []
        ignored: List[str] = []

        for path in sorted(set(paths)):
            clean = self._normalize_path(path)
            if not clean:
                continue
            if self._should_ignore(clean):
                ignored.append(clean)
                continue
            normalized.append(clean)

        result = RepositoryScanResult(
            status="ok",
            paths=normalized,
            ignored_paths=ignored,
            metadata={
                "source": "repository_paths",
                "scanner": "kernel.repository_scanner.RepositoryScanner",
            },
        )
        self.last_scan = result
        return result

    def scan_github_file_items(self, files: Iterable[Dict[str, Any]]) -> RepositoryScanResult:
        paths = []
        for item in files:
            path = item.get("path") or item.get("name") or ""
            item_type = item.get("type", "file")
            if path and item_type == "file":
                paths.append(path)
        return self.scan_paths(paths)

    def _normalize_path(self, path: str) -> str:
        return str(path or "").strip().replace("\\", "/").lstrip("/")

    def _should_ignore(self, path: str) -> bool:
        if any(path.startswith(prefix) for prefix in self.ignored_prefixes):
            return True
        if any(path.endswith(suffix) for suffix in self.ignored_suffixes):
            return True
        return False


def load_repository_scanner() -> RepositoryScanner:
    return RepositoryScanner()


repository_scanner = load_repository_scanner()
