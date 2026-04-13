from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import boto3
from botocore.exceptions import ClientError

from core.runtime_config import get_aws_region, get_sessions_table, is_aws_env


SESSION_TTL_HOURS = 12


def load_remote_session(session_id: str) -> dict[str, Any] | None:
    if not is_aws_env():
        return None

    table = get_sessions_table().strip()
    if not table or not session_id.strip():
        return None

    try:
        response = _get_table().get_item(Key={"session_id": session_id.strip()})
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "ResourceNotFoundException":
            return None
        raise

    item = response.get("Item")
    if not item:
        return None

    payload = item.get("payload")
    if not isinstance(payload, dict):
        return None

    return _deserialize(payload)


def save_remote_session(session_id: str, snapshot: dict[str, Any]) -> None:
    if not is_aws_env():
        return

    table = get_sessions_table().strip()
    if not table or not session_id.strip():
        return

    now = datetime.now(timezone.utc)
    expires_at = int((now + timedelta(hours=SESSION_TTL_HOURS)).timestamp())

    try:
        _get_table().put_item(
            Item={
                "session_id": session_id.strip(),
                "updated_at": now.isoformat(),
                "expires_at": expires_at,
                "payload": _serialize(snapshot),
            }
        )
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "ResourceNotFoundException":
            return
        raise


def delete_remote_session(session_id: str) -> None:
    if not is_aws_env():
        return

    table = get_sessions_table().strip()
    if not table or not session_id.strip():
        return

    try:
        _get_table().delete_item(Key={"session_id": session_id.strip()})
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "ResourceNotFoundException":
            return
        raise


def _get_table():
    dynamodb = boto3.resource("dynamodb", region_name=get_aws_region())
    return dynamodb.Table(get_sessions_table().strip())


def _serialize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _serialize(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return Decimal(str(value))

    return repr(value)


def _deserialize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _deserialize(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_deserialize(item) for item in value]
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)

    return deepcopy(value)
