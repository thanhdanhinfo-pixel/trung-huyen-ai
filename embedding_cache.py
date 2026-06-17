import hashlib

def key(text:str)->str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
