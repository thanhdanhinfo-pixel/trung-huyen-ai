class GoalManager:
    def create_goal(self, title:str):
        return {
            "title": title,
            "status": "created",
            "progress": 0
        }
