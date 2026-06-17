class TaskAgent:
    def execute(self, task:dict):
        return {
            "task": task,
            "status": "completed"
        }
