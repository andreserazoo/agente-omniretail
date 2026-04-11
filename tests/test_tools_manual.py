from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOCAL_SITE_PACKAGES = ROOT / ".venv" / "Lib" / "site-packages"
if LOCAL_SITE_PACKAGES.exists() and str(LOCAL_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(LOCAL_SITE_PACKAGES))

from core.session_context import get_session_customer, get_tool_trace, reset_session
from tools.auth_tools import verify_customer_by_dni, verify_customer_by_phone
from tools.order_tools import (
    get_order_amounts,
    get_order_shipments,
    get_order_status,
    get_order_tracking_history,
)
from tools.policy_tools import search_policy_sections
from tools.product_tools import get_product_price, get_product_stock


def main() -> None:
    reset_session()

    print("=== AUTH DNI ===")
    print(verify_customer_by_dni("123456").to_dict())

    print("=== AUTH PHONE ===")
    print(verify_customer_by_phone("3001234567").to_dict())

    print("=== ORDER AMOUNTS ===")
    print(get_order_amounts("2001").to_dict())

    print("=== ORDER STATUS ===")
    print(get_order_status("2001").to_dict())

    print("=== ORDER TRACKING ===")
    print(get_order_tracking_history("2001").to_dict())

    print("=== ORDER SHIPMENTS ===")
    print(get_order_shipments("2001").to_dict())

    print("=== PRODUCT PRICE ===")
    print(get_product_price("5001").to_dict())

    print("=== PRODUCT STOCK ===")
    print(get_product_stock("5001").to_dict())

    print("=== POLICY SEARCH ===")
    print(search_policy_sections("producto en promoción devolución").to_dict())
    print(search_policy_sections("garantía daños por agua").to_dict())
    print(search_policy_sections("cambio de dirección después del despacho").to_dict())

    print("=== SESSION CUSTOMER ===")
    print(get_session_customer())

    print("=== TOOL TRACE LENGTH ===")
    print(len(get_tool_trace()))


if __name__ == "__main__":
    main()
