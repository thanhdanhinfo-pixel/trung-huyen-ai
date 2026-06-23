from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Set

from services.github_runtime import github_runtime


@dataclass
class PythonModuleReport:
    path: str
    module: str
    imports: List[str] = field(default_factory=list)
    from_imports: List[str] = field(default_factory=list)
    local_dependencies: List[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DependencyAnalyzer:
    """Repository dependency analyzer.

    This is the first safe step before moving hundreds of root-level modules.
    It builds a dependency map without mutating files.
    """

    def __init__(self) -> None:
        self.last_report: Dict[str, Any] = {}

    def analyze(self, root: str = "") -> Dict[str, Any]:
        files = self._collect_python_files(root)
        module_names = {self._path_to_module(path) for path in files}
        reports = [self._analyze_file(path, module_names) for path in files]

        root_level = [path for path in files if "/" not in path]
        orphan_candidates = [
            report.path
            for report in reports
            if "/" not in report.path and not report.local_dependencies and not report.error
        ]

        self.last_report = {
            "status": "ok",
            "python_file_count": len(files),
            "root_python_file_count": len(root_level),
            "root_python_files": root_level,
            "orphan_candidates": orphan_candidates,
            "modules": [report.to_dict() for report in reports],
        }
        return self.last_report

    def dependencies(self) -> Dict[str, Any]:
        return self.last_report or self.analyze()

    def move_plan(self) -> Dict[str, Any]:
        report = self.dependencies()
        root_files = report.get("root_python_files", [])
        plan = []
        for path in root_files:
            destination = self._suggest_destination(path)
            if destination != path:
                plan.append({"source": path, "destination": destination, "risk": "review"})
        return {"status": "ok", "operation_count": len(plan), "operations": plan}

    def _collect_python_files(self, root: str = "") -> List[str]:
        collected: List[str] = []
        self._walk(root, collected)
        return sorted(set(collected))

    def _walk(self, path: str, collected: List[str]) -> None:
        items = github_runtime.list_files(path)
        if not isinstance(items, list):
            return
        for item in items:
            item_path = item.get("path", "")
            item_type = item.get("type", "")
            name = item.get("name", "")
            if item_type == "dir":
                if name in {".git", "__pycache__", ".venv", "venv"}:
                    continue
                self._walk(item_path, collected)
            elif item_type == "file" and item_path.endswith(".py"):
                collected.append(item_path)

    def _analyze_file(self, path: str, module_names: Set[str]) -> PythonModuleReport:
        report = PythonModuleReport(path=path, module=self._path_to_module(path))
        try:
            content = github_runtime.read_file(path).get("content", "")
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        report.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if node.level:
                        module = "." * node.level + module
                    report.from_imports.append(module)
            external = set(report.imports + [item.lstrip(".") for item in report.from_imports])
            report.local_dependencies = sorted(
                dep for dep in external if dep in module_names or dep.split(".")[0] in {m.split(".")[0] for m in module_names}
            )
        except Exception as exc:  # noqa: BLE001
            report.error = f"{type(exc).__name__}: {exc}"
        return report

    def _path_to_module(self, path: str) -> str:
        return path.removesuffix(".py").replace("/", ".")

    def _suggest_destination(self, path: str) -> str:
        name = path.rsplit("/", 1)[-1]
        lower = name.lower()
        if any(token in lower for token in ["agent", "ceo", "planner", "research", "brain"]):
            return f"agents/{name}"
        if any(token in lower for token in ["auth", "security", "permission"]):
            return f"core/security/{name}"
        if any(token in lower for token in ["chat", "prompt", "response", "validator", "guard"]):
            return f"services/chat/{name}"
        if any(token in lower for token in ["memory", "knowledge", "context", "document"]):
            return f"services/knowledge/{name}"
        if any(token in lower for token in ["queue", "workflow", "scheduler", "runtime", "orchestrator"]):
            return f"runtime/{name}"
        if any(token in lower for token in ["vector", "embedding", "chunk", "rag"]):
            return f"vector/{name}"
        if any(token in lower for token in ["log", "metric", "monitor", "health"]):
            return f"services/monitoring/{name}"
        return f"core/{name}"


dependency_analyzer = DependencyAnalyzer()
