from fastapi import APIRouter
from system.capability_lineage import capability_lineage

router=APIRouter(prefix='/graph',tags=['graph'])

@router.get('/capabilities')
def capability_graph():
    return {
        'nodes':['governance','evolution','knowledge_graph'],
        'edges':[['knowledge_graph','evolution'],['governance','evolution']],
        'lineage': capability_lineage.snapshot()
    }
