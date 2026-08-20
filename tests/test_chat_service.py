from app import chat_service


class FailingGraph:
    def invoke(self, state):
        raise RuntimeError("unexpected workflow failure")


def test_unexpected_workflow_failure_returns_safe_response(monkeypatch):
    monkeypatch.setattr(chat_service, "support_graph", FailingGraph())

    result = chat_service.process_support_message("Hello")

    assert result.action == "SERVICE_UNAVAILABLE"
    assert result.request_id is not None
    assert "unexpected workflow failure" not in result.response
