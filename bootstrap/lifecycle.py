from system.bootstrap import boot
from system.production_scheduler import production_scheduler

async def startup():
    boot()
    production_scheduler.start()
