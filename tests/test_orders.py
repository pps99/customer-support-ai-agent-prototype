from app.order_service import cancel_order, get_order


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
