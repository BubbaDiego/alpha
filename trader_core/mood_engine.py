from typing import Dict

def evaluate_mood(heat_index: float, mood_map: Dict[str, str]) -> str:
    """Return a mood string given the heat index and persona mood map."""
    if heat_index >= 60:
        return mood_map.get("market_crash", "chaotic")
    if heat_index >= 40:
        return mood_map.get("high_heat", "nervous")
    if heat_index <= 10:
        return mood_map.get("low_balance", "calm")
    return mood_map.get("stable", "neutral")
