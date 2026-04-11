from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal


STATUS_LABELS = {
    "active": "activo",
    "pending": "pendiente",
    "payment_confirmed": "pago confirmado",
    "preparing": "en preparacion",
    "shipped": "enviado",
    "in_transit": "en camino",
    "delivered": "entregado",
    "cancelled": "cancelado",
    "returned": "devuelto",
    "refunded": "reembolsado",
    "replaced": "reemplazado",
    "order_placed": "pedido creado",
}

DELIVERY_METHOD_LABELS = {
    "home_delivery": "domicilio",
    "pickup_point": "punto de recogida",
}


def format_value(value) -> str:
    if value is None:
        return "no disponible"

    if isinstance(value, bool):
        return "sí" if value else "no"

    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d")

    if isinstance(value, Decimal):
        value = float(value)

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.2f}"

    return str(value)


def format_currency_cop(value) -> str:
    if value is None:
        return "no disponible"

    try:
        amount = float(value)
    except Exception:
        return str(value)

    return f"COP {amount:,.0f}".replace(",", ".")


def format_short_text(value, fallback: str = "no disponible") -> str:
    if value is None:
        return fallback

    text = str(value).strip()
    if not text:
        return fallback

    return " ".join(text.split())


def format_status_label(value, fallback: str = "no disponible") -> str:
    text = format_short_text(value, fallback=fallback)
    normalized = text.strip().lower()
    return STATUS_LABELS.get(normalized, text)


def format_delivery_method(value, fallback: str = "no disponible") -> str:
    text = format_short_text(value, fallback=fallback)
    normalized = text.strip().lower()
    return DELIVERY_METHOD_LABELS.get(normalized, text)
