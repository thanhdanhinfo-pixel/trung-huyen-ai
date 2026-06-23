from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from services.github_runtime import github_runtime


@dataclass
class TransformResult:
    path: str
    status: str
    changed: bool = False
    message: str = ""
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CodeTransformer:
    """Small, safe code transformation engine.

    This avoids rewriting large files manually. It performs targeted text/AST
    aware operations and validates Python syntax before commit.
    """

    def insert_import(
        self,
        path: str,
        import_line: str,
        commit: bool = False,
        message: str = "Insert import",
    ) -> Dict[str, Any]:
        current = github_runtime.read_file(path)
        old_content = current.get("content", "")
        lines = old_content.splitlines()

        if import_line in lines:
            return TransformResult(path=path, status="noop", message="Import already exists").to_dict()

        insert_at = 0
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                insert_at = index + 1

        lines.insert(insert_at, import_line)
        new_content = "\n".join(lines) + ("\n" if old_content.endswith("\n") else "")
        return self._finalize(path, old_content, new_content, current.get("sha"), commit, message)

    def insert_after(
        self,
        path: str,
        anchor: str,
        code: str,
        commit: bool = False,
        message: str = "Insert code after anchor",
    ) -> Dict[str, Any]:
        current = github_runtime.read_file(path)
        old_content = current.get("content", "")
        if code in old_content:
            return TransformResult(path=path, status="noop", message="Code already exists").to_dict()
        if anchor not in old_content:
            return TransformResult(path=path, status="blocked", message="Anchor not found").to_dict()
        new_content = old_content.replace(anchor, anchor + "\n" + code, 1)
        return self._finalize(path, old_content, new_content, current.get("sha"), commit, message)

    def replace_block(
        self,
        path: str,
        find: str,
        replace: str,
        commit: bool = False,
        message: str = "Replace code block",
    ) -> Dict[str, Any]:
        current = github_runtime.read_file(path)
        old_content = current.get("content", "")
        if find not in old_content:
            return TransformResult(path=path, status="blocked", message="Block not found").to_dict()
        new_content = old_content.replace(find, replace, 1)
        return self._finalize(path, old_content, new_content, current.get("sha"), commit, message)

    def replace_function(
        self,
        path: str,
        function_name: str,
        new_code: str,
        commit: bool = False,
        message: str = "Replace function",
    ) -> Dict[str, Any]:
        current = github_runtime.read_file(path)
        old_content = current.get("content", "")
        try:
            tree = ast.parse(old_content)
            lines = old_content.splitlines()
            target: Optional[ast.AST] = None
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                    target = node
                    break
            if target is None or not hasattr(target, "lineno") or not hasattr(target, "end_lineno"):
                return TransformResult(path=path, status="blocked", message="Function not found").to_dict()

            start = int(getattr(target, "lineno")) - 1
            end = int(getattr(target, "end_lineno"))
            replacement_lines = new_code.rstrip("\n").splitlines()
            new_lines = lines[:start] + replacement_lines + lines[end:]
            new_content = "\n".join(new_lines) + ("\n" if old_content.endswith("\n") else "")
            return self._finalize(path, old_content, new_content, current.get("sha"), commit, message)
        except Exception as exc:  # noqa: BLE001
            return TransformResult(
                path=path,
                status="failed",
                message=f"{type(exc).__name__}: {exc}",
            ).to_dict()

    def register_router(
        self,
        path: str,
        import_line: str,
        router_line: str,
        anchor: str,
        commit: bool = False,
    ) -> Dict[str, Any]:
        current = github_runtime.read_file(path)
        old_content = current.get("content", "")
        content = old_content
        changed_steps = []

        if import_line not in content:
            lines = content.splitlines()
            insert_at = 0
            for index, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("import ") or stripped.startswith("from "):
                    insert_at = index + 1
            lines.insert(insert_at, import_line)
            content = "\n".join(lines) + ("\n" if old_content.endswith("\n") else "")
            changed_steps.append("insert_import")

        if router_line not in content:
            if anchor not in content:
                return TransformResult(
                    path=path,
                    status="blocked",
                    changed=content != old_content,
                    message="Router anchor not found",
                    details={"steps": changed_steps},
                ).to_dict()
            content = content.replace(anchor, anchor + "\n" + router_line, 1)
            changed_steps.append("insert_router")

        return self._finalize(
            path=path,
            old_content=old_content,
            new_content=content,
            sha=current.get("sha"),
            commit=commit,
            message="Register API router",
            details={"steps": changed_steps},
        )

    def _finalize(
        self,
        path: str,
        old_content: str,
        new_content: str,
        sha: Optional[str],
        commit: bool,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        warnings: List[str] = []
        if path.endswith(".py"):
            try:
                ast.parse(new_content)
            except SyntaxError as exc:
                return TransformResult(
                    path=path,
                    status="blocked",
                    changed=new_content != old_content,
                    message=f"python_syntax_error: line {exc.lineno}: {exc.msg}",
                    warnings=["python_syntax_error"],
                    details=details or {},
                ).to_dict()

        changed = new_content != old_content
        if not changed:
            return TransformResult(path=path, status="noop", changed=False, message="No changes", details=details or {}).to_dict()

        if not commit:
            return TransformResult(
                path=path,
                status="preview",
                changed=True,
                message="Preview only",
                warnings=warnings,
                details=details or {},
            ).to_dict()

        result = github_runtime.update_file(path=path, content=new_content, message=message, sha=sha)
        verify = github_runtime.read_file(path)
        return TransformResult(
            path=path,
            status="committed" if verify.get("content") == new_content else "failed",
            changed=True,
            message=message,
            warnings=warnings,
            details={"commit": result.get("commit", {}), **(details or {})},
        ).to_dict()


code_transformer = CodeTransformer()
