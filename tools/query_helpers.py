from __future__ import annotations

from typing import Any

from core.db import get_connection


def fetch_one_dict(sql: str, params: list[Any] | None = None) -> dict[str, Any] | None:
    conn = get_connection()
    rows = conn.execute(sql, params or []).fetchall()
    columns = [column[0] for column in conn.description]

    if not rows:
        return None

    return dict(zip(columns, rows[0]))


def fetch_all_dicts(sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(sql, params or []).fetchall()
    columns = [column[0] for column in conn.description]

    if not rows:
        return []

    return [dict(zip(columns, row)) for row in rows]
