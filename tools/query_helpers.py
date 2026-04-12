from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any

from core.db import get_connection


def _normalize_params(params: list[Any] | None = None) -> tuple[Any, ...]:
    return tuple(params or [])


@lru_cache(maxsize=256)
def _fetch_one_dict_cached(sql: str, params: tuple[Any, ...]) -> dict[str, Any] | None:
    conn = get_connection()
    rows = conn.execute(sql, list(params)).fetchall()
    columns = [column[0] for column in conn.description]

    if not rows:
        return None

    return dict(zip(columns, rows[0]))


def fetch_one_dict(sql: str, params: list[Any] | None = None) -> dict[str, Any] | None:
    row = _fetch_one_dict_cached(sql, _normalize_params(params))
    return deepcopy(row) if row is not None else None


@lru_cache(maxsize=256)
def _fetch_all_dicts_cached(sql: str, params: tuple[Any, ...]) -> tuple[dict[str, Any], ...]:
    conn = get_connection()
    rows = conn.execute(sql, list(params)).fetchall()
    columns = [column[0] for column in conn.description]

    if not rows:
        return ()

    return tuple(dict(zip(columns, row)) for row in rows)


def fetch_all_dicts(sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
    rows = _fetch_all_dicts_cached(sql, _normalize_params(params))
    return deepcopy(list(rows))
