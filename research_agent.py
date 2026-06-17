class ResearchAgent:
    def analyze(self, query:str):
        return {
            "query": query,
            "keywords": query.split(),
            "status": "ready"
        }
