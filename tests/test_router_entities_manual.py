from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOCAL_SITE_PACKAGES = ROOT / ".venv" / "Lib" / "site-packages"
if LOCAL_SITE_PACKAGES.exists() and str(LOCAL_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(LOCAL_SITE_PACKAGES))

from core.entity_extractor import extract_entities
from core.router import decide_route


def main() -> None:
    messages = [
        "Mi teléfono es 3001234567",
        "Mi documento es 12345678",
        "¿Dónde está mi pedido 2001?",
        "¿Mi producto del pedido 2001 aún tiene garantía?",
        "¿Puedo devolver el producto 5001 del pedido 2001?",
        "¿Cuál es el precio del producto 5001?",
    ]

    for message in messages:
        print("=" * 100)
        print("MENSAJE:", message)
        print("ROUTE:", decide_route(message))
        print("ENTITIES:", extract_entities(message))


if __name__ == "__main__":
    main()
