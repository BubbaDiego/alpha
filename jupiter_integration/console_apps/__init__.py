"""Console application entry points for Jupiter integration."""

from .phantom_console_app import main as phantom_main
from .solflare_console_app import main as solflare_main

__all__ = ["phantom_main", "solflare_main"]

