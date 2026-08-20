from app.models import ChatResponse
from app import ui


def test_respond_accepts_empty_optional_fields(monkeypatch):
    def fake_process_support_message(message, order_id, customer_email):
        assert message == "Can I return my shoes?"
        assert order_id is None
        assert customer_email is None
        return ChatResponse(
            response="You can return eligible shoes.",
            action="KNOWLEDGE_RESPONSE",
        )

    monkeypatch.setattr(
        ui,
        "process_support_message",
        fake_process_support_message,
    )

    response = ui.respond(
        "Can I return my shoes?",
        [],
        None,
        None,
    )

    assert "You can return eligible shoes." in response
    assert "Action: KNOWLEDGE_RESPONSE" in response
