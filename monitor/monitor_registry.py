# monitor/core/monitor_registry.py

class MonitorRegistry:
    """
    Holds and manages all monitor instances.
    """
    def __init__(self):
        self.monitors = {}

    def register(self, name: str, monitor):
        self.monitors[name] = monitor

    def get(self, name: str):
        return self.monitors.get(name)

    def get_all_monitors(self):
        return self.monitors
