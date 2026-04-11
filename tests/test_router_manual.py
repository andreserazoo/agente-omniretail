from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOCAL_SITE_PACKAGES = ROOT / ".venv" / "Lib" / "site-packages"
if LOCAL_SITE_PACKAGES.exists() and str(LOCAL_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(LOCAL_SITE_PACKAGES))

from core.router import decide_route


def main() -> None:
    test_messages = [
        "¿Qué métodos de pago manejan?",
        "¿Puedo devolver un producto en promoción?",
        "¿Cuánto pagué de IVA en mi pedido?",
        "¿Dónde está mi pedido?",
        "¿Cuál es el precio del producto 5001?",
        "Necesito ayuda",
    ]

    for message in test_messages:
        result = decide_route(message)
        print("=" * 80)
        print("MENSAJE:", message)
        print("RESULTADO:", result)


if __name__ == "__main__":
    main()
