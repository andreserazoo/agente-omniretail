from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any

# IMPORTANTE:
# Este estado vive a nivel de módulo para que sea accesible dentro del mismo proceso.
# No usar threading.local(), contextvars ni mecanismos que aíslen el estado por hilo.
_LOCK = RLock()
MAX_TOOL_TRACE_ENTRIES = 100
MAX_CONVERSATION_MESSAGES = 12

_SESSION_STATE: dict[str, Any] = {
    "customer": None,
    "tool_trace": [],
    "conversation": [],
    "metadata": {},
}


@dataclass
class SessionContext:
    user_id: str | None = None
    locale: str = "es-MX"
    authenticated: bool = False
    cart_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def _now_iso() -> str:
    """Retorna timestamp UTC en formato ISO 8601."""
    return datetime.now(timezone.utc).isoformat()


def _safe_copy(value: Any) -> Any:
    """
    Hace una copia segura para evitar que el estado interno sea mutado desde fuera.
    Si deepcopy falla, retorna una representación segura.
    """
    try:
        return deepcopy(value)
    except Exception:
        return repr(value)


def _append_bounded(items: list[Any], value: Any, max_size: int) -> None:
    items.append(value)
    overflow = len(items) - max_size
    if overflow > 0:
        del items[:overflow]


# =========================================================
# Funciones OBLIGATORIAS para el reto
# =========================================================

def add_tool_trace(tool_name: str, input_data: Any, output_data: Any) -> dict[str, Any]:
    """
    Registra evidencia auditable de uso de herramienta.

    Args:
        tool_name: Nombre lógico de la herramienta invocada.
        input_data: Entrada usada por la herramienta.
        output_data: Resultado devuelto por la herramienta.

    Returns:
        La traza registrada.
    """
    if not isinstance(tool_name, str) or not tool_name.strip():
        raise ValueError("tool_name debe ser un string no vacío")

    entry = {
        "timestamp": _now_iso(),
        "tool_name": tool_name.strip(),
        "input_data": _safe_copy(input_data),
        "output_data": _safe_copy(output_data),
    }

    with _LOCK:
        _append_bounded(_SESSION_STATE["tool_trace"], entry, MAX_TOOL_TRACE_ENTRIES)

    return _safe_copy(entry)


def set_session_customer(customer_id: Any, display_name: str) -> dict[str, Any]:
    """
    Registra que la identidad del cliente fue verificada exitosamente.

    Args:
        customer_id: Identificador interno del cliente.
        display_name: Nombre visible para la conversación.

    Returns:
        El cliente almacenado en sesión.
    """
    if customer_id is None or str(customer_id).strip() == "":
        raise ValueError("customer_id no puede estar vacío")

    customer = {
        "customer_id": customer_id,
        "display_name": (display_name or "").strip() or f"Cliente {customer_id}",
        "verified_at": _now_iso(),
    }

    with _LOCK:
        _SESSION_STATE["customer"] = customer

    return _safe_copy(customer)


def reset_session() -> None:
    """
    Limpia completamente el estado de sesión.
    """
    with _LOCK:
        _SESSION_STATE["customer"] = None
        _SESSION_STATE["tool_trace"] = []
        _SESSION_STATE["conversation"] = []
        _SESSION_STATE["metadata"] = {}


def get_tool_trace() -> list[dict[str, Any]]:
    """
    Retorna todas las trazas registradas.
    """
    with _LOCK:
        return _safe_copy(_SESSION_STATE["tool_trace"])


def get_tool_trace_length() -> int:
    """
    Retorna la cantidad de trazas registradas.
    """
    with _LOCK:
        return len(_SESSION_STATE["tool_trace"])


def get_tool_trace_since(index: int) -> list[dict[str, Any]]:
    """
    Retorna las trazas desde una posición dada.

    Args:
        index: Índice inicial.

    Returns:
        Lista de trazas desde ese índice.
    """
    if not isinstance(index, int):
        raise TypeError("index debe ser un entero")

    if index < 0:
        index = 0

    with _LOCK:
        return _safe_copy(_SESSION_STATE["tool_trace"][index:])


# =========================================================
# Funciones auxiliares (no obligatorias, pero útiles)
# =========================================================

def get_session_customer() -> dict[str, Any] | None:
    """
    Retorna el cliente autenticado actual, si existe.
    """
    with _LOCK:
        return _safe_copy(_SESSION_STATE["customer"])


def has_verified_customer() -> bool:
    """
    Indica si ya hay un cliente verificado en la sesión.
    """
    with _LOCK:
        return _SESSION_STATE["customer"] is not None


def clear_session_customer() -> None:
    """
    Limpia solo el cliente verificado, sin borrar trazas ni conversación.
    """
    with _LOCK:
        _SESSION_STATE["customer"] = None


def add_conversation_message(role: str, content: str) -> dict[str, str]:
    """
    Guarda un turno de conversación. Útil para memoria básica.
    """
    if not isinstance(role, str) or not role.strip():
        raise ValueError("role debe ser un string no vacío")

    message = {
        "timestamp": _now_iso(),
        "role": role.strip(),
        "content": content if isinstance(content, str) else str(content),
    }

    with _LOCK:
        _append_bounded(
            _SESSION_STATE["conversation"],
            message,
            MAX_CONVERSATION_MESSAGES,
        )

    return _safe_copy(message)


def get_conversation_history() -> list[dict[str, str]]:
    """
    Retorna el historial conversacional guardado en sesión.
    """
    with _LOCK:
        return _safe_copy(_SESSION_STATE["conversation"])


def set_context_value(key: str, value: Any) -> None:
    """
    Guarda metadata útil de sesión, por ejemplo:
    last_intent, last_order_id, last_policy_topic, etc.
    """
    if not isinstance(key, str) or not key.strip():
        raise ValueError("key debe ser un string no vacío")

    with _LOCK:
        _SESSION_STATE["metadata"][key.strip()] = _safe_copy(value)


def get_context_value(key: str, default: Any = None) -> Any:
    """
    Lee un valor de metadata de sesión.
    """
    if not isinstance(key, str) or not key.strip():
        return default

    with _LOCK:
        return _safe_copy(_SESSION_STATE["metadata"].get(key.strip(), default))


def clear_context_value(key: str) -> None:
    """
    Elimina una clave puntual de metadata.
    """
    if not isinstance(key, str) or not key.strip():
        return

    with _LOCK:
        _SESSION_STATE["metadata"].pop(key.strip(), None)


def get_session_snapshot() -> dict[str, Any]:
    """
    Devuelve una foto completa del estado actual.
    Muy útil para depuración local.
    """
    with _LOCK:
        return _safe_copy(_SESSION_STATE)


__all__ = [
    "SessionContext",
    "add_tool_trace",
    "set_session_customer",
    "reset_session",
    "get_tool_trace",
    "get_tool_trace_length",
    "get_tool_trace_since",
    "get_session_customer",
    "has_verified_customer",
    "clear_session_customer",
    "add_conversation_message",
    "get_conversation_history",
    "set_context_value",
    "get_context_value",
    "clear_context_value",
    "get_session_snapshot",
]
