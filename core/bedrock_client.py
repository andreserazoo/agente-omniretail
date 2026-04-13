from __future__ import annotations

import json
import re
from typing import Any

import boto3
from botocore.config import Config

from core.runtime_config import get_aws_region, get_bedrock_model_id


DEFAULT_SYSTEM_PROMPT = (
    "Eres el asistente de OmniRetail. "
    "Responde en español claro y útil. "
    "No inventes datos de pedidos, clientes, productos o políticas. "
    "No uses emojis. "
    "No uses markdown salvo listas simples si son realmente necesarias. "
    "Si no tienes datos confirmados, dilo de forma explícita."
)


def is_bedrock_configured() -> bool:
    return bool(get_bedrock_model_id().strip())


def generate_bedrock_text(
    user_message: str,
    *,
    system_prompt: str | None = None,
    max_tokens: int = 250,
    temperature: float = 0.2,
    top_p: float = 0.9,
) -> str | None:
    model_id = get_bedrock_model_id().strip()
    if not model_id:
        return None

    client = boto3.client(
        "bedrock-runtime",
        region_name=get_aws_region(),
        config=Config(read_timeout=60),
    )

    request_body: dict[str, Any] = {
        "messages": [
            {
                "role": "user",
                "content": [{"text": (user_message or "").strip()}],
            }
        ],
        "system": [{"text": (system_prompt or DEFAULT_SYSTEM_PROMPT).strip()}],
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": temperature,
            "topP": top_p,
        },
    }

    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body),
    )
    response_body = json.loads(response["body"].read())

    content_blocks = (
        response_body.get("output", {})
        .get("message", {})
        .get("content", [])
    )

    parts: list[str] = []
    for block in content_blocks:
        text = block.get("text")
        if isinstance(text, str) and text.strip():
            parts.append(text.strip())

    final_text = "\n".join(parts).strip()
    return _sanitize_model_text(final_text) or None


def _sanitize_model_text(text: str) -> str:
    cleaned = (text or "").strip()
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

    # Remove common markdown decoration while keeping readable text.
    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.replace("__", "")
    cleaned = re.sub(r"`([^`]*)`", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*\n]+)\*", r"\1", cleaned)

    # Keep only readable characters expected in Spanish plain text.
    cleaned = re.sub(r"[^\x00-\x7FáéíóúÁÉÍÓÚñÑüÜ¿?¡!.,:;()/%\- \n]", "", cleaned)

    # Normalize whitespace and reduce overly spaced output.
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r" ?\n ?", "\n", cleaned)

    # Avoid unfinished endings that look visually broken.
    cleaned = cleaned.rstrip(" \"'*-")
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."

    return cleaned.strip()
