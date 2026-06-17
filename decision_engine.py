class DecisionEngine:
    def decide(self, options:list):
        if not options:
            return None
        return options[0]
