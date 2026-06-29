_CACHE={} 

def get(key):
    return _CACHE.get(key)

def set(key,value):
    _CACHE[key]=value

def clear():
    _CACHE.clear()
