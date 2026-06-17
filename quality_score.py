def score(answer:str,sources:int):
    s=min(100,len(answer)//20 + sources*10)
    return {"score":s}
