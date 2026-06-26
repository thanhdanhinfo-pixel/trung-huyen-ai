class WsSubscriptions:
    def match(self,subs,event_type):
        return any(s.endswith('*') and event_type.startswith(s[:-1]) or s==event_type for s in subs)
ws_subscriptions=WsSubscriptions()
