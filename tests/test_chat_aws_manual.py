from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DEFAULT_API_URL = "https://tqsbuks3mc.execute-api.us-east-1.amazonaws.com/Prod/chat"


WELCOME_TEXT = """
Agent OmniRetail AWS - Consola de prueba manual

Comandos disponibles:
  /help        Muestra esta ayuda
  /reset       Reinicia la sesión con un nuevo session_id
  /session     Muestra el session_id actual
  /examples    Muestra preguntas sugeridas
  /exit        Cierra la consola

Escribe cualquier mensaje para conversar con el agente desplegado en AWS.
""".strip()


EXAMPLES = [
    "Necesito ayuda con algo pero no sé cómo explicarlo",
    "¿Qué métodos de pago manejan?",
    "¿Cuál es el precio del producto 5001?",
    "¿Puedo devolver un producto en promoción?",
    "Mi documento es 878545512",
    "Quiero saber sobre mi pedido",
    "Quiero saber del pedido 28",
    "¿y la guía?",
    "¿y el tracking?",
    "¿Cuánto pagué en ese pedido?",
]


def _build_session_id() -> str:
    return f"aws-chat-{uuid.uuid4().hex[:8]}"


def _get_api_url() -> str:
    return os.getenv("OMNIRETAIL_AWS_API_URL", DEFAULT_API_URL).strip() or DEFAULT_API_URL


def _print_examples() -> None:
    print("\nPreguntas sugeridas:")
    for idx, example in enumerate(EXAMPLES, start=1):
        print(f"  {idx}. {example}")
    print()


def _send_message(api_url: str, session_id: str, message: str) -> dict:
    payload = json.dumps(
        {
            "message": message,
            "session_id": session_id,
        },
        ensure_ascii=False,
    ).encode("utf-8")

    request = Request(
        api_url,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    with urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)


def main() -> None:
    api_url = _get_api_url()
    session_id = _build_session_id()
    turn = 0

    print("=" * 88)
    print(WELCOME_TEXT)
    print("=" * 88)
    print(f"Endpoint AWS: {api_url}")
    print(f"Session ID inicial: {session_id}")

    while True:
        try:
            message = input("\nTú > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSesión terminada.")
            break

        if not message:
            continue

        command = message.lower()
        if command in {"/exit", "exit", "quit", "salir"}:
            print("Sesión terminada.")
            break
        if command == "/help":
            print("\n" + WELCOME_TEXT)
            continue
        if command == "/examples":
            _print_examples()
            continue
        if command == "/session":
            print(f"\nSession ID actual: {session_id}")
            continue
        if command == "/reset":
            session_id = _build_session_id()
            turn = 0
            print(f"\nSesión reiniciada correctamente. Nuevo session_id: {session_id}")
            continue

        turn += 1
        print(f"\nTurno {turn}")
        print("-" * 88)

        try:
            result = _send_message(api_url, session_id, message)
            print(f"Agente > {result.get('response', '')}")
        except HTTPError as exc:
            try:
                error_body = exc.read().decode("utf-8", errors="ignore")
            except Exception:
                error_body = str(exc)
            print(f"Agente > Error HTTP {exc.code}: {error_body}")
        except URLError as exc:
            print(f"Agente > No se pudo conectar al endpoint AWS: {exc}")
        except Exception as exc:
            print(f"Agente > Error durante la ejecución: {exc}")


if __name__ == "__main__":
    main()
