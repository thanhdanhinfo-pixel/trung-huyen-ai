class AgentOrchestrator:
    def __init__(self):
        self.agents={}
    def register(self,name,agent):
        self.agents[name]=agent
    def list_agents(self):
        return list(self.agents.keys())
