from time import perf_counter 

class PerformanceMonitor:
    def start(self):
        self.t=perf_counter()
    def stop(self):
        return {"elapsed":round(perf_counter()-self.t,4)}
