class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name:str, tool):
        self.tools[name] = tool

    def list(self):
        return list(self.tools.keys())
