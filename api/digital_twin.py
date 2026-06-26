from fastapi import APIRouter

try:
    from system.digital_twin_simulation import digital_twin_simulation
except Exception as exc:
    print('DIGITAL_TWIN_IMPORT_FAILED:', exc)
    digital_twin_simulation = None

router = APIRouter(prefix='/digital-twin', tags=['digital-twin'])


@router.get('/health')
def health():
    return {
        'status': 'online' if digital_twin_simulation else 'safe-mode',
        'simulation_loaded': bool(digital_twin_simulation),
    }


@router.get('/state')
def state():
    return {
        'identity': 'TRUNG_HUYEN_AI_OS',
        'mode': 'safe-mode',
        'connected': bool(digital_twin_simulation),
    }


@router.get('/profile')
def profile():
    return {
        'system': 'digital_twin',
        'version': 'v1',
    }


@router.get('/simulate')
def simulate(add_workers: int = 0):
    if digital_twin_simulation:
        return digital_twin_simulation.simulate(add_workers)
    return {'status': 'safe-mode'}
