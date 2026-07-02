from fastapi import APIRouter
from pydantic import BaseModel, Field
from services.github_runtime import github_runtime
import difflib
import ast
import re
import time
import requests
from typing import Any

router = APIRouter(prefix="/github", tags=["GitHub Runtime"])

class RefactorImportsRequest(BaseModel):
    mapping: dict[str, str]
    paths: list[str] = Field(default_factory=list)
    message: str = "Refactor Python imports"
    commit: bool = False
    
class ReadFile(BaseModel):
    path: str


class UpdateFile(BaseModel):
    path: str
    content: str
    message: str
    sha: str | None = None


class DeleteFile(BaseModel):
    path: str
    message: str = "Delete file"


class MoveFile(BaseModel):
    source: str
    destination: str
    message: str = "Move file"


class BatchCommit(BaseModel):
    operations: list[dict[str, Any]]
    message: str = "Batch repository update"


class CleanupRepository(BaseModel):
    commit: bool = False


class PatchOperation(BaseModel):
    type: str
    find: str = ""
    replace: str = ""


class PatchFile(BaseModel):
    path: str
    operations: list[PatchOperation]
    message: str = "Safe patch update"
    commit: bool = False

class MoveBatchRequest(BaseModel):
    moves: list[dict[str, str]] = Field(default_factory=list)
    message: str = "Batch move files"
    commit: bool = False
    
class MkdirRequest(BaseModel):
    paths: list[str] = Field(default_factory=list)
    message: str = "Create repository directories"
    
class PatchBatchItem(BaseModel):
    path: str
    operations: list[PatchOperation] = Field(default_factory=list)

    
class PatchBatchRequest(BaseModel):
    files: list[PatchBatchItem] = Field(default_factory=list)
    message: str = "Batch patch files"
    commit: bool = False

@router.post("/refactor-imports")
def refactor_imports(req: RefactorImportsRequest):
    paths = req.paths

    if not paths:
        all_files = github_runtime.list_files("")
        paths = [
            item["path"]
            for item in all_files
            if item.get("type") == "file" and item.get("path", "").endswith(".py")
        ]

    results = []

    for path in paths:
        current = github_runtime.read_file(path)
        old_content = current.get("content", "")
        new_content = old_content

        for old, new in req.mapping.items():
            old_escaped = re.escape(old)

            new_content = re.sub(
                rf"(^|\n)(\s*)from {old_escaped} import ",
                rf"\1\2from {new} import ",
                new_content,
            )

            new_content = re.sub(
                rf"(^|\n)(\s*)import {old_escaped}(\s+as\s+\w+)?(\s*(?:#.*)?)(?=\n|$)",
                rf"\1\2import {new}\3\4",
                new_content,
            )

        if new_content == old_content:
            results.append({
                "path": path,
                "changed": False,
            })
            continue

        if req.commit:
            result = github_runtime.update_file(
                path=path,
                content=new_content,
                message=req.message,
                sha=current.get("sha"),
            )
        else:
            result = {
                "status": "preview",
                "changed": True,
            }

        results.append({
                "path": path,
                "changed": True,
                "result": result,
        })

    return {
        "status": "ok",
        "commit": req.commit,
        "count": len(results),
        "results": results,
    }

@router.post("/move-batch")
def move_batch(req: MoveBatchRequest):
    results = []

    for item in req.moves:
        source = item.get("from") or item.get("source")
        destination = item.get("to") or item.get("destination")

        if not source or not destination:
            results.append({
                "status": "error",
                "message": "source and destination are required",
                "item": item,
            })
            continue

        if source == destination:
            results.append({
                "status": "skipped",
                "message": "source and destination are identical",
                "source": source,
                "destination": destination,
            })
            continue

        if not req.commit:
            results.append({
                "status": "preview",
                "source": source,
                "destination": destination,
                "ready_to_commit": True,
            })
            continue

        try:
            result = github_runtime.move_file(
                source=source,
                destination=destination,
                message=req.message,
            )
            results.append(result)
        except Exception as exc:
            results.append({
                "status": "error",
                "source": source,
                "destination": destination,
                "message": str(exc),
            })

    return {
        "status": "ok",
        "commit": req.commit,
        "count": len(results),
        "results": results,
    }
    
@router.post("/patch-batch")
def patch_batch(req: PatchBatchRequest):
    results = []

    for item in req.files:
        patch_request = PatchFile(
            path=item.path,
            operations=item.operations,
            message=req.message,
            commit=req.commit,
        )

        result = patch(patch_request)

        results.append({
            "path": item.path,
            "result": result,
        })

    return {
        "status": "ok",
        "count": len(results),
        "results": results,
    }
    
