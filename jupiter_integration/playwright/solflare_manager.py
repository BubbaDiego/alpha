"""Re-export :class:`SolflareManager` from :mod:`auto_core.playwright`."""

try:  # SolflareManager depends on Playwright, which may be optional
    from auto_core.playwright import SolflareManager
except Exception:  # pragma: no cover - optional dependency may be missing
    SolflareManager = None

__all__ = ["SolflareManager"]

