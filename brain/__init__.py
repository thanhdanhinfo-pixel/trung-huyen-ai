"""Living Brain entrypoint.

Single brain instance for the entire system.
Do not create another coordinator.
"""

from kernel.kernel import kernel as brain

__all__ = ["brain"]
