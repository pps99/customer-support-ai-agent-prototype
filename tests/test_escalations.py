import json

from app.escalation_service import create_escalation


def test_escalation_is_persisted_for_human_review(tmp_path):
    escalation_file = tmp_path / "escalations.json"

    ticket = create_escalation(
        reason="REFUND_REQUEST",
        message="Please refund my order",
        order_id="ORD-1001",
        data_file=escalation_file,
    )

    stored = json.loads(escalation_file.read_text(encoding="utf-8"))
    assert stored[0]["ticket_id"] == ticket["ticket_id"]
    assert stored[0]["status"] == "queued"
    assert stored[0]["reason"] == "REFUND_REQUEST"
