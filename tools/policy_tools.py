from __future__ import annotations

import re
import unicodedata

from core.policy_loader import load_policy_sections
from core.session_context import add_tool_trace
from tools.base_tool_models import ToolResult


STOPWORDS = {
    "a",
    "al",
    "ante",
    "con",
    "de",
    "del",
    "el",
    "ella",
    "en",
    "es",
    "esta",
    "este",
    "hago",
    "la",
    "las",
    "lo",
    "los",
    "me",
    "mi",
    "no",
    "o",
    "pasa",
    "por",
    "puedo",
    "que",
    "se",
    "si",
    "tengo",
    "un",
    "una",
}


def _normalize_text(text: str) -> str:
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _tokenize(text: str) -> list[str]:
    normalized = _normalize_text(text)
    return [
        token
        for token in re.split(r"[^a-z0-9]+", normalized)
        if token and token not in STOPWORDS and len(token) > 1
    ]


def _score_policy_section(
    query_text: str,
    source_file: str,
    title_norm: str,
    content_norm: str,
) -> tuple[int, list[str]]:
    query_tokens = _tokenize(query_text)
    score = 0
    matched_tokens: list[str] = []

    for token in query_tokens:
        if token in title_norm:
            score += 3
            matched_tokens.append(token)
        elif token in content_norm:
            score += 1
            matched_tokens.append(token)

    phrase_boosts = [
        ("producto llego incompleto", ["incompleto", "incorrecto", "dano estetico"], 8),
        ("rechazar el paquete", ["rechazar", "puerta", "entrega"], 7),
        ("celular se mojo", ["agua", "electronica"], 8),
        ("danos por agua", ["agua", "electronica"], 8),
        ("garantia en electronica", ["garantia", "electronica"], 6),
        ("tecnico no autorizado", ["tecnico", "autorizado"], 7),
        ("producto de belleza abierto", ["belleza", "cuidado personal", "abiertos", "abierto"], 8),
        ("pedido no llega en el tiempo estimado", ["tiempo", "entrega", "envio"], 5),
        ("cancelar un pedido que ya fue despachado", ["despacho", "despachado", "en camino"], 8),
    ]

    for trigger, related_terms, boost in phrase_boosts:
        if trigger in query_text:
            if any(term in title_norm for term in related_terms):
                score += boost
            elif any(term in content_norm for term in related_terms):
                score += boost // 2

    if any(trigger in query_text for trigger in ["celular se mojo", "mojo", "agua"]):
        if "garantia" in source_file and ("agua" in content_norm or "humedad" in content_norm):
            score += 20
        if "garantia" in source_file and "exclusiones especificas por categoria" in title_norm:
            score += 10

    if any(trigger in query_text for trigger in ["tecnico no autorizado", "no era autorizado"]):
        if "garantia" in source_file and (
            "personal no autorizado" in content_norm
            or "tecnicos no autorizados" in content_norm
            or "intervencion tecnica" in content_norm
        ):
            score += 18

    if "producto de belleza abierto" in query_text:
        if "devoluciones" in source_file and (
            "articulos no elegibles" in title_norm
            or "belleza y cuidado personal" in content_norm
            or "abiertos o usados" in content_norm
        ):
            score += 18

    return score, sorted(set(matched_tokens))


def search_policy_sections(query: str) -> ToolResult:
    normalized_query = (query or "").strip()

    if not normalized_query:
        result = ToolResult(
            ok=False,
            tool_name="search_policy_sections",
            error="query vacía",
        )
        add_tool_trace("search_policy_sections", {"query": normalized_query}, result.to_dict())
        return result

    query_tokens = _tokenize(normalized_query)
    if not query_tokens:
        result = ToolResult(
            ok=False,
            tool_name="search_policy_sections",
            error="query sin tokens útiles",
            data={"query": normalized_query},
        )
        add_tool_trace("search_policy_sections", {"query": normalized_query}, result.to_dict())
        return result

    sections = load_policy_sections()
    scored_sections = []

    for section in sections:
        title_norm = _normalize_text(section.section_title)
        content_norm = _normalize_text(section.content)
        score, matched_tokens = _score_policy_section(
            _normalize_text(normalized_query),
            _normalize_text(section.source_file),
            title_norm,
            content_norm,
        )

        if score > 0:
            scored_sections.append(
                {
                    "source_file": section.source_file,
                    "section_title": section.section_title,
                    "section_level": section.section_level,
                    "content": section.content,
                    "score": score,
                    "matched_tokens": sorted(set(matched_tokens)),
                }
            )

    scored_sections.sort(
        key=lambda item: (
            -item["score"],
            item["source_file"],
            item["section_title"],
        )
    )

    top_sections = scored_sections[:3]

    if not top_sections:
        result = ToolResult(
            ok=False,
            tool_name="search_policy_sections",
            error="No se encontraron secciones relevantes",
            data={"query": normalized_query},
        )
        add_tool_trace("search_policy_sections", {"query": normalized_query}, result.to_dict())
        return result

    result = ToolResult(
        ok=True,
        tool_name="search_policy_sections",
        data={
            "query": normalized_query,
            "results_count": len(top_sections),
            "results": top_sections,
        },
    )
    add_tool_trace("search_policy_sections", {"query": normalized_query}, result.to_dict())
    return result
