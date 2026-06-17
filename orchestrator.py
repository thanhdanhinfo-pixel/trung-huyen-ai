class Orchestrator:
    def execute(self, workflow):
        return {
            "workflow": workflow,
            "status":"running"
        }
