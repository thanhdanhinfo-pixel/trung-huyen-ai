from fastapi import APIRouter
import os

router=APIRouter(prefix='/system',tags=['system'])

@router.get('/status')
def status():
    return {
        'system':'TRUNG_HUYEN_AI_OS',
        'runtime':'online',
        'revision':os.getenv('K_REVISION'),
        'capabilities_url':'/system/capabilities',
        'self_awareness_url':'/system/self-awareness'
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
        'mcp':True
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
