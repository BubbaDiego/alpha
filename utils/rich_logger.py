import logging
import json
import time
import inspect
from datetime import datetime
from typing import Dict, List, Optional
try:
    from rich.logging import RichHandler  # type: ignore
except Exception:  # pragma: no cover - fallback for minimal env
    import logging

    class RichHandler(logging.StreamHandler):
        """Simple stand-in if rich is unavailable."""

        def __init__(self, *args, **kwargs):
            super().__init__()
            self.level_styles = {}


class ModuleFilter(logging.Filter):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def filter(self, record: logging.LogRecord) -> bool:
        module = getattr(record, "source_module", None)
        if not module:
            module = record.name.split(".")[-1]
        return self.controller._is_logging_allowed(module)


class RichLogger:
    """Wrapper around logging.Logger with colored output via Rich."""

    ICONS = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "debug": "🐞",
        "death": "💀",
        "route": "🌐",
    }

    logging_enabled = True
    module_log_control: Dict[str, bool] = {}
    group_map: Dict[str, List[str]] = {}
    group_log_control: Dict[str, bool] = {}
    timers: Dict[str, float] = {}

    def __init__(self, name: str = "cyclone") -> None:
        self.logger = logging.getLogger(name)
        handler = RichHandler(show_path=False, markup=True)
        # Force INFO messages to display in blue. Some environments render INFO
        # as red, so wrap the message in explicit markup as a fallback.
        self._info_markup = "[blue]{label}[/blue]"
        handler.addFilter(ModuleFilter(self))
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        self.logger.handlers = [handler]
        self.logger.setLevel(logging.INFO)

    # ------------------------------------------------------
    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def _get_caller_module(cls) -> str:
        stack = inspect.stack()
        for frame in stack[2:]:
            module = inspect.getmodule(frame[0])
            if module and hasattr(module, "__name__"):
                mod_name = module.__name__
                if mod_name == "__main__":
                    filename = frame.filename.split("/")[-1]
                    return filename.replace(".py", "")
                return mod_name.split(".")[-1]
            elif hasattr(frame, "filename"):
                filename = frame.filename.split("/")[-1]
                return filename.replace(".py", "")
        return "unknown"

    # ------------------------------------------------------
    @classmethod
    def _is_logging_allowed(cls, module: str) -> bool:
        if not cls.logging_enabled:
            return False
        if module in cls.module_log_control:
            return cls.module_log_control[module]
        for group, modules in cls.group_map.items():
            if module in modules and not cls.group_log_control.get(group, True):
                return False
        for prefix, enabled in cls.module_log_control.items():
            if not enabled and module.startswith(prefix):
                return False
        return True

    # ------------------------------------------------------
    def _log(self, level: int, icon_key: str, message: str, source: Optional[str] = None, payload: Optional[Dict] = None):
        module = source or self._get_caller_module()
        timestamp = self._timestamp()
        icon = self.ICONS.get(icon_key, "")
        label = f"{icon} {message} :: [{module}] @ {timestamp}"
        if level == logging.INFO:
            # Wrap INFO lines in explicit blue markup so they never inherit
            # previous error colors.
            label = self._info_markup.format(label=label)

        inline_payload = ""
        if payload:
            try:
                if all(isinstance(v, (str, int, float, bool, type(None))) for v in payload.values()):
                    inline_payload = " → " + ", ".join(f"{k}: {v}" for k, v in payload.items())
                else:
                    pretty = json.dumps(payload, indent=2, default=str)
                    inline_payload = "\n" + "\n".join("    " + line for line in pretty.splitlines())
            except Exception as e:
                inline_payload = f" [payload error: {e}]"

        self.logger.log(level, label + inline_payload, extra={"source_module": module}, stacklevel=2)

    # Public API ------------------------------------------------------
    def info(self, message: str, source: Optional[str] = None, payload: Optional[Dict] = None):
        self._log(logging.INFO, "info", message, source, payload)

    def success(self, message: str, source: Optional[str] = None, payload: Optional[Dict] = None):
        self._log(logging.INFO, "success", message, source, payload)

    def warning(self, message: str, source: Optional[str] = None, payload: Optional[Dict] = None):
        self._log(logging.WARNING, "warning", message, source, payload)

    def error(self, message: str, source: Optional[str] = None, payload: Optional[Dict] = None):
        self._log(logging.ERROR, "error", message, source, payload)

    def debug(self, message: str, source: Optional[str] = None, payload: Optional[Dict] = None):
        self._log(logging.DEBUG, "debug", message, source, payload)

    def critical(self, message: str, source: Optional[str] = None, payload: Optional[Dict] = None):
        """Log a critical message. Uses the error icon with CRITICAL level."""
        self._log(logging.CRITICAL, "error", message, source, payload)

    def death(self, message: str, source: Optional[str] = None, payload: Optional[Dict] = None):
        self._log(logging.CRITICAL, "death", message, source, payload)

    def route(self, message: str, source: Optional[str] = None, payload: Optional[Dict] = None):
        self._log(logging.INFO, "route", message, source, payload)

    def banner(self, message: str):
        print("\n" + "=" * 60)
        print(message.center(60))
        print("=" * 60 + "\n")

    # Timer utilities ------------------------------------------------
    def start_timer(self, label: str):
        self.timers[label] = time.time()

    def end_timer(self, label: str, source: Optional[str] = None):
        if label not in self.timers:
            self.warning(f"No timer started for label '{label}'", source)
            return
        elapsed = time.time() - self.timers.pop(label)
        self.success(f"Timer '{label}' completed in {elapsed:.2f}s", source)

    # Suppression controls -------------------------------------------
    @classmethod
    def silence_module(cls, module: str):
        cls.module_log_control[module] = False

    @classmethod
    def enable_module(cls, module: str):
        cls.module_log_control[module] = True

    @classmethod
    def assign_group(cls, group: str, modules: List[str]):
        cls.group_map[group] = modules

    @classmethod
    def silence_group(cls, group: str):
        cls.group_log_control[group] = False

    @classmethod
    def enable_group(cls, group: str):
        cls.group_log_control[group] = True

    @classmethod
    def silence_prefix(cls, prefix: str):
        cls.silence_module(prefix)

    @classmethod
    def silence_all(cls):
        cls.logging_enabled = False

    @classmethod
    def enable_all(cls):
        cls.logging_enabled = True


    def init_status(self):
        """Log the current logger configuration and suppression status."""
        muted = [k for k, v in self.module_log_control.items() if not v]
        enabled = [k for k, v in self.module_log_control.items() if v]
        msg = "\n"
        if muted:
            msg += f"    🔒 Muted Modules:      {', '.join(muted)}\n"
        if enabled:
            msg += f"    🔊 Enabled Modules:    {', '.join(enabled)}\n"

        if self.group_map:
            msg += "    🧠 Groups:\n"
            for group, modules in self.group_map.items():
                msg += f"        {group:<10} ➜ {', '.join(modules)}\n"
        self.info("🧩 RichLogger initialized.", source="Logger")
        print(msg.strip())

    def hijack_logger(self, target_logger_name: str):
        def handler(record: logging.LogRecord):
            self.info(record.getMessage(), source=target_logger_name)

        h = logging.Handler()
        h.emit = handler
        hijacked = logging.getLogger(target_logger_name)
        hijacked.handlers = [h]
        hijacked.propagate = False
        hijacked.setLevel(logging.INFO)
        self.info(f"🕵️ Logger '{target_logger_name}' hijacked", source="LoggerControl")

    def print_dashboard_link(self, host: str = "127.0.0.1", port: int = 5001, route: str = "/dashboard"):
        """Print hyperlinks for both localhost and LAN dashboard URLs."""
        from utils.net_utils import get_local_ip

        url_local = f"http://{host}:{port}{route}"
        lan_ip = get_local_ip()
        url_lan = f"http://{lan_ip}:{port}{route}"

        try:
            hyperlink_local = f"\033]8;;{url_local}\033\\🔗 Open Sonic Dashboard\033]8;;\033\\"
            hyperlink_lan = f"\033]8;;{url_lan}\033\\🔗 Open Sonic Dashboard (LAN)\033]8;;\033\\"
            print(f"\n🌐 Sonic Dashboard: {hyperlink_local}")
            if lan_ip != host:
                print(f"🌐 Sonic Dashboard: {hyperlink_lan}")
            print()
        except Exception:
            # Fallback to plain URL if ANSI hyperlinks aren't supported
            print(f"\n🌐 Sonic Dashboard: {url_local}")
            if lan_ip != host:
                print(f"🌐 Sonic Dashboard: {url_lan}")
            print()
