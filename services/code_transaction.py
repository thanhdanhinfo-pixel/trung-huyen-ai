from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.code_transformer import code_transformer


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TransactionStepResult:
    index: int
    operation: str
    status: str
    result: Dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CodeTransactionRun:
    id: str
    status: str = "created"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    results: List[Dict[str, Any]] = field(default_factory=list)
    error: str | None = None

    def update(self, status: str) -> None:
        self.status = status
        self.updated_at = utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CodeTransactionEngine:
    """Run multiple code transformations as a guarded transaction.

    Phase 1 supports safe preview and sequential commit. Before committing,
    every step is previewed with syntax validation. If any preview is blocked,
    nothing is committed.
    """

    def __init__(self) -> None:
        self.runs: List[CodeTransactionRun] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "engine": "code_transaction",
            "run_count": len(self.runs),
            "latest": self.runs[-1].to_dict() if self.runs else None,
        }

    def preview(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        run = CodeTransactionRun(id=f"code-transaction-{len(self.runs) + 1:04d}", steps=steps)
        self.runs.append(run)
        run.update("previewing")
        results = self._run_steps(steps, commit=False)
        run.results = [item.to_dict() for item in results]
        blocked = any(item.status not in {"preview", "noop", "committed"} for item in results)
        run.update("blocked" if blocked else "preview")
        return {"status": run.status, "run": run.to_dict()}

    def execute(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        run = CodeTransactionRun(id=f"code-transaction-{len(self.runs) + 1:04d}", steps=steps)
        self.runs.append(run)
        run.update("previewing")

        preview_results = self._run_steps(steps, commit=False)
        run.results = [item.to_dict() for item in preview_results]
        blocked = any(item.status not in {"preview", "noop", "committed"} for item in preview_results)
        if blocked:
            run.update("blocked")
            return {"status": "blocked", "run": run.to_dict()}

        run.update("committing")
        commit_results = self._run_steps(steps, commit=True)
        run.results = [item.to_dict() for item in commit_results]
        failed = any(item.status not in {"committed", "noop"} for item in commit_results)
        run.update("partial_failure" if failed else "done")
        return {"status": run.status, "run": run.to_dict()}

    def history(self) -> List[Dict[str, Any]]:
        return [run.to_dict() for run in self.runs]

    def _run_steps(self, steps: List[Dict[str, Any]], commit: bool) -> List[TransactionStepResult]:
        results: List[TransactionStepResult] = []
        for index, step in enumerate(steps, start=1):
            operation = step.get("operation", "")
            path = step.get("path", "")
            params = step.get("params", {}) or {}
            try:
                result = self._dispatch(operation, path, params, commit=commit)
                results.append(
                    TransactionStepResult(
                        index=index,
                        operation=operation,
                        status=result.get("status", "unknown"),
                        result=result,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                results.append(
                    TransactionStepResult(
                        index=index,
                        operation=operation,
                        status="failed",
                        error=f"{type(exc).__name__}: {exc}",
                    )
                )
        return results

    def _dispatch(self, operation: str, path: str, params: Dict[str, Any], commit: bool) -> Dict[str, Any]:
        operations = {
            "insert_import": code_transformer.insert_import,
            "insert_after": code_transformer.insert_after,
            "replace_block": code_transformer.replace_block,
            "replace_function": code_transformer.replace_function,
            "register_router": code_transformer.register_router,
        }
        if operation not in operations:
            return {"status": "error", "message": f"Unsupported operation: {operation}"}
        return operations[operation](path=path, commit=commit, **params)


code_transaction_engine = CodeTransactionEngine()
