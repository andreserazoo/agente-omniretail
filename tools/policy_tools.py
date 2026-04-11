from __future__ import annotations

import re
import unicodedata

from core.policy_loader import load_policy_sections
from core.session_context import add_tool_trace
from tools.base_tool_models import ToolResult


def _normalize_text(text: str) -> str:
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _tokenize(text: str) -> list[str]:
    normalized = _normalize_text(text)
    return [token for token in re.split(r"[^a-z0-9]+", normalized) if token]


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

        score = 0
        matched_tokens: list[str] = []

        for token in query_tokens:
            if token in title_norm:
                score += 3
                matched_tokens.append(token)
            elif token in content_norm:
                score += 1
                matched_tokens.append(token)

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