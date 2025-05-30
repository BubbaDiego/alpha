import os
import logging
from flask import Blueprint, render_template, request, jsonify
try:  # pragma: no cover - optional dependency
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore
from dotenv import load_dotenv

from .context_loader import get_context_messages

# Load environment variables from .env if present
load_dotenv()

logger = logging.getLogger("ChatGPTBP")
logger.setLevel(logging.DEBUG)

# Instantiate the OpenAI client using API key from env.
# Prefer the new ``OPENAI_API_KEY`` variable but fall back to ``OPEN_AI_KEY``
# for backward compatibility.
api_key = (os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_KEY") or "").strip()
if not api_key or OpenAI is None:
    logger.warning(
        "OpenAI client disabled: package missing or API key not configured"
    )
    client = None
else:
    client = OpenAI(api_key=api_key)

# Default model used for chat completions.
MODEL_NAME = "gpt-3.5-turbo"

chat_gpt_bp = Blueprint(
    "chat_gpt_bp",
    __name__,
    url_prefix="/GPT",
    template_folder="../templates",
)

@chat_gpt_bp.route("/chat", methods=["GET"])
def chat():
    """Render the ChatGPT interface."""
    logger.debug("GET /chat - Rendering chat interface.")
    if client is None:
        logger.debug("OpenAI client not configured; service unavailable.")
        return jsonify({"error": "OpenAI API key not configured"}), 503
    return render_template("chat_gpt.html", model_name=MODEL_NAME)


@chat_gpt_bp.route("/oracle", methods=["GET"])
def oracle_ui():
    """Render the GPT Oracle interface."""
    logger.debug("GET /oracle - Rendering oracle interface.")
    return render_template("oracle_gpt.html", model_name=MODEL_NAME)


@chat_gpt_bp.route("/chat", methods=["POST"])
def chat_post():
    """Handle ChatGPT messages and return the response."""
    logger.debug("POST /chat - Received request.")
    if client is None:
        logger.debug("OpenAI client not configured; service unavailable.")
        return jsonify({"error": "OpenAI API key not configured"}), 503
    data = request.get_json() or {}
    logger.debug(f"Request JSON: {data}")
    user_message = (data.get("message") or "").strip()
    logger.debug(f"User message: '{user_message}'")

    if not user_message:
        logger.debug("No valid message provided; returning error response.")
        return jsonify({"reply": "Please provide a valid message."}), 400

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.extend(get_context_messages())
    messages.append({"role": "user", "content": user_message})
    logger.debug(f"Sending messages to OpenAI: {messages}")

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
        )
        logger.debug("Received response from OpenAI API.")
        reply = response.choices[0].message.content.strip()
        logger.debug(f"ChatGPT reply: '{reply}'")

        usage = {}
        try:
            usage = response.usage.model_dump() if response.usage else {}
        except Exception as ex:  # pragma: no cover - defensive
            logger.debug(f"Usage parsing failed: {ex}")

        return jsonify({"reply": reply, "model": response.model, "usage": usage})
    except Exception as e:  # pragma: no cover - rely on OpenAI client
        logger.exception("OpenAI API error")
        return jsonify({"reply": f"An error occurred: {e}"}), 500

