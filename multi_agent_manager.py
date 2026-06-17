class MultiAgentManager:
    def dispatch(self, task):
        return {
            "task": task,
            "agents": [
                "AI_CEO",
                "AI_RESEARCH",
                "AI_CONTENT",
                "AI_PLANNER"
            ]
        }
