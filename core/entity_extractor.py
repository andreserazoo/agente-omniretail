from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass
class ExtractedEntities:
    dni: str | None = None
    phone: str | None = None
    order_id: str | None = None
    product_id: str | None = None


def extract_entities(user_message: str) -> ExtractedEntities:
    text = (user_message or "").strip()
    normalized_text = _normalize(text)

    order_id = _extract_labeled_number(
        normalized_text,
        patterns=[
            r"(?:pedido|pedio|peddido)\s*(?:#|no\.?|nro\.?|numero\s*|id\s*)?(\d{1,10})",
            r"orden\s*(?:#|no\.?|nro\.?|numero\s*|id\s*)?(\d{1,10})",
            r"order\s*id\s*(\d{1,10})",
            r"(?:^|[\s\?\.,])y\s+(?:el|la|del)\s+(\d{1,10})(?:$|[\s\?\.,])",
            r"(?:^|[\s\?\.,])el\s+(\d{1,10})\s+(?:cuanto|costo|vale|tiene)(?:$|[\s\?\.,])",
        ],
    )

    product_id = _extract_labeled_number(
        normalized_text,
        patterns=[
            r"(?:producto|prodcto|prod)\s*(?:#|id\s*)?(\d{3,10})",
            r"articulo\s*(?:#|id\s*)?(\d{3,10})",
            r"product\s*id\s*(\d{3,10})",
        ],
    )

    phone = _extract_phone(text)
    dni = _extract_dni(
        normalized_text,
        phone=phone,
        order_id=order_id,
        product_id=product_id,
    )

    return ExtractedEntities(
        dni=dni,
        phone=phone,
        order_id=order_id,
        product_id=product_id,
    )


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", (text or "").strip().lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _extract_labeled_number(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def _extract_phone(text: str) -> str | None:
    compact = re.sub(r"[^\d]", "", text or "")
    candidates = re.findall(r"(3\d{9})", compact)
    if candidates:
        return candidates[0]
    return None


def _extract_dni(
    text: str,
    phone: str | None = None,
    order_id: str | None = None,
    product_id: str | None = None,
) -> str | None:
    labeled_patterns = [
        r"(?:dni|documento|doc|cedula|cc)\s*(?:es|:)?\s*(\d{5,12})",
    ]

    for pattern in labeled_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)

    generic_candidates = re.findall(r"(?<!\d)(\d{5,12})(?!\d)", text)

    filtered: list[str] = []
    for value in generic_candidates:
        if phone and value == phone:
            continue
        if order_id and value == order_id:
            continue
        if product_id and value == product_id:
            continue
        filtered.append(value)

    if filtered:
        return filtered[0]

    return None
