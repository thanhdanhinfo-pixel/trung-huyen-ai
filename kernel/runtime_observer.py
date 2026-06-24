from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


def now()->str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class RuntimeSnapshot:
    observed_at:str=field(default_factory=now)
    kernel_status:str="unknown"
    runtime:Dict[str,Any]=field(default_factory=dict)
    health:Dict[str,Any]=field(default_factory=dict)
    services:Dict[str,Any]=field(default_factory=dict)

    def to_dict(self)->Dict[str,Any]:
        return {
            "observed_at":self.observed_at,
            "kernel_status":self.kernel_status,
            "runtime":self.runtime,
            "health":self.health,
            "services":self.services,
        }

class RuntimeObserver:
    def observe(self,kernel:Any)->RuntimeSnapshot:
        return RuntimeSnapshot(
            kernel_status="running",
            runtime=kernel.runtime.snapshot(),
            health=kernel.health.check(kernel),
            services={
                "execute_api":"online",
                "system_awareness":"online"
            }
        )

runtime_observer=RuntimeObserver()
