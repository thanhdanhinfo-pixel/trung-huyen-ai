from fastapi import APIRouter
from system.digital_twin_simulation import digital_twin_simulation

router=APIRouter(prefix='/digital-twin',tags=['digital-twin'])

@router.get('/simulate')
def simulate(add_workers:int=0):
    return digital_twin_simulation.simulate(add_workers)
