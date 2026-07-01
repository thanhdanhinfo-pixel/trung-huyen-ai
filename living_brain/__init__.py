"""Living Brain control-plane entrypoint.

This package is the only operational Brain namespace.
- living_brain = control plane / coordination authority
- kernel = neural core implementation
- brain/ = knowledge layer only
"""

from kernel.kernel import kernel as brain

__all__ = ["brain"]
