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
from tools.query_helpers import fetch_one_dict


def main() -> None:
    customer = fetch_one_dict(
        """
        SELECT customer_id, dni, name, last_name1, last_name2
        FROM customers
        LIMIT 1
        """
    )
    own_order = fetch_one_dict(
        f"""
        SELECT CAST(order_id AS VARCHAR) AS order_id
        FROM orders
        WHERE CAST(customer_id AS VARCHAR) = '{customer["customer_id"]}'
        LIMIT 1
        """
    )
    tracking_order = fetch_one_dict(
        f"""
        SELECT DISTINCT CAST(o.order_id AS VARCHAR) AS order_id
        FROM orders o
        JOIN tracking t
            ON o.order_id = t.order_id
        WHERE CAST(o.customer_id AS VARCHAR) = '{customer["customer_id"]}'
        LIMIT 1
        """
    )

    reset_session()
    agent = create_agent()

    messages = [
        f"¿Cuánto pagué en mi pedido {own_order['order_id']}?",
        f"Mi documento es {customer['dni']}",
        f"¿Cuánto pagué en mi pedido {own_order['order_id']}?",
        f"Dame el tracking del pedido {tracking_order['order_id']}",
        f"¿Mi producto del pedido {own_order['order_id']} aún tiene garantía?",
    ]

    for message in messages:
        print("=" * 100)
        print("USER:", message)
        response = agent(message)
        print("AGENT:", response.content)


if __name__ == "__main__":
    main()
