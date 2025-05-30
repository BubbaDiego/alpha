"""Console logging utilities with color and contextual control.

This module exposes the :class:`ConsoleLogger` which prints color coded
messages and allows modules to be muted or enabled.  v2 introduces a
``highlight`` method for eye catching output and context managers for
temporarily overriding module or group logging settings.
"""

import json
import time
import inspect
from datetime import datetime
from contextlib import contextmanager



class ConsoleLogger:
    logging_enabled = True
    module_log_control = {}
    group_map = {}
    group_log_control = {}
    timers = {}

    debug_trace_enabled = False
    trace_modules = set()

    COLORS = {
        "info": "\033[94m",        # 🔵 Light blue
        "success": "\033[92m",     # 🟢 Green
        "warning": "\033[93m",     # 🟡 Yellow
        "error": "\033[91m",       # 🔴 Red
        "confidence": "\033[96m",  # 🧊 Cyan
        "debug": "\033[38;5;208m", # 🧡 Orange-ish
        "death": "\033[95m",       # 💀 Purple-pink
        "highlight": "\033[38;5;99m", # ✨ Bright pink
        "endc": "\033[0m",         # ⛔ Reset
    }

    ICONS = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "confidence": "🐻",
        "debug": "🐞",
        "death": "💀",
        "highlight": "✨",
    }

    @staticmethod
    def _timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def _get_caller_module(cls):
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

    @classmethod
    def _is_logging_allowed(cls, module: str) -> bool:
        if not cls.logging_enabled:
            return False

        if module in cls.module_log_control:
            return cls.module_log_control[module]

        for group, modules in cls.group_map.items():
            if module in modules:
                if not cls.group_log_control.get(group, True):
                    return False

        for prefix in cls.module_log_control:
            if not cls.module_log_control[prefix] and module.startswith(prefix):
                return False

        return True

    @classmethod
    def _print(cls, level: str, message: str, source: str = None, payload: dict = None):
        caller_module = cls._get_caller_module()
        effective_source = source or caller_module

        if not cls._is_logging_allowed(effective_source):
            return

        if cls.debug_trace_enabled and (
            not cls.trace_modules or effective_source in cls.trace_modules
        ):
            print(f"[🧠 LOGGING DEBUG] caller='{caller_module}' source='{source}' → effective='{effective_source}'")
            print("                └─ FINAL DECISION: ✅ allowed")

        icon = cls.ICONS.get(level, cls.ICONS.get("info", ""))
        start_reset = cls.COLORS["endc"]
        # Only render messages in red when actually logging an error.
        if level == "error":
            color = cls.COLORS["error"]
            endc = cls.COLORS["endc"]
        else:
            color = ""
            endc = ""
        timestamp = cls._timestamp()
        label = f"{icon} {message} :: [{effective_source}] @ {timestamp}"

        inline_payload = ""
        if payload:
            try:
                if all(isinstance(v, (str, int, float, bool, type(None))) for v in payload.values()):
                    inline_payload = " → " + ", ".join(f"{k}: {v}" for k, v in payload.items())
                else:
                    try:
                        pretty = json.dumps(payload, indent=2, default=str)
                        inline_payload = "\n" + "\n".join("    " + line for line in pretty.splitlines())
                    except Exception as je:
                        inline_payload = f" [payload JSON serialization failed: {je}]"
            except Exception as e:
                inline_payload = f" [payload processing error: {e}]"

        # Always start with a reset code so any previous colored output doesn't
        # bleed into the new log line.
        print(f"{start_reset}{color}{label}{inline_payload}{endc}")

    @classmethod
    def info(cls, message: str, source: str = None, payload: dict = None):
        cls._print("info", message, source, payload)

    @classmethod
    def success(cls, message: str, source: str = None, payload: dict = None):
        cls._print("success", message, source, payload)

    @classmethod
    def warning(cls, message: str, source: str = None, payload: dict = None):
        cls._print("warning", message, source, payload)

    @classmethod
    def error(cls, message: str, source: str = None, payload: dict = None):
        cls._print("error", message, source, payload)

    @classmethod
    def debug(cls, message: str, source: str = None, payload: dict = None):
        cls._print("debug", message, source, payload)

    @classmethod
    def death(cls, message: str, source: str = None, payload: dict = None):
        cls._print("death", message, source, payload)

    @classmethod
    def highlight(cls, message: str, source: str = None, payload: dict = None):
        """Print a message in a distinctive highlight color."""
        cls._print("highlight", message, source, payload)

    @classmethod
    def start_timer(cls, label: str):
        cls.timers[label] = time.time()

    @classmethod
    def end_timer(cls, label: str, source: str = None):
        if label not in cls.timers:
            cls.warning(f"No timer started for label '{label}'", source)
            return
        elapsed = time.time() - cls.timers.pop(label)
        cls.success(f"Timer '{label}' completed in {elapsed:.2f}s", source)

    @classmethod
    def silence_module(cls, module: str):
        cls.module_log_control[module] = False

    @classmethod
    def enable_module(cls, module: str):
        cls.module_log_control[module] = True

    @classmethod
    def assign_group(cls, group: str, modules: list):
        cls.group_map[group] = modules

    @classmethod
    def silence_group(cls, group: str):
        cls.group_log_control[group] = False

    @classmethod
    def enable_group(cls, group: str):
        cls.group_log_control[group] = True

    @classmethod
    @contextmanager
    def temporary_module(cls, module: str, enabled: bool):
        """Temporarily override logging state for ``module``."""
        previous = cls.module_log_control.get(module, True)
        cls.module_log_control[module] = enabled
        try:
            yield
        finally:
            cls.module_log_control[module] = previous

    @classmethod
    @contextmanager
    def temporary_group(cls, group: str, enabled: bool):
        """Temporarily override logging state for ``group``."""
        previous = cls.group_log_control.get(group, True)
        cls.group_log_control[group] = enabled
        try:
            yield
        finally:
            cls.group_log_control[group] = previous

    @classmethod
    def set_trace_modules(cls, modules: list):
        cls.trace_modules = set(modules)
        cls.debug_trace_enabled = True

    @classmethod
    def silence_prefix(cls, prefix: str):
        cls.silence_module(prefix)

    @classmethod
    def silence_all(cls):
        cls.logging_enabled = False

    @classmethod
    def enable_all(cls):
        cls.logging_enabled = True

    @classmethod
    def init_status(cls):
        muted = [k for k, v in cls.module_log_control.items() if not v]
        enabled = [k for k, v in cls.module_log_control.items() if v]

        msg = "\n"
        if muted:
            msg += f"    🔒 Muted Modules:      {', '.join(muted)}\n"
        if enabled:
            msg += f"    🔊 Enabled Modules:    {', '.join(enabled)}\n"
        if cls.group_map:
            msg += "    🧠 Groups:\n"
            for group, modules in cls.group_map.items():
                msg += f"        {group:<10} ➜ {', '.join(modules)}\n"

        cls.info("🧩 ConsoleLogger initialized.", source="Logger")
        print(msg.strip())

    @classmethod
    def debug_module(cls):
        mod = cls._get_caller_module()
        cls.debug(f"Detected module: {mod}", source="Logger")

    @classmethod
    def banner(cls, message: str):
        print("\n" + "=" * 60)
        print(f"🚀 {message.center(50)} 🚀")
        print("=" * 60 + "\n")

    @classmethod
    def hijack_logger(cls, target_logger_name: str):
        import logging

        def handler(record):
            mod = target_logger_name
            if cls._is_logging_allowed(mod):
                cls.info(record.getMessage(), source=mod)

        h = logging.StreamHandler()
        h.emit = handler
        hijacked_logger = logging.getLogger(target_logger_name)
        hijacked_logger.handlers = [h]
        hijacked_logger.propagate = False
        hijacked_logger.setLevel(logging.INFO)

        cls.info(f"🕵️ Logger '{target_logger_name}' has been hijacked by ConsoleLogger.", source="LoggerControl")

    @classmethod
    def print_dashboard_link(cls, host="127.0.0.1", port=5001, route="/dashboard"):
        """Display both localhost and LAN links to the dashboard."""
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
            print(f"\n🌐 Sonic Dashboard: {url_local}")
            if lan_ip != host:
                print(f"🌐 Sonic Dashboard: {url_lan}")
            print()

    @classmethod
    def route(cls, message: str, source: str = None, payload: dict = None):
        caller_module = cls._get_caller_module()
        effective_source = source or caller_module

        CYAN = "\033[96m"
        ENDC = "\033[0m"
        ICON = "🌐"
        timestamp = cls._timestamp()
        label = f"{ICON} {message} :: [{effective_source}] @ {timestamp}"

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

        print(f"{CYAN}{label}{inline_payload}{ENDC}")
