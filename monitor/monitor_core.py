import sys
import os
from typing import Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.logging import log

# Import your monitor classes here
from monitor.price_monitor import PriceMonitor
from monitor.position_monitor import PositionMonitor
from monitor.operations_monitor import OperationsMonitor
from monitor.xcom_monitor import XComMonitor
from monitor.twilio_monitor import TwilioMonitor
# Add any new monitors here

from monitor.monitor_registry import MonitorRegistry

class MonitorCore:
    """Central controller for all registered monitors."""

    def __init__(self, registry: Optional[MonitorRegistry] = None):
        """Create the core controller.

        If ``registry`` is not supplied a new :class:`MonitorRegistry` instance
        is created and the default monitors are registered. When a registry is
        provided it is used as-is, allowing external callers to customize the
        available monitors.
        """

        self.registry = registry or MonitorRegistry()

        if registry is None:
            # Register default monitors when no custom registry is supplied
            self.registry.register("price_monitor", PriceMonitor())
            self.registry.register("position_monitor", PositionMonitor())
            self.registry.register("operations_monitor", OperationsMonitor())
            self.registry.register("xcom_monitor", XComMonitor())
            self.registry.register("twilio_monitor", TwilioMonitor())
            # Add more monitors as needed

    def run_all(self):
        """
        Run all registered monitors in sequence.
        """
        for name, monitor in self.registry.get_all_monitors().items():
            try:
                log.info(f"Running monitor: {name}", source="MonitorCore")
                monitor.run_cycle()
                log.success(f"Monitor '{name}' completed successfully.", source="MonitorCore")
            except Exception as e:
                log.error(f"Monitor '{name}' failed: {e}", source="MonitorCore")

    def run_by_name(self, name: str):
        """
        Run a specific monitor by its registered name.
        """
        monitor = self.registry.get(name)
        if monitor:
            try:
                log.info(f"Running monitor: {name}", source="MonitorCore")
                monitor.run_cycle()
                log.success(f"Monitor '{name}' completed successfully.", source="MonitorCore")
            except Exception as e:
                log.error(f"Monitor '{name}' failed: {e}", source="MonitorCore")
        else:
            log.warning(f"Monitor '{name}' not found.", source="MonitorCore")
