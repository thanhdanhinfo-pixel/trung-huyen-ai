"""AI Kernel package for TRUNG_HUYEN_AI_OS.

The kernel is the single entry point for identity, registry,
capability, runtime, discovery, memory, governance and health.
"""

from .kernel import AIKernel, kernel

__all__ = ["AIKernel", "kernel"]
