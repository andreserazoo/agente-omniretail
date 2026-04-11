from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOCAL_SITE_PACKAGES = ROOT / ".venv" / "Lib" / "site-packages"
if LOCAL_SITE_PACKAGES.exists() and str(LOCAL_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(LOCAL_SITE_PACKAGES))

from core.session_context import (
    add_tool_trace,
    get_session_customer,
    get_tool_trace,
    get_tool_trace_length,
    get_tool_trace_since,
    reset_session,
    set_session_customer,
)


def test_session_context_flow():
    reset_session()

    trace = add_tool_trace(
        "lookup_customer_by_dni",
        {"dni": "123456789"},
        {"found": True, "customer_id": 1001},
    )

    customer = set_session_customer(1001, "Cliente Demo")

    assert trace["tool_name"] == "lookup_customer_by_dni"
    assert trace["input_data"]["dni"] == "123456789"
    assert trace["output_data"]["customer_id"] == 1001
    assert get_tool_trace_length() == 1
    assert get_tool_trace()[0]["tool_name"] == "lookup_customer_by_dni"
    assert get_tool_trace_since(0)[0]["output_data"]["found"] is True
    assert customer["customer_id"] == 1001
    assert get_session_customer()["display_name"] == "Cliente Demo"
