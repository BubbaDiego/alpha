
from importlib import import_module
import sys

# Alias for backward compatibility
models = import_module('.models_core', __name__)
sys.modules[__name__ + '.models'] = models

__all__ = []  # package exports handled by submodules
