from __future__ import annotations

from system.system_awareness import system_awareness
from system.digital_twin import digital_twin
from runtime_health import runtime_health


class ObservabilityLayer:

    def system_snapshot(self):
        return {
            'awareness': system_awareness.snapshot(),
            'digital_twin': digital_twin.snapshot(),
            'runtime': runtime_health.status(),
        }

    def capability_status(self):
        registry = system_awareness.capability_registry()
        groups = registry.get('capability_groups', {})
        return {k: v.get('status') for k, v in groups.items()}

    def memory_status(self):
        return {
            'self_state': 'loaded',
            'digital_twin': 'loaded',
            'memory_log': 'available',
        }

    def github_status(self):
        return {'status': 'connected'}

    def drive_status(self):
        return {'status': 'active'}

    def planner_status(self):
        from system.agent_runtime import planner_status
        return planner_status()

    def worker_status(self):
        from system.agent_runtime import worker_status
        return worker_status()


observability = ObservabilityLayer()
