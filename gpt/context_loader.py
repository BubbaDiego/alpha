import json
import logging
import os

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _load_json(name: str) -> dict:
    """Load a JSON file from the data directory."""
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        logger.debug("Context file missing: %s", path)
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as ex:  # pragma: no cover - defensive
        logger.error("Failed to load %s: %s", name, ex)
        return {}


def get_context_data() -> dict:
    """Return dict of loaded context files by name."""
    files = [
        "gpt_meta_input.json",
        "gpt_definitions_input.json",
        "gpt_alert_thresholds_input.json",
        "gpt_module_references.json",
        "snapshot_sample.json",
    ]
    data = {}
    for fname in files:
        content = _load_json(fname)
        if content:
            data[fname] = content
    return data


def get_context_messages() -> list:
    """Return a list of system messages for ChatGPT."""
    messages = []
    for content in get_context_data().values():
        messages.append({"role": "system", "content": json.dumps(content)})
    return messages
