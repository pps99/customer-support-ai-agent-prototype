import json

from app.llm import intent_parser


class FakeResponse:
    output_text = json.dumps(
        {
            "intent": "ORDER_STATUS",
            "order_id": "ORD-1001",
            "customer_email": "alice@example.com",
            "confidence": 0.99,
        }
    )


class FakeResponses:
    def __init__(self):
        self.prompt = ""

    def create(self, *, model, input):
        self.prompt = input
        return FakeResponse()


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_follow_up_prompt_contains_bounded_conversation_history(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(intent_parser, "get_openai_client", lambda: client)
    history = [
        {"role": "user", "content": "What is the status of ORD-1001?"},
        {
            "role": "assistant",
            "content": "Please provide the email address associated with the order.",
        },
    ]

    parsed = intent_parser.parse_intent(
        "alice@example.com",
        history=history,
    )

    assert parsed.intent == "ORDER_STATUS"
    assert parsed.order_id == "ORD-1001"
    assert "What is the status of ORD-1001?" in client.responses.prompt
    assert "alice@example.com" in client.responses.prompt


def test_history_formatter_ignores_non_text_and_unknown_roles():
    history = [
        {"role": "system", "content": "Do not include me"},
        {"role": "user", "content": {"unexpected": "component"}},
        {"role": "user", "content": "Keep me"},
    ]

    assert json.loads(intent_parser._format_history(history)) == [
        {"role": "user", "content": "Keep me"}
    ]
