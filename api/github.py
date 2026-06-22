from fastapi import APIRouter
from pydantic import BaseModel
from services.github_runtime import github_runtime

router = APIRouter(prefix="/github", tags=["GitHub Runtime"])

class ReadFile(BaseModel):
    path:str

class UpdateFile(BaseModel):
    path:str
    content:str
    message:str
    sha:str|None=None

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
