from __future__ import annotations

from core.session_context import add_tool_trace
from tools.base_tool_models import ToolResult
from tools.query_helpers import fetch_all_dicts, fetch_one_dict


def list_order_items(order_id: str) -> ToolResult:
    normalized_order_id = (order_id or "").strip()

    if not normalized_order_id:
        result = ToolResult(
            ok=False,
            tool_name="list_order_items",
            error="order_id vacío",
        )
        add_tool_trace("list_order_items", {"order_id": normalized_order_id}, result.to_dict())
        return result

    rows = fetch_all_dicts(
        """
        SELECT
            oi.item_id,
            oi.order_id,
            oi.product_id,
            oi.qty,
            oi.unit_price,
            oi.warranty_expires_at,
            oi.return_deadline,
            oi.item_status,
            p.name AS product_name,
            p.return_days,
            p.is_final_sale,
            p.warranty_months
        FROM order_items oi
        LEFT JOIN products p
            ON oi.product_id = p.product_id
        WHERE CAST(oi.order_id AS VARCHAR) = ?
        ORDER BY oi.item_id ASC
        """,
        [normalized_order_id],
    )

    if not rows:
        result = ToolResult(
            ok=False,
            tool_name="list_order_items",
            error="No se encontraron ítems para ese pedido",
            data={"order_id": normalized_order_id},
        )
        add_tool_trace("list_order_items", {"order_id": normalized_order_id}, result.to_dict())
        return result

    result = ToolResult(
        ok=True,
        tool_name="list_order_items",
        data={
            "order_id": normalized_order_id,
            "items_count": len(rows),
            "items": rows,
        },
    )
    add_tool_trace("list_order_items", {"order_id": normalized_order_id}, result.to_dict())
    return result


def get_order_item_by_product(order_id: str, product_id: str) -> ToolResult:
    normalized_order_id = (order_id or "").strip()
    normalized_product_id = (product_id or "").strip()

    if not normalized_order_id or not normalized_product_id:
        result = ToolResult(
            ok=False,
            tool_name="get_order_item_by_product",
            error="order_id o product_id vacío",
            data={
                "order_id": normalized_order_id,
                "product_id": normalized_product_id,
            },
        )
        add_tool_trace(
            "get_order_item_by_product",
            {"order_id": normalized_order_id, "product_id": normalized_product_id},
            result.to_dict(),
        )
        return result

    row = fetch_one_dict(
        """
        SELECT
            oi.item_id,
            oi.order_id,
            oi.product_id,
            oi.qty,
            oi.unit_price,
            oi.warranty_expires_at,
            oi.return_deadline,
            oi.item_status,
            p.name AS product_name,
            p.return_days,
            p.is_final_sale,
            p.warranty_months
        FROM order_items oi
        LEFT JOIN products p
            ON oi.product_id = p.product_id
        WHERE CAST(oi.order_id AS VARCHAR) = ?
          AND CAST(oi.product_id AS VARCHAR) = ?
        LIMIT 1
        """,
        [normalized_order_id, normalized_product_id],
    )

    if not row:
        result = ToolResult(
            ok=False,
            tool_name="get_order_item_by_product",
            error="No se encontró ese producto dentro del pedido",
            data={
                "order_id": normalized_order_id,
                "product_id": normalized_product_id,
            },
        )
        add_tool_trace(
            "get_order_item_by_product",
            {"order_id": normalized_order_id, "product_id": normalized_product_id},
            result.to_dict(),
        )
        return result

    result = ToolResult(
        ok=True,
        tool_name="get_order_item_by_product",
        data=row,
    )
    add_tool_trace(
        "get_order_item_by_product",
        {"order_id": normalized_order_id, "product_id": normalized_product_id},
        result.to_dict(),
    )
    return result