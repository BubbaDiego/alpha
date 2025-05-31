"""Simple registry for Jupiter Auto Engine steps."""

from __future__ import annotations

from typing import Callable, Dict, Optional


class StepRegistry:
    """Registry mapping step names to callables."""

    def __init__(self) -> None:
        self._registry: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable) -> None:
        """Register a step function under ``name``."""
        self._registry[name] = func

    def get(self, name: str) -> Optional[Callable]:
        """Return the registered step function for ``name``."""
        return self._registry.get(name)

    def all(self) -> Dict[str, Callable]:
        """Return a copy of the registry mapping."""
        return dict(self._registry)

    def unregister(self, name: str) -> None:
        """Remove a previously registered step."""
        self._registry.pop(name, None)
