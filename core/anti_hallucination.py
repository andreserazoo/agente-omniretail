from __future__ import annotations

from typing import Iterable

from core.session_context import get_tool_trace_since


def has_required_tool_usage_since(
    trace_start_index: int,
    required_tool_names: Iterable[str],
) -> bool:
    """
    Verifica si desde un punto dado de la traza ya se usó al menos una
    de las tools requeridas.
    """
    required = set(required_tool_names)
    if not required:
        return True

    traces = get_tool_trace_since(trace_start_index)
    used_tools = {entry.get("tool_name") for entry in traces}

    return any(tool_name in used_tools for tool_name in required)


def build_missing_tool_response() -> str:
    return (
        "No puedo confirmar ese dato todavía porque no logré consultar "
        "la fuente necesaria en este turno."
    )