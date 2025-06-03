from datetime import datetime


def short_datetime(value):
    """Format timestamps like '2025-06-03T13:06:03.968905' as '3:06PM 6/3/25'."""
    if not value:
        return ""
    try:
        if isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(float(value))
        else:
            try:
                dt = datetime.fromisoformat(str(value))
            except ValueError:
                dt = datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
        formatted = dt.strftime("%I:%M%p %m/%d/%y")
        if formatted.startswith("0"):
            formatted = formatted[1:]
        formatted = formatted.replace("/0", "/")
        return formatted
    except Exception:
        return value

