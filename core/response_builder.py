"""Helpers to build consistent agent responses."""


def build_response(message: str, route: str, data: dict | None = None, ok: bool = True) -> dict:
    return {
        "ok": ok,
        "route": route,
        "message": message,
        "data": data or {},
    }
