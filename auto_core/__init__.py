try:  # AutoCore requires Playwright
    from .auto_core import AutoCore
    from .console_apps import phantom_workflow
except Exception:  # pragma: no cover - optional dependency may be missing
    AutoCore = None
    phantom_workflow = None

try:  # PhantomManager requires Playwright
    from .phantom_manager import PhantomManager
except Exception:  # pragma: no cover - optional dependency may be missing
    PhantomManager = None

__all__ = ["AutoCore", "phantom_workflow", "PhantomManager"]
