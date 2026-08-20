from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_reports_policy_readiness():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] in {"ok", "degraded"}
    assert isinstance(response.json()["policy_documents"], int)


def test_order_lookup_does_not_put_email_in_url():
    response = client.post(
        "/orders/lookup",
        json={
            "order_id": "ORD-1001",
            "customer_email": "alice@example.com",
        },
    )

    assert response.status_code == 200
    assert response.json()["order_id"] == "ORD-1001"


def test_order_lookup_failure_is_neutral():
    response = client.post(
        "/orders/lookup",
        json={
            "order_id": "ORD-1001",
            "customer_email": "attacker@example.com",
        },
    )

    assert response.status_code == 404
    assert "identity" in response.json()["detail"].lower()
