from __future__ import annotations

import re

from core.session_context import add_tool_trace, set_session_customer
from tools.base_tool_models import ToolResult
from tools.query_helpers import fetch_one_dict


def _normalize_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def _normalize_phone(value: str) -> str:
    digits = _normalize_digits(value)
    if len(digits) >= 10:
        return digits[-10:]
    return digits


def verify_customer_by_dni(dni: str) -> ToolResult:
    normalized_dni = _normalize_digits(dni)

    if not normalized_dni:
        result = ToolResult(
            ok=False,
            tool_name="verify_customer_by_dni",
            error="dni vacío",
        )
        add_tool_trace("verify_customer_by_dni", {"dni": normalized_dni}, result.to_dict())
        return result

    row = fetch_one_dict(
        """
        SELECT
            customer_id,
            dni,
            phone,
            name,
            last_name1,
            last_name2,
            account_status,
            is_premium
        FROM customers
        WHERE regexp_replace(CAST(dni AS VARCHAR), '[^0-9]', '', 'g') = ?
        LIMIT 1
        """,
        [normalized_dni],
    )

    if not row:
        result = ToolResult(
            ok=False,
            tool_name="verify_customer_by_dni",
            error="Cliente no encontrado con ese dni",
            data={"dni": normalized_dni},
        )
        add_tool_trace("verify_customer_by_dni", {"dni": normalized_dni}, result.to_dict())
        return result

    display_name = " ".join(
        part.strip()
        for part in [
            str(row.get("name", "") or ""),
            str(row.get("last_name1", "") or ""),
            str(row.get("last_name2", "") or ""),
        ]
        if part and part.strip()
    ).strip()

    set_session_customer(row["customer_id"], display_name or f"Cliente {row['customer_id']}")

    result = ToolResult(
        ok=True,
        tool_name="verify_customer_by_dni",
        data=row,
    )
    add_tool_trace("verify_customer_by_dni", {"dni": normalized_dni}, result.to_dict())
    return result


def verify_customer_by_phone(phone: str) -> ToolResult:
    normalized_phone = _normalize_phone(phone)

    if not normalized_phone:
        result = ToolResult(
            ok=False,
            tool_name="verify_customer_by_phone",
            error="phone vacío",
        )
        add_tool_trace("verify_customer_by_phone", {"phone": normalized_phone}, result.to_dict())
        return result

    row = fetch_one_dict(
        """
        SELECT
            customer_id,
            dni,
            phone,
            name,
            last_name1,
            last_name2,
            account_status,
            is_premium
        FROM customers
        WHERE right(regexp_replace(CAST(phone AS VARCHAR), '[^0-9]', '', 'g'), 10) = ?
        LIMIT 1
        """,
        [normalized_phone],
    )

    if not row:
        result = ToolResult(
            ok=False,
            tool_name="verify_customer_by_phone",
            error="Cliente no encontrado con ese phone",
            data={"phone": normalized_phone},
        )
        add_tool_trace("verify_customer_by_phone", {"phone": normalized_phone}, result.to_dict())
        return result

    display_name = " ".join(
        part.strip()
        for part in [
            str(row.get("name", "") or ""),
            str(row.get("last_name1", "") or ""),
            str(row.get("last_name2", "") or ""),
        ]
        if part and part.strip()
    ).strip()

    set_session_customer(row["customer_id"], display_name or f"Cliente {row['customer_id']}")

    result = ToolResult(
        ok=True,
        tool_name="verify_customer_by_phone",
        data=row,
    )
    add_tool_trace("verify_customer_by_phone", {"phone": normalized_phone}, result.to_dict())
    return result
