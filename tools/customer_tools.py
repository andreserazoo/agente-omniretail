from __future__ import annotations

from core.session_context import add_tool_trace
from tools.base_tool_models import ToolResult
from tools.query_helpers import fetch_all_dicts


def list_customer_orders(customer_id: str) -> ToolResult:
    normalized_customer_id = (customer_id or "").strip()

    if not normalized_customer_id:
        result = ToolResult(
            ok=False,
            tool_name="list_customer_orders",
            error="customer_id vacío",
        )
        add_tool_trace("list_customer_orders", {"customer_id": normalized_customer_id}, result.to_dict())
        return result

    rows = fetch_all_dicts(
        """
        SELECT
            order_id,
            customer_id,
            order_date,
            status,
            subtotal,
            shipping_cost,
            tax,
            total_amount,
            delivery_method,
            payment_method
        FROM orders
        WHERE CAST(customer_id AS VARCHAR) = ?
        ORDER BY order_date DESC
        """,
        [normalized_customer_id],
    )

    if not rows:
        result = ToolResult(
            ok=False,
            tool_name="list_customer_orders",
            error="No se encontraron pedidos para ese customer_id",
            data={"customer_id": normalized_customer_id},
        )
        add_tool_trace("list_customer_orders", {"customer_id": normalized_customer_id}, result.to_dict())
        return result

    result = ToolResult(
        ok=True,
        tool_name="list_customer_orders",
        data={
            "customer_id": normalized_customer_id,
            "orders_count": len(rows),
            "orders": rows,
        },
    )
    add_tool_trace("list_customer_orders", {"customer_id": normalized_customer_id}, result.to_dict())
    return result