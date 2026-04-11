from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOCAL_SITE_PACKAGES = ROOT / ".venv" / "Lib" / "site-packages"
if LOCAL_SITE_PACKAGES.exists() and str(LOCAL_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(LOCAL_SITE_PACKAGES))

from core.agent import create_agent


def main() -> None:
    agent = create_agent()

    response_1 = agent("Hola")
    print("Respuesta 1:", str(response_1))
    print("Contenido 1:", response_1.content)

    response_2 = agent("")
    print("Respuesta 2:", str(response_2))
    print("Contenido 2:", response_2.content)

    agent.reset_memory()
    response_3 = agent("Quiero saber sobre mi pedido")
    print("Respuesta 3:", str(response_3))
    print("Contenido 3:", response_3.content)


if __name__ == "__main__":
    main()
