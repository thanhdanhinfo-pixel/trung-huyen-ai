from fastapi import APIRouter

try:
    from system.capability_lineage import capability_lineage
except Exception as exc:
    print('GRAPH_IMPORT_FAILED:', exc)
    capability_lineage = None

router = APIRouter(prefix='/graph', tags=['graph'])


@router.get('/health')
def health():
    return {
        'status': 'online' if capability_lineage else 'safe-mode',
        'lineage_loaded': bool(capability_lineage),
    }


@router.get('/capabilities')
def capability_graph():
    lineage = capability_lineage.snapshot() if capability_lineage else {}
    return {
        'nodes': ['governance', 'evolution', 'knowledge_graph'],
        'edges': [
            ['knowledge_graph', 'evolution'],
            ['governance', 'evolution'],
        ],
        'lineage': lineage,
        'mode': 'safe-mode' if not capability_lineage else 'online',
    }
