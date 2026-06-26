class ProductionScheduler:
    def config(self):
        return {'engine':'APScheduler','evolution_interval_minutes':30,'retention_cron':'0 3 * * *','status':'configured'}
production_scheduler=ProductionScheduler()
