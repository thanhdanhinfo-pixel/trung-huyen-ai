from collections import defaultdict

class EventSubscriptions:
    def __init__(self):
        self._subs = defaultdict(set)

    def subscribe(self, event_type:str, consumer:str):
        self._subs[event_type].add(consumer)
        return {'event_type':event_type,'consumer':consumer,'status':'subscribed'}

    def snapshot(self):
        return {k:list(v) for k,v in self._subs.items()}

event_subscriptions = EventSubscriptions()
