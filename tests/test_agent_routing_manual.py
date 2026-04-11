from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOCAL_SITE_PACKAGES = ROOT / ".venv" / "Lib" / "site-packages"
if LOCAL_SITE_PACKAGES.exists() and str(LOCAL_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(LOCAL_SITE_PACKAGES))

from core.agent import create_agent
from core.session_context import reset_session
from tools.auth_tools import verify_customer_by_dni


def main() -> None:
    reset_session()
    agent = create_agent()

    messages = [
        "¿Qué métodos de pago manejan?",
        "¿Puedo devolver un producto en promoción?",
        "¿Dónde está mi pedido?",
        "¿Cuál es el precio del producto 5001?",
    ]

    for message in messages:
        print("=" * 80)
        print("USER:", message)
        response = agent(message)
        print("AGENT:", response.content)

    print("=" * 80)
    print("AUTENTICANDO CLIENTE DE PRUEBA...")
    auth_result = verify_customer_by_dni("123456")
    print(auth_result.to_dict())

    print("=" * 80)
    response = agent("¿Dónde está mi pedido?")
    print("USER: ¿Dónde está mi pedido?")
    print("AGENT:", response.content)


if __name__ == "__main__":
    main()
