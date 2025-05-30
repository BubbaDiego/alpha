import os
import json
from datetime import datetime, timezone
from tenacity import retry, stop_after_attempt, wait_exponential

# === 🔧 FLAT STRUCTURE SAFE UTILITIES ===

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_TIMER_CONFIG = os.path.join(BASE_DIR, "config", "timer_config.json")

def retry_on_locked():
    def wrapper(func):
        return func
    return wrapper


# === ⏱️ TimerConfig Class ===

class TimerConfig:
    def __init__(self, path=None):
        self.path = path or DEFAULT_TIMER_CONFIG
        self._cache = None

    def load(self) -> dict:
        if self._cache is None:
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
            except Exception as e:
                print(f"[TimerConfig] load error: {e}")
                self._cache = {}
        return self._cache

    def save(self) -> None:
        tmp = self.path + '.tmp'
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, indent=2)
            os.replace(tmp, self.path)
            self._cache = None
        except Exception as e:
            print(f"[TimerConfig] save error: {e}")

    def get(self, key, default=None):
        return self.load().get(key, default)

    def set(self, key, value):
        cfg = self.load()
        cfg[key] = value
        self.save()


# === 🧪 EXPORTED HELPERS ===

@retry_on_locked()
def load_timer_config(path=None):
    return TimerConfig(path).load()

def update_timer_config(config_data, path=None):
    tc = TimerConfig(path)
    tc._cache = config_data
    tc.save()


# === 🌐 HTTP Client With Retry ===

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def call_endpoint(url: str, method: str = "get", verify: bool = True, **kwargs) -> dict:
    import requests
    func = getattr(requests, method.lower())
    resp = func(url, timeout=30, verify=verify, **kwargs)
    resp.raise_for_status()
    return resp.json()
