from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
import re


@dataclass
class RouteDecision:
    intent: str
    is_sensitive: bool
    requires_auth: bool
    data_source: str
    needs_order_id: bool = False
    needs_product_id: bool = False
    matched_keywords: list[str] = field(default_factory=list)


FAQ_KEYWORDS = {
    "metodos de pago",
    "pago",
    "pagos",
    "canales de atencion",
    "atencion",
    "whatsapp",
    "envios a todo colombia",
    "cobertura",
    "horario",
    "cuanto tarda",
    "tiempo de entrega",
    "dias habiles",
    "informacion general",
    "quiero info",
    "necesito ayuda",
    "me ayudas",
}

POLICY_KEYWORDS = {
    "devolucion",
    "devolver",
    "cambio",
    "garantia",
    "reembolso",
    "despacho",
    "direccion",
    "envio",
    "promocion",
    "promocional",
}

ORDER_AMOUNT_KEYWORDS = {
    "subtotal",
    "iva",
    "total",
    "total_amount",
    "shipping_cost",
    "costo de envio",
    "cuanto pague",
    "monto",
    "montos",
}

ORDER_STATUS_KEYWORDS = {
    "mi pedido",
    "estado de mi pedido",
    "donde esta mi pedido",
    "donde va mi pedido",
    "donde anda",
    "onde anda",
    "onde esta",
    "que paso con mi pedido",
    "que ha pasado con mi pedido",
    "que ha pasao con mi pedido",
    "info de mi pedido",
    "dame info del pedido",
    "quiero saber del pedido",
    "informacion del pedido",
    "informacion sobre el pedido",
    "detalle del pedido",
    "resumen del pedido",
    "ver pedido",
    "revisar pedido",
    "tracking",
    "historial",
    "guia",
    "envio de mi pedido",
    "pedido entregado",
    "pedido cancelado",
    "transportadora",
    "en camino",
    "entregado",
    "y la guia",
    "y el tracking",
}

PRODUCT_KEYWORDS = {
    "precio",
    "stock",
    "disponible",
    "inventario",
    "producto",
    "envio gratis",
    "promocion",
    "categoria",
    "marca",
}

WARRANTY_KEYWORDS = {
    "garantia",
    "warranty",
    "aun tiene garantia",
    "vigencia de garantia",
}

RETURN_KEYWORDS = {
    "devolucion",
    "devolver",
    "cambio",
    "reembolso",
    "return_deadline",
    "fecha limite de devolucion",
    "puedo devolver",
}


def _normalize(text: str) -> str:
    raw = " ".join((text or "").strip().lower().split())
    normalized = unicodedata.normalize("NFKD", raw)
    text = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return re.sub(r"\s+", " ", text)


def _find_matches(text: str, keywords: set[str]) -> list[str]:
    return sorted([keyword for keyword in keywords if keyword in text])


def decide_route(user_message: str) -> RouteDecision:
    text = _normalize(user_message)

    faq_matches = _find_matches(text, FAQ_KEYWORDS)
    policy_matches = _find_matches(text, POLICY_KEYWORDS)
    amount_matches = _find_matches(text, ORDER_AMOUNT_KEYWORDS)
    status_matches = _find_matches(text, ORDER_STATUS_KEYWORDS)
    product_matches = _find_matches(text, PRODUCT_KEYWORDS)
    warranty_matches = _find_matches(text, WARRANTY_KEYWORDS)
    return_matches = _find_matches(text, RETURN_KEYWORDS)

    mentions_my_purchase = any(
        token in text
        for token in [
            "mi pedido",
            "mi compra",
            "mi producto",
            "del pedido",
            "de mi pedido",
            "de mi compra",
            "pedido ",
            "pedio ",
        ]
    )

    # Fuzzy stems to survive imperfect encoding like "garant?a" / "gu?a".
    has_warranty_signal = any(token in text for token in ["garant", "warranty"])
    has_return_signal = any(token in text for token in ["devol", "reembol", "cambio"])
    has_status_signal = any(
        token in text
        for token in [
            "tracking",
            "track",
            "trak",
            "historial",
            "transportadora",
            "guia",
            "gui",
            "envio",
            "donde esta",
            "donde va",
            "donde anda",
            "onde anda",
            "onde esta",
            "que paso",
            "pasao",
            "dame info del pedido",
            "quiero saber del pedido",
            "informacion del pedido",
            "detalle del pedido",
            "resumen del pedido",
            "ver pedido",
            "revisar pedido",
            "estado",
        ]
    )
    has_faq_signal = any(
        token in text
        for token in ["pago", "whatsapp", "atenc", "env", "cobertura", "tarda", "informacion general"]
    )

    if amount_matches:
        return RouteDecision(
            intent="order_amount",
            is_sensitive=True,
            requires_auth=True,
            data_source="orders",
            needs_order_id=True,
            matched_keywords=amount_matches,
        )

    if (warranty_matches or (has_warranty_signal and mentions_my_purchase)) and mentions_my_purchase:
        return RouteDecision(
            intent="warranty_check",
            is_sensitive=True,
            requires_auth=True,
            data_source="order_items_products",
            needs_order_id=True,
            matched_keywords=warranty_matches or ["garant"],
        )

    if (return_matches or (has_return_signal and mentions_my_purchase)) and mentions_my_purchase:
        return RouteDecision(
            intent="return_request",
            is_sensitive=True,
            requires_auth=True,
            data_source="order_items_products_policies",
            needs_order_id=True,
            matched_keywords=return_matches or ["devol"],
        )

    if status_matches or (("pedido" in text or "pedio" in text) and has_status_signal):
        return RouteDecision(
            intent="order_status_history",
            is_sensitive=True,
            requires_auth=True,
            data_source="orders_tracking_shipments",
            needs_order_id=True,
            matched_keywords=status_matches or ["pedido"],
        )

    if policy_matches and mentions_my_purchase:
        return RouteDecision(
            intent="policy_specific_order_case",
            is_sensitive=True,
            requires_auth=True,
            data_source="orders_items_policies",
            needs_order_id=True,
            matched_keywords=policy_matches,
        )

    if policy_matches:
        return RouteDecision(
            intent="policy_question",
            is_sensitive=False,
            requires_auth=False,
            data_source="policies",
            matched_keywords=policy_matches,
        )

    if product_matches:
        return RouteDecision(
            intent="product_price_stock",
            is_sensitive=False,
            requires_auth=False,
            data_source="products_stock_promotions",
            needs_product_id=True,
            matched_keywords=product_matches,
        )

    if faq_matches or (has_faq_signal and not mentions_my_purchase):
        return RouteDecision(
            intent="faq_public",
            is_sensitive=False,
            requires_auth=False,
            data_source="static_or_policies",
            matched_keywords=faq_matches or ["faq_signal"],
        )

    return RouteDecision(
        intent="unknown",
        is_sensitive=False,
        requires_auth=False,
        data_source="unknown",
        matched_keywords=[],
    )
