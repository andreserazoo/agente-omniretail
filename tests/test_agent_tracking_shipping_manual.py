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


def main() -> None:
    reset_session()
    agent = create_agent()

    test_messages = [
        "Mi documento es 123456",
        "¿Dónde está mi pedido 2001?",
        "Dame el tracking del pedido 2001",
        "Dame la guía del pedido 2001",
    ]

    for message in test_messages:
        print("=" * 80)
        print("USER:", message)
        response = agent(message)
        print("AGENT:", response.content)


if __name__ == "__main__":
    main()
