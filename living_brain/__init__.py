"""Living Brain control-plane entrypoint.

This package is the only operational control plane.
- living_brain = coordination authority
- kernel = neural core implementation
- brain/ = deprecated knowledge namespace pending rename
"""

from kernel.kernel import kernel as neural_core

brain = neural_core

__all__ = ["brain", "neural_core"]
