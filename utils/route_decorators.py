from functools import wraps
from flask import request
from core.logging import log

def route_log_alert(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        method = request.method
        path = request.path
        ip = request.remote_addr or "unknown"
        agent = request.headers.get("User-Agent", "N/A")[:12]  # 🔪 Trim to 25 chars
        route = f"{method} {path}"

        log.route(f"{route} :: IP={ip} :: Agent={agent}")

        try:
            result = func(*args, **kwargs)

            status = None
            if hasattr(result, "status_code"):
                status = result.status_code
            elif isinstance(result, tuple) and len(result) > 1:
                status = result[1]

            status_str = f"{status} ✅" if status and int(status) < 400 else f"{status} ❌"
            log.success(f"🌐 {route} :: STATUS={status_str}", source="Route")

            return result

        except Exception as e:
            log.error(f"🌐 {route} :: STATUS=500 ❌", source="Route")
            log.error(f"     └─ Error: {e}", source="Route")
            raise
    return wrapper
