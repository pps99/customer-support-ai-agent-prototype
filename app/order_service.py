import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any

from app.config import ORDERS_FILE


_orders_lock = threading.Lock()


def load_orders(data_file: Path | None = None) -> list[dict[str, Any]]:
    """Load orders from the local JSON data store."""
    path = data_file or ORDERS_FILE
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def save_orders(orders: list[dict[str, Any]], data_file: Path | None = None) -> None:
    """Atomically persist orders so a partial write cannot corrupt the store."""
    path = data_file or ORDERS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary_file:
        json.dump(orders, temporary_file, indent=2)
        temporary_file.write("\n")
        temporary_path = Path(temporary_file.name)

    os.replace(temporary_path, path)


def get_order(
    order_id: str,
    customer_email: str,
    data_file: Path | None = None,
) -> dict[str, Any] | None:
    """Return an order only when both its ID and customer email match."""
    for order in load_orders(data_file):
        if (
            order["order_id"] == order_id
            and order["customer_email"] == customer_email
        ):
            return order

    return None


def cancel_order(
    order_id: str,
    customer_email: str,
    data_file: Path | None = None,
) -> dict[str, Any]:
    """Validate whether an order can be cancelled and return the outcome."""
    with _orders_lock:
        orders = load_orders(data_file)

        for order in orders:
            if order["order_id"] != order_id:
                continue

            if order["customer_email"] != customer_email:
                return {"success": False, "reason": "IDENTITY_MISMATCH"}

            if order["status"] != "processing":
                return {"success": False, "reason": "ORDER_NOT_CANCELLABLE"}

            order["status"] = "cancelled"
            save_orders(orders, data_file)

            return {
                "success": True,
                "order_id": order_id,
                "status": "cancelled",
            }

    return {"success": False, "reason": "ORDER_NOT_FOUND"}
