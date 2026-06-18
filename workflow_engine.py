class WorkflowEngine:
    def run(self, steps:list):
        return [{
            "step": step,
            "status": "done"
        } for step in steps]
