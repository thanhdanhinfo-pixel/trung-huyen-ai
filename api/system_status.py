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
