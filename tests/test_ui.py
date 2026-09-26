from app.models import ChatResponse
from app import ui


def test_respond_accepts_empty_optional_fields(monkeypatch):
    def fake_process_support_message(message, order_id, customer_email, history):
        assert message == "Can I return my shoes?"
        assert order_id is None
        assert customer_email is None
        assert history == []
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
    assert "Outcome:** Grounded policy answer" in response


def test_respond_passes_conversation_history_to_workflow(monkeypatch):
    history = [
        {"role": "user", "content": "Check order ORD-1001"},
        {"role": "assistant", "content": "Please provide your email."},
    ]

    def fake_process_support_message(message, order_id, customer_email, history):
        assert message == "alice@example.com"
        assert history == [
            {"role": "user", "content": "Check order ORD-1001"},
            {"role": "assistant", "content": "Please provide your email."},
        ]
        return ChatResponse(response="Order ORD-1001 is currently shipped.")

    monkeypatch.setattr(ui, "process_support_message", fake_process_support_message)

    response = ui.respond("alice@example.com", history, None, None)

    assert "currently shipped" in response


def test_submit_message_preserves_a_readable_conversation(monkeypatch):
    monkeypatch.setattr(
        ui,
        "respond",
        lambda *args: "A grounded answer.\n\n---\n**Outcome:** Policy answer",
    )

    cleared_message, history = ui.submit_message(
        "What is the return policy?",
        None,
        None,
        None,
    )

    assert cleared_message == ""
    assert history[0]["role"] == "assistant"
    assert history[-2] == {
        "role": "user",
        "content": "What is the return policy?",
    }
    assert history[-1]["role"] == "assistant"


def test_empty_message_does_not_call_agent(monkeypatch):
    def unexpected_call(*args):
        raise AssertionError("Agent should not run for an empty message")

    monkeypatch.setattr(ui, "respond", unexpected_call)

    cleared_message, history = ui.submit_message("   ", None, None, None)

    assert cleared_message == ""
    assert history == [ui.WELCOME_MESSAGE]


def test_gradio_text_blocks_are_normalized_before_follow_up(monkeypatch):
    browser_history = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What is the status for the order no ORD-1003",
                }
            ],
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "Please provide the email address associated with the order.",
                }
            ],
        },
    ]

    def fake_process_support_message(message, order_id, customer_email, history):
        assert message == "kitty@example.com"
        assert history == [
            {
                "role": "user",
                "content": "What is the status for the order no ORD-1003",
            },
            {
                "role": "assistant",
                "content": "Please provide the email address associated with the order.",
            },
        ]
        return ChatResponse(
            response="Order ORD-1003 is currently processing.",
            action="ORDER_STATUS",
        )

    monkeypatch.setattr(ui, "process_support_message", fake_process_support_message)

    _, history = ui.submit_message(
        "kitty@example.com",
        browser_history,
        None,
        None,
    )

    assert history[-1]["content"].startswith(
        "Order ORD-1003 is currently processing."
    )
