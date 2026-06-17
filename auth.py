from fastapi import Header, HTTPException

def verify_api_key(x_api_key: str | None = Header(default=None)):
    # TODO: thay bằng kiểm tra API key thật
    return True
