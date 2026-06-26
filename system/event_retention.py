class EventRetention:
    def policy(self):
        return {
            'max_events': 1000,
            'archive_after_days': 30,
            'strategy': 'rolling_window'
        }

event_retention = EventRetention()
