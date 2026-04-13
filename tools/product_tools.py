from __future__ import annotations

from core.session_context import add_tool_trace
from tools.base_tool_models import ToolResult
from tools.query_helpers import fetch_all_dicts, fetch_one_dict


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


def search_products_by_text(query: str, limit: int = 5) -> ToolResult:
    normalized_query = " ".join((query or "").strip().split())

    if not normalized_query:
        result = ToolResult(
            ok=False,
            tool_name="search_products_by_text",
            error="query vacio",
        )
        add_tool_trace("search_products_by_text", {"query": normalized_query}, result.to_dict())
        return result

    lowered = normalized_query.lower()
    rows = fetch_all_dicts(
        """
        SELECT
            p.product_id,
            p.name,
            p.price,
            p.active,
            b.name AS brand_name,
            c.name AS category_name,
            COALESCE((s.stock_qty - s.reserved_qty), 0) AS available_qty
        FROM products p
        LEFT JOIN brands b
            ON p.brand_id = b.brand_id
        LEFT JOIN categories c
            ON p.category_id = c.category_id
        LEFT JOIN stock s
            ON p.product_id = s.product_id
        WHERE LOWER(p.name) LIKE ?
           OR LOWER(COALESCE(b.name, '')) LIKE ?
           OR LOWER(COALESCE(c.name, '')) LIKE ?
        ORDER BY p.product_id
        LIMIT ?
        """,
        [f"%{lowered}%", f"%{lowered}%", f"%{lowered}%", limit],
    )

    if not rows:
        fallback_rows = fetch_all_dicts(
            """
            SELECT
                p.product_id,
                p.name,
                p.price,
                p.active,
                b.name AS brand_name,
                c.name AS category_name,
                COALESCE((s.stock_qty - s.reserved_qty), 0) AS available_qty
            FROM products p
            LEFT JOIN brands b
                ON p.brand_id = b.brand_id
            LEFT JOIN categories c
                ON p.category_id = c.category_id
            LEFT JOIN stock s
                ON p.product_id = s.product_id
            ORDER BY p.product_id
            """,
        )
        query_tokens = [
            token for token in lowered.split()
            if token not in {"buenas", "hola", "quiero", "saber", "tienen", "tiene", "cuanto", "cuesta", "vale"}
        ]
        scored_rows: list[tuple[int, dict]] = []
        for row in fallback_rows:
            haystack = " ".join(
                [
                    str(row.get("name", "")).lower(),
                    str(row.get("brand_name", "")).lower(),
                    str(row.get("category_name", "")).lower(),
                ]
            )
            score = sum(1 for token in query_tokens if token and token in haystack)
            if score > 0:
                scored_rows.append((score, row))
        scored_rows.sort(key=lambda item: (-item[0], item[1].get("product_id", 0)))
        rows = [row for _, row in scored_rows[:limit]]

    if not rows:
        result = ToolResult(
            ok=False,
            tool_name="search_products_by_text",
            error="Producto no encontrado",
            data={"query": normalized_query},
        )
        add_tool_trace("search_products_by_text", {"query": normalized_query}, result.to_dict())
        return result

    result = ToolResult(
        ok=True,
        tool_name="search_products_by_text",
        data={"query": normalized_query, "results": rows},
    )
    add_tool_trace("search_products_by_text", {"query": normalized_query}, result.to_dict())
    return result
