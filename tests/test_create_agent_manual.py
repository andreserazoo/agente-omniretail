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
    response = agent("Hola")

    print("Agent creado correctamente:", agent is not None)
    print("Respuesta no nula:", response is not None)
    print("Contenido:", response.content)
    print("Como texto:", str(response))


if __name__ == "__main__":
    main()
