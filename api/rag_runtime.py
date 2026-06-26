from fastapi import APIRouter

try:
    from rag.search import search_knowledge
except Exception as exc:
    print('RAG_IMPORT_FAILED:', exc)
    search_knowledge = None

router = APIRouter(prefix='/rag', tags=['rag-runtime'])

@router.get('/status')
def status():
    return {
        'status': 'online' if search_knowledge else 'safe-mode',
        'search_loaded': bool(search_knowledge)
    }

@router.get('/sources')
def sources():
    return {
        'sources': ['google_drive', 'qdrant', 'knowledge_base'],
        'mode': 'safe-mode' if not search_knowledge else 'online'
    }
