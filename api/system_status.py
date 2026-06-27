from fastapi import APIRouter, Query
import os

router=APIRouter(prefix='/system',tags=['system'])

@router.get('/status')
def status():
    return {
        'system':'TRUNG_HUYEN_AI_OS',
        'runtime':'online',
        'revision':os.getenv('K_REVISION'),
        'capabilities_url':'/system/capabilities',
        'self_awareness_url':'/system/self-awareness',
        'repository_tree_url':'/system/repository-tree',
        'folder_health_url':'/system/folder-health',
        'protected_files_url':'/system/protected-files',
        'repository_observer_version':'L1-runtime-verified'
    }

@router.get('/capabilities')
def capabilities():
    return {
        'openai':True,
        'qdrant':True,
        'drive':True,
        'github':True,
        'cloud_build':True,
        'cloud_logging':True,
        'monitoring':True,
        'mcp':True,
        'repository_observer':True
    }

@router.get('/self-awareness')
def self_awareness():
    return {
        'identity':'TRUNG_HUYEN_AI_OS',
        'mode':'production-self-observed',
        'health':'green'
    }

@router.get('/watchdog')
def watchdog():
    return {
        'status':'ok',
        'mode':'passive',
        'auto_restart':False,
        'rollback_enabled':True,
        'last_revision':os.getenv('K_REVISION')
    }

@router.get('/runtime-graph')
def runtime_graph():
    return {
        'status':'green',
        'nodes':['openai','qdrant','drive','github','cloud_build','cloud_logging','secret_manager','mcp'],
        'edges':[
            ['openai','qdrant'],
            ['drive','qdrant'],
            ['github','cloud_build'],
            ['cloud_build','cloud_run']
        ]
    }

@router.get('/repository-tree')
def repository_tree(depth:int=Query(default=1,ge=1,le=3)):
    from services.repository_observer import repository_tree as get_tree
    return get_tree(depth=depth)

@router.get('/folder-health')
def folder_health():
    from services.repository_observer import folder_health as get_health
    return get_health()

@router.get('/protected-files')
def protected_files():
    from services.repository_observer import protected_files as get_protected
    return get_protected()
