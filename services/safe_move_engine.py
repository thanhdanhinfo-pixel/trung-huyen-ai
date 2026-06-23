from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from services.github_runtime import github_runtime
from services.import_rewriter import import_rewriter


@dataclass
class SafeMoveResult:
    source: str
    destination: str
    status: str = "created"
    move_result: Dict[str, Any] = field(default_factory=dict)
    import_rewrite_result: Dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SafeMoveEngine:
    """Move files safely and rewrite imports.

    This engine intentionally works in small batches. It is the safe bridge
    between DependencyAnalyzer move plans and GitHubRuntime write operations.
    """

    def preview(self, operations: List[Dict[str, str]]) -> Dict[str, Any]:
        module_moves = {
            op["source"]: op["destination"]
            for op in operations
            if op.get("source") and op.get("destination")
        }
        return {
            "status": "preview",
            "operation_count": len(operations),
            "module_moves": module_moves,
            "operations": operations,
        }

    def execute(
        self,
        operations: List[Dict[str, str]],
        import_files: List[str] | None = None,
        message: str = "Safe repository move",
    ) -> Dict[str, Any]:
        import_files = import_files or []
        module_moves = {
            op["source"]: op["destination"]
            for op in operations
            if op.get("source") and op.get("destination")
        }

        results: List[SafeMoveResult] = []
        failed = 0

        for op in operations:
            source = op.get("source", "")
            destination = op.get("destination", "")
            item = SafeMoveResult(source=source, destination=destination, status="running")
            try:
                item.move_result = github_runtime.move_file(
                    source=source,
                    destination=destination,
                    message=op.get("message", message),
                )
                item.status = "moved" if item.move_result.get("verified") else "failed"
                if item.status == "failed":
                    failed += 1
            except Exception as exc:  # noqa: BLE001
                item.status = "failed"
                item.error = f"{type(exc).__name__}: {exc}"
                failed += 1
            results.append(item)

        rewrite_result = {"status": "skipped", "reason": "no import_files provided"}
        if import_files and failed == 0:
            rewrite_result = import_rewriter.apply(
                files=import_files,
                module_moves=module_moves,
                message="Rewrite imports after safe move",
            )

        return {
            "status": "done" if failed == 0 else "partial_failure",
            "operation_count": len(operations),
            "failed": failed,
            "moves": [item.to_dict() for item in results],
            "import_rewrite": rewrite_result,
        }


safe_move_engine = SafeMoveEngine()
