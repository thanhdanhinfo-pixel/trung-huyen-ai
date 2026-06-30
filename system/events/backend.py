class DistributedBackend:
    SUPPORTED=['redis-streams','nats','kafka']
    def status(self):
        return {'supported':self.SUPPORTED,'active':'redis-streams','mode':'single-node-compatible'}

distributed_backend=DistributedBackend() 
