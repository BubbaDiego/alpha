"""Re-export :class:`JupiterPerpsFlow` from :mod:`auto_core.playwright`."""

try:  # JupiterPerpsFlow depends on Playwright, which may be optional
    from auto_core.playwright import JupiterPerpsFlow
except Exception:  # pragma: no cover - optional dependency may be missing
    JupiterPerpsFlow = None

__all__ = ["JupiterPerpsFlow"]

