from __future__ import annotations

import json
from typing import Any

from core.agent import create_agent


def _normalize_request_body(event: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(event, dict):
        return {}

    body = event.get("body", {})
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return {}

    if not isinstance(body, dict):
        return {}

    return body


def lambda_handler(event: dict[str, Any] | None, context: Any) -> dict[str, Any]:
    body = _normalize_request_body(event)

    message = str(body.get("message", "")).strip()
    session_id = str(body.get("session_id", "default-session")).strip() or "default-session"

    agent = create_agent()
    response = agent(message)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(
            {
                "ok": True,
                "session_id": session_id,
                "message": message,
                "response": response.content,
            },
            ensure_ascii=False,
        ),
    }