@router.get('/runtime/status')
def runtime_status():
    return github_runtime.status()

@router.post("/mkdir")
def mkdir(req: MkdirRequest):
    results = []

    for path in req.paths:
        clean = path.strip("/")

        if not clean:
            continue

        try:
            result = github_runtime.update_file(
                path=f"{clean}/.gitkeep",
                content="",
                message=req.message,
                sha=None,
            )

            results.append({
                "path": clean,
                "status": "ok",
                "result": result,
            })

        except Exception as exc:
            results.append({
                "path": clean,
                "status": "error",
                "message": str(exc),
            })

    return {
        "status": "ok",
        "count": len(results),
        "results": results,
    }
    
@router.get('/list')
def list_files(path: str = ''):
    return {'status': 'ok', 'files': github_runtime.list_files(path)}


@router.post('/read')
def read(req: ReadFile):
    try:
        return github_runtime.read_file(req.path)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            return {
                "status": "not_found",
                "path": req.path,
                "message": f"File '{req.path}' does not exist"
            }
        raise


@router.post('/update')
def update(req: UpdateFile):
    return {"status":"error","message":"Direct write endpoint disabled. Use MCP governed tools."}


@router.post('/delete')
def delete(req: DeleteFile):
    return {"status":"error","message":"Direct write endpoint disabled. Use MCP governed tools."}


@router.post('/move')
def move(req: MoveFile):
    return {"status":"error","message":"Direct write endpoint disabled. Use MCP governed tools."}


@router.post('/batch')
def batch(req: BatchCommit):
    return {"status":"error","message":"Direct write endpoint disabled. Use MCP governed tools."}


@router.post('/cleanup')
def cleanup(req: CleanupRepository):
    return {"status":"error","message":"Direct write endpoint disabled. Use MCP governed tools."}


@router.post("/patch")
def patch(req: PatchFile):
    current = github_runtime.read_file(req.path)
    old_content = current.get("content", "")
    new_content = old_content

    for op in req.operations:
        if op.type == "replace":
            if not op.find or op.find not in new_content:
                return {"status": "error", "message": "find text not found"}
            new_content = new_content.replace(op.find, op.replace, 1)

        elif op.type == "insert_after":
            if not op.find or op.find not in new_content:
                return {"status": "error", "message": "anchor text not found"}
            new_content = new_content.replace(op.find, op.find + op.replace, 1)

        elif op.type == "insert_before":
            if not op.find or op.find not in new_content:
                return {"status": "error", "message": "anchor text not found"}
            new_content = new_content.replace(op.find, op.replace + op.find, 1)

        elif op.type == "append":
            new_content = new_content + op.replace

        elif op.type == "prepend":
            new_content = op.replace + new_content

        else:
            return {"status": "error", "message": f"Unsupported operation: {op.type}"}

    before_lines = old_content.splitlines()
    after_lines = new_content.splitlines()

    warnings = []
    if len(after_lines) < len(before_lines) * 0.8:
        warnings.append("line_count_drop_over_20_percent")

    diff = "\n".join(
        difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=f"before/{req.path}",
            tofile=f"after/{req.path}",
            lineterm="",
        )
    )

    result = {
        "status": "preview",
        "path": req.path,
        "changed": new_content != old_content,
        "warnings": warnings,
        "ready_to_commit": new_content != old_content and not warnings,
        "diff": diff,
    }
    if req.path.endswith(".py"):
        try:
            ast.parse(new_content)
        except SyntaxError as e:
            warnings.append(f"python_syntax_error: line {e.lineno}: {e.msg}")

    result["warnings"] = warnings
    result["ready_to_commit"] = new_content != old_content and len(warnings) == 0
    if not req.commit:
        return result

    if warnings:
        return {"status": "blocked", "warnings": warnings, "diff": diff}

    commit_result = github_runtime.update_file(
        path=req.path,
        content=new_content,
        message=req.message,
        sha=current.get("sha"),
    )

    verified = False
    for _ in range(5):
        time.sleep(0.5)
        verify = github_runtime.read_file(req.path)
        if verify.get("content") == new_content:
            verified = True
            break

    return {
        "status": "committed",
        "path": req.path,
        "commit": commit_result.get("commit", {}),
        "verified": verified,
    }
