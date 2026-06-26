"""Execution Plan Engine for TRUNG_HUYEN_AI_OS.

This module is the Level-4 execution layer:
AI produces an intent/plan, while the engine translates it into safe GitHub
operations with validation and structured reporting.

Initial version supports:
- create
- update
- upsert/write
- delete
- patch via exact find/replace

Future versions can replace internals with AST transforms and Git Data API
without changing the plan contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from services.github_service import (
    github_batch_update,
    github_file_exists,
    github_copy_file,
    github_move_file,
)


@dataclass
class ExecutionStep:
    type: str
    path: str = ""
    content: str = ""
    find: str = ""
    replace: str = ""
    message: str = ""
    source: str = ""
    destination: str = ""
    overwrite: bool = False


@dataclass
class ExecutionPlan:
    name: str
    message: str
    steps: List[ExecutionStep] = field(default_factory=list)


class ExecutionEngine:
    """Translate high-level plans into GitHub operations."""

    def validate_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        errors: List[Dict[str, Any]] = []

        if not plan.name:
            errors.append({"field": "name", "message": "plan.name is required"})
        if not plan.message:
            errors.append({"field": "message", "message": "plan.message is required"})
        if not plan.steps:
            errors.append({"field": "steps", "message": "plan.steps must not be empty"})

        for index, step in enumerate(plan.steps):
            step_type = (step.type or "").lower()
            if not step_type:
                errors.append({"index": index, "field": "type", "message": "step.type is required"})
            if step_type not in {"create", "update", "upsert", "write", "delete", "patch"}:
                errors.append({"index": index, "field": "type", "message": f"unsupported step type: {step.type}"})
            if not step.path:
                errors.append({"index": index, "field": "path", "message": "step.path is required"})
            if step_type == "patch":
                if not step.find:
                    errors.append({"index": index, "field": "find", "message": "patch step requires find"})
                if step.replace is None:
                    errors.append({"index": index, "field": "replace", "message": "patch step requires replace"})

        return {
            "status": "ok" if not errors else "error",
            "errors": errors,
        }

    def _patch_to_operation(self, step: ExecutionStep, default_message: str) -> Dict[str, Any]:
        existing = github_file_exists(step.path)
        if not existing:
            raise ValueError(f"File not found for patch: {step.path}")

        current = existing["content"]
        if step.find not in current:
            raise ValueError(f"Patch find text not found in {step.path}")

        new_content = current.replace(step.find, step.replace, 1)
        return {
            "type": "update",
            "path": step.path,
            "content": new_content,
            "message": step.message or default_message,
        }

    def compile_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        validation = self.validate_plan(plan)
        if validation["status"] != "ok":
            return {
                "status": "error",
                "stage": "validate",
                "errors": validation["errors"],
            }

        operations: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []

        for index, step in enumerate(plan.steps):
            step_type = step.type.lower()
            try:
                if step_type == "patch":
                    operation = self._patch_to_operation(step, plan.message)
                else:
                    operation = {
                        "type": step_type,
                        "path": step.path,
                        "content": step.content,
                        "message": step.message or plan.message,
                    }
                operations.append(operation)
            except Exception as exc:
                errors.append({
                    "index": index,
                    "type": step.type,
                    "path": step.path,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                })

        return {
            "status": "ok" if not errors else "error",
            "stage": "compile",
            "operations": operations,
            "errors": errors,
        }

    def execute(self, plan: ExecutionPlan, approved: bool = False) -> Dict[str, Any]:
        if not approved:
            return {
                "status": "error",
                "stage": "approval",
                "message": "Execution denied. User approval is required.",
            }

        compiled = self.compile_plan(plan)
        if compiled["status"] != "ok":
            return compiled

        result = github_batch_update(
            message=plan.message,
            operations=compiled["operations"],
        )

        return {
            "status": result.get("status"),
            "stage": "execute",
            "plan": plan.name,
            "compiled_operations": len(compiled["operations"]),
            "result": result,
        }


def execution_plan_from_dict(data: Dict[str, Any]) -> ExecutionPlan:
    steps = [
        ExecutionStep(
            type=item.get("type", ""),
            path=item.get("path", ""),
            content=item.get("content", ""),
            find=item.get("find", ""),
            replace=item.get("replace", ""),
            message=item.get("message", ""),
        )
        for item in data.get("steps", [])
    ]

    return ExecutionPlan(
        name=data.get("name", ""),
        message=data.get("message", data.get("name", "Execution plan")),
        steps=steps,
    )


execution_engine = ExecutionEngine()
