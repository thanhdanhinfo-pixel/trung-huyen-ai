import os
class RedisEventBus:
    def status(self):
        return {'enabled':os.getenv('EVENT_BACKEND')=='redis','url':os.getenv('REDIS_URL','redis://localhost:6379/0'),'mode':'adapter-ready'}
redis_event_bus=RedisEventBus()
