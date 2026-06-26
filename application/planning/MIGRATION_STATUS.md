# Planning Migration Status

Phase: PREPARE

Target modules:
- planner_agent.py
- master_planner.py
- query_planner.py

Policy:
1. Move implementation.
2. Keep root compatibility shims.
3. Audit imports before removing root modules.
