from task_queue import TaskQueue  
queue=TaskQueue()
def task_status():
    snapshot=queue.snapshot()
    return {'pending_count':snapshot['pending_count'],'history_count':snapshot['history_count'],'pending':snapshot['pending'],'history':snapshot['history'][-10:]}
