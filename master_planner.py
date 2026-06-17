class MasterPlanner:
    def create_plan(self, goal):
        return {
            "goal": goal,
            "phases":[
                "Analyze",
                "Design",
                "Execute",
                "Review"
            ]
        }
