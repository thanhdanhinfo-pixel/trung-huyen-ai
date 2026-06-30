class ConversationMemory: 
    def __init__(self):
        self.history=[]
    def add(self,role,content):
        self.history.append({"role":role,"content":content})
    def recent(self,n=10):
        return self.history[-n:]
