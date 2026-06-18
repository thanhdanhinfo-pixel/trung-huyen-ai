from math import sqrt

def cosine_similarity(a,b):
    if len(a)!=len(b):
        return 0.0
    dot=sum(x*y for x,y in zip(a,b))
    na=sqrt(sum(x*x for x in a))
    nb=sqrt(sum(y*y for y in b))
    if na==0 or nb==0:
        return 0.0
    return dot/(na*nb)
