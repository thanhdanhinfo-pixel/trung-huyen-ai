from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from .repository_scanner import RepositoryScanResult, repository_scanner


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RepositoryAdapterStatus:
    """Runtime status for a repository adapter."""

    provider: str = "github"
    status: str = "unknown"
    checked_at: str = field(default_factory=utc_now)
    last_error: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "status": self.status,
            "checked_at": self.checked_at,
            "last_error": self.last_error,
            "metadata": self.metadata,
        }


@dataclass
class RepositoryAdapter:
    """Repository observation adapter for AI Kernel.

    The Kernel should not depend directly on GitHub Runtime. This adapter
    translates provider-specific file listings into provider-neutral scan
    results for RepositoryScanner and DiscoveryEngine.
    """

    provider: str = "github"
    scanner: Any = field(default_factory=lambda: repository_scanner)
    status_record: RepositoryAdapterStatus = field(default_factory=RepositoryAdapterStatus)

    def scan_files(self, files: List[Dict[str, Any]]) -> RepositoryScanResult:
        """Scan repository file items returned by a provider API."""
        self.status_record = RepositoryAdapterStatus(
            provider=self.provider,
            status="ok",
            metadata={"input_file_count": len(files)},
        )
        return self.scanner.scan_github_file_items(files)

    def scan_paths(self, paths: List[str]) -> RepositoryScanResult:
        """Scan raw repository paths from any provider."""
        self.status_record = RepositoryAdapterStatus(
            provider=self.provider,
            status="ok",
            metadata={"input_path_count": len(paths)},
        )
        return self.scanner.scan_paths(paths)

    def mark_error(self, error: Exception | str) -> Dict[str, Any]:
        self.status_record = RepositoryAdapterStatus(
            provider=self.provider,
            status="error",
            last_error=str(error),
        )
        return self.status_record.to_dict()

    def status(self) -> Dict[str, Any]:
        return self.status_record.to_dict()


def load_repository_adapter() -> RepositoryAdapter:
    return RepositoryAdapter()


repository_adapter = load_repository_adapter()
