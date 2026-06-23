from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.workflow_engine import workflow_engine
from services.code_transformer import code_transformer
from services.code_transaction import code_transaction_engine

router = APIRouter(tags=["Developer Gateway"])


class DeveloperExecuteRequest(BaseModel):
    action: str
    payload: dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False
    auto_run: bool = True


class TransformRequest(BaseModel):
    operation: str
    path: str
    commit: bool = False
    params: dict[str, Any] = Field(default_factory=dict)


class TransactionRequest(BaseModel):
    steps: list[dict[str, Any]] = Field(default_factory=list)
    commit: bool = False


@router.post("/developer/execute")
def developer_execute(req: DeveloperExecuteRequest):
    return workflow_engine.submit(
        action=f"developer.{req.action}",
        payload=req.payload,
        requires_approval=req.requires_approval,
        auto_run=req.auto_run,
    )


@router.post("/developer/transform")
def developer_transform(req: TransformRequest):
    ops = {
        "insert_import": code_transformer.insert_import,
        "insert_after": code_transformer.insert_after,
        "replace_block": code_transformer.replace_block,
        "replace_function": code_transformer.replace_function,
        "register_router": code_transformer.register_router,
    }
    if req.operation not in ops:
        return {"status": "error", "message": "Unsupported operation"}
    return ops[req.operation](path=req.path, commit=req.commit, **req.params)


@router.get("/developer/transaction/status")
def developer_transaction_status():
    return code_transaction_engine.status()


@router.get("/developer/transaction/history")
def developer_transaction_history():
    return {"status": "ok", "history": code_transaction_engine.history()}


@router.post("/developer/transaction")
def developer_transaction(req: TransactionRequest):
    if req.commit:
        return code_transaction_engine.execute(req.steps)
    return code_transaction_engine.preview(req.steps)


@router.get("/developer/workflow/status")
def developer_workflow_status():
    return workflow_engine.status()


@router.get("/developer/workflow/tasks")
def developer_workflow_tasks():
    return {"status": "ok", "tasks": workflow_engine.queue()}
