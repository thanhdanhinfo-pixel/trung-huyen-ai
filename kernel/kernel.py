from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class AIKernelIdentity:
    """Identity layer of TRUNG_HUYEN_AI_OS.

    This answers the first Kernel question:
    "Who am I inside this system?"
    """

    system_name: str = "TRUNG_HUYEN_AI_OS"
    role: str = "AI Chief Architect / AI CTO"
    mission: str = "Understand, operate and evolve the Trung Huyen AI OS."
    owner: str = "Trung Huyen"
    architecture_version: str = "AI_OS_V1_KERNEL_FIRST"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "system_name": self.system_name,
            "role": self.role,
            "mission": self.mission,
            "owner": self.owner,
            "architecture_version": self.architecture_version,
        }


@dataclass
class AIKernel:
    """Single entry point for the future AI OS Kernel.

    The Kernel is intentionally minimal at this stage. It establishes the
    stable boot contract first, then registry/capability/runtime/memory/
    governance/health will be attached incrementally.
    """

    identity: AIKernelIdentity = field(default_factory=AIKernelIdentity)
    booted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def boot_status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "kernel": "booted",
            "booted_at": self.booted_at,
            "identity": self.identity.as_dict(),
            "next_layers": [
                "registry",
                "capability",
                "runtime",
                "memory",
                "governance",
                "health",
            ],
        }

    def answer_self_question(self) -> Dict[str, Any]:
        """Return the Kernel's current self-understanding."""
        return {
            "who_am_i": self.identity.as_dict(),
            "what_stage": "kernel_foundation_refactor",
            "what_is_missing": [
                "registry layer",
                "capability layer",
                "runtime layer",
                "memory layer",
                "governance layer",
                "health layer",
            ],
        }


kernel = AIKernel()
