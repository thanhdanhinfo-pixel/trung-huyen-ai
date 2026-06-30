REQUEST_COUNT=0 

def inc():
    global REQUEST_COUNT
    REQUEST_COUNT += 1

def stats():
    return {"requests":REQUEST_COUNT}
