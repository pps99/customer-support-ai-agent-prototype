import uuid


def create_escalation(
    reason: str,
    message: str,
    order_id: str | None = None,
) -> dict[str, str | None]:
    ticket_id = "ESC-" + str(uuid.uuid4())[:8]

    return {
        "ticket_id": ticket_id,
        "status": "queued",
        "reason": reason,
        "order_id": order_id,
        "message": message,
    }
