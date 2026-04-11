from __future__ import annotations

from core.session_context import add_tool_trace
from tools.base_tool_models import ToolResult
from tools.query_helpers import fetch_one_dict


def get_product_price(product_id: str) -> ToolResult:
    normalized_product_id = (product_id or "").strip()

    if not normalized_product_id:
        result = ToolResult(
            ok=False,
            tool_name="get_product_price",
            error="product_id vacío",
        )
        add_tool_trace("get_product_price", {"product_id": normalized_product_id}, result.to_dict())
        return result

    row = fetch_one_dict(
        """
        SELECT
            p.product_id,
            p.name,
            p.price,
            p.free_shipping,
            p.active,
            b.name AS brand_name,
            c.name AS category_name
        FROM products p
        LEFT JOIN brands b
            ON p.brand_id = b.brand_id
        LEFT JOIN categories c
            ON p.category_id = c.category_id
        WHERE CAST(p.product_id AS VARCHAR) = ?
        LIMIT 1
        """,
        [normalized_product_id],
    )

    if not row:
        result = ToolResult(
            ok=False,
            tool_name="get_product_price",
            error="Producto no encontrado",
            data={"product_id": normalized_product_id},
        )
        add_tool_trace("get_product_price", {"product_id": normalized_product_id}, result.to_dict())
        return result

    result = ToolResult(
        ok=True,
        tool_name="get_product_price",
        data=row,
    )
    add_tool_trace("get_product_price", {"product_id": normalized_product_id}, result.to_dict())
    return result


def get_product_stock(product_id: str) -> ToolResult:
    normalized_product_id = (product_id or "").strip()

    if not normalized_product_id:
        result = ToolResult(
            ok=False,
            tool_name="get_product_stock",
            error="product_id vacío",
        )
        add_tool_trace("get_product_stock", {"product_id": normalized_product_id}, result.to_dict())
        return result

    row = fetch_one_dict(
        """
        SELECT
            p.product_id,
            p.name,
            s.stock_qty,
            s.reserved_qty,
            (s.stock_qty - s.reserved_qty) AS available_qty,
            s.low_stock_threshold,
            s.restock_date,
            s.last_updated,
            s.warehouse_location,
            p.active
        FROM products p
        LEFT JOIN stock s
            ON p.product_id = s.product_id
        WHERE CAST(p.product_id AS VARCHAR) = ?
        LIMIT 1
        """,
        [normalized_product_id],
    )

    if not row:
        result = ToolResult(
            ok=False,
            tool_name="get_product_stock",
            error="Producto no encontrado",
            data={"product_id": normalized_product_id},
        )
        add_tool_trace("get_product_stock", {"product_id": normalized_product_id}, result.to_dict())
        return result

    result = ToolResult(
        ok=True,
        tool_name="get_product_stock",
        data=row,
    )
    add_tool_trace("get_product_stock", {"product_id": normalized_product_id}, result.to_dict())
    return result