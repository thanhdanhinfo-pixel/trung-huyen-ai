class DigitalTwinSimulation:
    def simulate(self, add_workers=0):  
        return {'expected_latency_change_pct':-10*add_workers,'resource_usage_change_pct':5*add_workers,'risk':'low' if add_workers<=2 else 'medium'}
digital_twin_simulation=DigitalTwinSimulation()
