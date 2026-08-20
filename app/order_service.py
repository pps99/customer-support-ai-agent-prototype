import json
from typing import Any

from app.config import ORDERS_FILE


def load_orders() -> list[dict[str, Any]]:
    """Load orders from the local JSON data store."""
    with ORDERS_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def get_order(order_id: str, customer_email: str) -> dict[str, Any] | None:
    """Return an order only when both its ID and customer email match."""
    for order in load_orders():
        if (
            order["order_id"] == order_id
            and order["customer_email"] == customer_email
        ):
            return order

    return None


def cancel_order(order_id: str, customer_email: str) -> dict[str, Any]:
    """Validate whether an order can be cancelled and return the outcome."""
    orders = load_orders()

    for order in orders:
        if order["order_id"] != order_id:
            continue

        if order["customer_email"] != customer_email:
            return {"success": False, "reason": "IDENTITY_MISMATCH"}

        if order["status"] != "processing":
            return {"success": False, "reason": "ORDER_NOT_CANCELLABLE"}

        order["status"] = "cancelled"

        return {
            "success": True,
            "order_id": order_id,
            "status": "cancelled",
        }

    return {"success": False, "reason": "ORDER_NOT_FOUND"}
