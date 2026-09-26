from fastapi.testclient import TestClient

from app.models import ChatResponse
from app import main
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


def test_chat_endpoint_passes_conversation_history(monkeypatch):
    def fake_process_support_message(
        message,
        order_id,
        customer_email,
        history,
    ):
        assert message == "alice@example.com"
        assert order_id is None
        assert customer_email is None
        assert history == [
            {"role": "user", "content": "Check status for ORD-1001"},
            {"role": "assistant", "content": "Please provide your email."},
        ]
        return ChatResponse(
            response="Order ORD-1001 is currently shipped.",
            action="ORDER_STATUS",
        )

    monkeypatch.setattr(main, "process_support_message", fake_process_support_message)

    response = client.post(
        "/chat",
        json={
            "message": "alice@example.com",
            "history": [
                {"role": "user", "content": "Check status for ORD-1001"},
                {"role": "assistant", "content": "Please provide your email."},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["action"] == "ORDER_STATUS"
