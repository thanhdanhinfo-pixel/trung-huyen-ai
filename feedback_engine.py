class FeedbackEngine:
    def process(self, feedback):
        return {"received": len(feedback), "status":"processed"}
