from planner_agent import PlannerAgent
from multi_agent_manager import MultiAgentManager

planner = PlannerAgent()
manager = MultiAgentManager()

def planner_status():
    sample = planner.create_plan('planning engine health check')
    return {
        'status': sample.get('status','unknown'),
        'intent': sample.get('intent',{}).get('name'),
        'task_count': sample.get('task_count',0)
    }


def worker_status():
    data = manager.dispatch('health_check')
    return {
        'status': 'active',
        'agents': data.get('agents',[]),
        'count': len(data.get('agents',[]))
    }
