from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOCAL_SITE_PACKAGES = ROOT / ".venv" / "Lib" / "site-packages"
if LOCAL_SITE_PACKAGES.exists() and str(LOCAL_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(LOCAL_SITE_PACKAGES))

from core.agent import OmniRetailAgent
from core.router import route_request
from core.session_context import SessionContext


def test_route_request_orders():
    assert route_request("Quiero revisar mi pedido") == "orders"


def test_agent_handle_returns_response():
    agent = OmniRetailAgent()
    context = SessionContext(user_id="user-1", authenticated=True)

    response = agent.handle("Necesito ayuda con una devolucion", context)

    assert response["ok"] is True
    assert response["route"] == "policies"
    assert response["data"]["user_id"] == "user-1"
