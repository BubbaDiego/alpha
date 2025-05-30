"""Re-export :class:`PhantomManager` from :mod:`auto_core.playwright`."""

try:  # PhantomManager depends on Playwright, which may be optional
    from auto_core.playwright import PhantomManager
except Exception:  # pragma: no cover - optional dependency may be missing
    PhantomManager = None

__all__ = ["PhantomManager"]
