from __future__ import annotations

import json
from typing import Any

from core.agent import create_agent
from core.session_context import get_session_snapshot, load_session_snapshot, reset_session
from core.session_store import load_remote_session, save_remote_session


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

    reset_session()
    load_session_snapshot(load_remote_session(session_id))

    agent = create_agent()
    response = agent(message)
    save_remote_session(session_id, get_session_snapshot())

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
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
