from fastapi.responses import JSONResponse

def error(message:str,status:int=500):
    return JSONResponse(status_code=status,content={"status":"error","message":message})
