class TaskQueue:
    def __init__(self):
        self.tasks=[]
    def push(self, task):
        self.tasks.append(task)
    def pop(self):
        return self.tasks.pop(0) if self.tasks else None
