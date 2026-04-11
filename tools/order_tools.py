from __future__ import annotations

from core.session_context import add_tool_trace
from tools.base_tool_models import ToolResult
from tools.query_helpers import fetch_all_dicts, fetch_one_dict


def get_order_amounts(order_id: str) -> ToolResult:
    normalized_order_id = (order_id or "").strip()

    if not normalized_order_id:
        result = ToolResult(
            ok=False,
            tool_name="get_order_amounts",
            error="order_id vacío",
        )
        add_tool_trace("get_order_amounts", {"order_id": normalized_order_id}, result.to_dict())
        return result

    row = fetch_one_dict(
        """
        SELECT
            order_id,
            customer_id,
            status,
            subtotal,
            shipping_cost,
            tax,
            total_amount,
            payment_method,
            delivery_method,
            order_date
        FROM orders
        WHERE CAST(order_id AS VARCHAR) = ?
        LIMIT 1
        """,
        [normalized_order_id],
    )

    if not row:
        result = ToolResult(
            ok=False,
            tool_name="get_order_amounts",
            error="Pedido no encontrado",
            data={"order_id": normalized_order_id},
        )
        add_tool_trace("get_order_amounts", {"order_id": normalized_order_id}, result.to_dict())
        return result

    result = ToolResult(
        ok=True,
        tool_name="get_order_amounts",
        data=row,
    )
    add_tool_trace("get_order_amounts", {"order_id": normalized_order_id}, result.to_dict())
    return result


def get_order_status(order_id: str) -> ToolResult:
    normalized_order_id = (order_id or "").strip()

    if not normalized_order_id:
        result = ToolResult(
            ok=False,
            tool_name="get_order_status",
            error="order_id vacío",
        )
        add_tool_trace("get_order_status", {"order_id": normalized_order_id}, result.to_dict())
        return result

    row = fetch_one_dict(
        """
        SELECT
            order_id,
            customer_id,
            status,
            order_date,
            payment_confirmed_at,
            shipped_at,
            delivered_at,
            cancelled_at,
            cancellation_reason,
            delivery_method
        FROM orders
        WHERE CAST(order_id AS VARCHAR) = ?
        LIMIT 1
        """,
        [normalized_order_id],
    )

    if not row:
        result = ToolResult(
            ok=False,
            tool_name="get_order_status",
            error="Pedido no encontrado",
            data={"order_id": normalized_order_id},
        )
        add_tool_trace("get_order_status", {"order_id": normalized_order_id}, result.to_dict())
        return result

    result = ToolResult(
        ok=True,
        tool_name="get_order_status",
        data=row,
    )
    add_tool_trace("get_order_status", {"order_id": normalized_order_id}, result.to_dict())
    return result


def get_order_tracking_history(order_id: str) -> ToolResult:
    normalized_order_id = (order_id or "").strip()

    if not normalized_order_id:
        result = ToolResult(
            ok=False,
            tool_name="get_order_tracking_history",
            error="order_id vacío",
        )
        add_tool_trace("get_order_tracking_history", {"order_id": normalized_order_id}, result.to_dict())
        return result

    rows = fetch_all_dicts(
        """
        SELECT
            tracking_id,
            order_id,
            item_id,
            timestamp,
            status,
            location
        FROM tracking
        WHERE CAST(order_id AS VARCHAR) = ?
        ORDER BY timestamp ASC
        """,
        [normalized_order_id],
    )

    if not rows:
        result = ToolResult(
            ok=False,
            tool_name="get_order_tracking_history",
            error="No se encontraron eventos de tracking para ese pedido",
            data={"order_id": normalized_order_id},
        )
        add_tool_trace("get_order_tracking_history", {"order_id": normalized_order_id}, result.to_dict())
        return result

    result = ToolResult(
        ok=True,
        tool_name="get_order_tracking_history",
        data={
            "order_id": normalized_order_id,
            "events": rows,
            "events_count": len(rows),
        },
    )
    add_tool_trace("get_order_tracking_history", {"order_id": normalized_order_id}, result.to_dict())
    return result


def get_order_shipments(order_id: str) -> ToolResult:
    normalized_order_id = (order_id or "").strip()

    if not normalized_order_id:
        result = ToolResult(
            ok=False,
            tool_name="get_order_shipments",
            error="order_id vacío",
        )
        add_tool_trace("get_order_shipments", {"order_id": normalized_order_id}, result.to_dict())
        return result

    rows = fetch_all_dicts(
        """
        SELECT
            shipment_id,
            order_id,
            item_id,
            carrier,
            tracking_number,
            tracking_url,
            shipped_date,
            estimated_delivery_date,
            actual_delivery_date,
            delivery_attempts,
            last_attempt_date,
            failed_delivery_reason,
            shipment_status
        FROM shipments
        WHERE CAST(order_id AS VARCHAR) = ?
        ORDER BY shipped_date ASC NULLS LAST
        """,
        [normalized_order_id],
    )

    if not rows:
        result = ToolResult(
            ok=False,
            tool_name="get_order_shipments",
            error="No se encontraron envíos para ese pedido",
            data={"order_id": normalized_order_id},
        )
        add_tool_trace("get_order_shipments", {"order_id": normalized_order_id}, result.to_dict())
        return result

    result = ToolResult(
        ok=True,
        tool_name="get_order_shipments",
        data={
            "order_id": normalized_order_id,
            "shipments": rows,
            "shipments_count": len(rows),
        },
    )
    add_tool_trace("get_order_shipments", {"order_id": normalized_order_id}, result.to_dict())
    return result


def order_belongs_to_customer(order_id: str, customer_id: str) -> ToolResult:
    normalized_order_id = (order_id or "").strip()
    normalized_customer_id = (customer_id or "").strip()

    if not normalized_order_id or not normalized_customer_id:
        result = ToolResult(
            ok=False,
            tool_name="order_belongs_to_customer",
            error="order_id o customer_id vacío",
            data={
                "order_id": normalized_order_id,
                "customer_id": normalized_customer_id,
            },
        )
        add_tool_trace(
            "order_belongs_to_customer",
            {"order_id": normalized_order_id, "customer_id": normalized_customer_id},
            result.to_dict(),
        )
        return result

    row = fetch_one_dict(
        """
        SELECT
            order_id,
            customer_id
        FROM orders
        WHERE CAST(order_id AS VARCHAR) = ?
        LIMIT 1
        """,
        [normalized_order_id],
    )

    if not row:
        result = ToolResult(
            ok=False,
            tool_name="order_belongs_to_customer",
            error="Pedido no encontrado",
            data={
                "order_id": normalized_order_id,
                "customer_id": normalized_customer_id,
                "belongs": False,
                "exists": False,
            },
        )
        add_tool_trace(
            "order_belongs_to_customer",
            {"order_id": normalized_order_id, "customer_id": normalized_customer_id},
            result.to_dict(),
        )
        return result

    actual_customer_id = str(row["customer_id"])
    belongs = actual_customer_id == normalized_customer_id

    result = ToolResult(
        ok=True,
        tool_name="order_belongs_to_customer",
        data={
            "order_id": normalized_order_id,
            "customer_id": normalized_customer_id,
            "belongs": belongs,
            "exists": True,
            "actual_customer_id": actual_customer_id,
        },
    )
    add_tool_trace(
        "order_belongs_to_customer",
        {"order_id": normalized_order_id, "customer_id": normalized_customer_id},
        result.to_dict(),
    )
    return result