"""Utility helpers for alert calculations."""

def calculate_threshold_progress(start, trigger, current):
    """Compute progress percentage between start and trigger."""
    try:
        if start is None:
            start = trigger if trigger is not None else 0

        if trigger != start:
            pct = ((current - start) / (trigger - start)) * 100
        elif start != 0:
            pct = (current / start) * 100
        else:
            pct = 0

        return max(min(pct, 100), -100)
    except Exception:
        return 0
