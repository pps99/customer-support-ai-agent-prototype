import json

from app.order_service import cancel_order, get_order


def write_orders(path):
    path.write_text(
        json.dumps(
            [
                {
                    "order_id": "ORD-TEST",
                    "customer_email": "test@example.com",
                    "status": "processing",
                }
            ]
        ),
        encoding="utf-8",
    )


def test_correct_customer_can_get_order():
    order = get_order("ORD-1001", "alice@example.com")

    assert order is not None
    assert order["order_id"] == "ORD-1001"


def test_wrong_customer_cannot_get_order():
    order = get_order("ORD-1001", "wrong@example.com")

    assert order is None


def test_shipped_order_cannot_be_cancelled():
    result = cancel_order("ORD-1001", "alice@example.com")

    assert result["success"] is False
    assert result["reason"] == "ORDER_NOT_CANCELLABLE"


def test_order_lookup_checks_every_order():
    order = get_order("ORD-1002", "bob@example.com")

    assert order is not None
    assert order["order_id"] == "ORD-1002"


def test_successful_cancellation_is_persisted(tmp_path):
    orders_file = tmp_path / "orders.json"
    write_orders(orders_file)

    result = cancel_order(
        "ORD-TEST",
        "test@example.com",
        data_file=orders_file,
    )

    assert result["success"] is True
    persisted = get_order(
        "ORD-TEST",
        "test@example.com",
        data_file=orders_file,
    )
    assert persisted["status"] == "cancelled"


def test_identity_mismatch_does_not_modify_order(tmp_path):
    orders_file = tmp_path / "orders.json"
    write_orders(orders_file)

    result = cancel_order(
        "ORD-TEST",
        "attacker@example.com",
        data_file=orders_file,
    )

    assert result == {"success": False, "reason": "IDENTITY_MISMATCH"}
    assert json.loads(orders_file.read_text())[0]["status"] == "processing"
