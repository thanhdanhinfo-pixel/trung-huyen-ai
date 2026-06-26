from system.event_bus import event_bus

def replay(limit=100):
    return {'mode':'replay','events':event_bus.recent(limit)}
