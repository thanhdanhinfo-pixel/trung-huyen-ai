from fastapi import APIRouter
from pydantic import BaseModel
from services.github_runtime import github_runtime
import difflib
import ast
router = APIRouter(prefix="/github", tags=["GitHub Runtime"])

class ReadFile(BaseModel):
    path:str

class UpdateFile(BaseModel):
    path:str
    content:str
    message:str
    sha:str|None=None
class PatchOperation(BaseModel):
    type: str
    find: str = ""
    replace: str = ""


class PatchFile(BaseModel):
    path: str
    operations: list[PatchOperation]
    message: str = "Safe patch update"
    commit: bool = False

@router.get('/runtime/status')
def runtime_status():
    return github_runtime.status()

@router.get('/list')
def list_files(path:str=''):
    return {'status':'ok','files':github_runtime.list_files(path)}

@router.post('/read')
def read(req:ReadFile):
    return github_runtime.read_file(req.path)

@router.post('/update')
def update(req:UpdateFile):
    return github_runtime.update_file(req.path,req.content,req.message,req.sha)

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
    # Python syntax verification
    if req.path.endswith(".py"):
        try:
            ast.parse(new_content)
        except SyntaxError as e:
            warnings.append(
                f"python_syntax_error: line {e.lineno}: {e.msg}"
            )

    result["warnings"] = warnings
    result["ready_to_commit"] = (
        new_content != old_content and len(warnings) == 0
    )
    if not req.commit:
        return result

    if warnings:
        return {
            "status": "blocked",
            "warnings": warnings,
            "diff": diff,
        }

    commit_result = github_runtime.update_file(
        path=req.path,
        content=new_content,
        message=req.message,
        sha=current.get("sha"),
    )

    verify = github_runtime.read_file(req.path)

    return {
        "status": "committed",
        "path": req.path,
        "commit": commit_result.get("commit", {}),
        "verified": verify.get("content") == new_content,
    }
