import json
recommendations={'application/planning':['planner_agent.py','master_planner.py','query_planner.py'],'application/orchestration':['task_agent.py','task_queue.py','workflow_engine.py','multi_agent_manager.py'],'knowledge/core':['knowledge_graph.py','vectordb.py'],'kernel/governance':['rule_engine.py','decision_engine.py']}
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'artifacts'; out.mkdir(exist_ok=True)
(out/'move_plan.json').write_text(json.dumps(recommendations,indent=2),encoding='utf-8')