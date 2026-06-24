from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict
from .registry import load_registry
from .runtime import runtime as kernel_runtime
from .capability import load_capabilities
from .memory import load_memory

@dataclass
class AIKernelIdentity:
    system_name:str="TRUNG_HUYEN_AI_OS"
    role:str="AI Chief Architect / AI CTO"
    mission:str="Understand, operate and evolve the AI OS"
    owner:str="Trung Huyen"
    architecture_version:str="AI_OS_V2_KERNEL"
    def as_dict(self)->Dict[str,Any]: return self.__dict__.copy()

@dataclass
class AIKernel:
    identity:AIKernelIdentity=field(default_factory=AIKernelIdentity)
    registry:any=field(default_factory=load_registry)
    runtime:any=field(default_factory=lambda: kernel_runtime)
    capabilities:any=field(default_factory=load_capabilities)
    memory:any=field(default_factory=load_memory)
    booted_at:str=field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    def boot_status(self)->Dict[str,Any]:
        return {
            "status":"ok",
            "booted_at":self.booted_at,
            "identity":self.identity.as_dict(),
            "registry":self.registry.validate(),
            "runtime":self.runtime.snapshot(),
            "capabilities":self.capabilities.validate(),
            "memory":self.memory.as_dict()
        }
    def self_awareness(self)->Dict[str,Any]:
        return {
            "identity":self.identity.as_dict(),
            "registry":self.registry.as_dict(),
            "runtime":self.runtime.snapshot(),
            "capabilities":self.capabilities.summary(),
            "memory_records":self.memory.as_dict()["record_count"]
        }
kernel=AIKernel()