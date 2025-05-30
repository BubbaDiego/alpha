import json
from typing import List

from .context_loader import get_context_messages


def create_gpt_context_service(core, request_type: str, instructions: str = "") -> List[dict]:
    """Return chat messages for GPT based on the request type.

    Parameters
    ----------
    core : object
        Instance providing ``build_payload`` for analysis requests.
    request_type : str
        Type of request, e.g. ``"analysis"`` or ``"portfolio"``.
    instructions : str, optional
        Optional instructions for GPT.
    """
    if request_type == "analysis":
        payload = core.build_payload(instructions)
        return [
            {"role": "system", "content": "You are a portfolio analysis assistant."},
            {"role": "user", "content": json.dumps(payload)},
        ]

    if request_type == "portfolio":
        messages = [
            {"role": "system", "content": "You are a portfolio analysis assistant."}
        ]
        messages.extend(get_context_messages())
        messages.append({"role": "user", "content": instructions or "Provide a portfolio analysis summary."})
        return messages

    raise ValueError(f"Unsupported request type: {request_type}")
