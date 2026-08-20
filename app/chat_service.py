"""Shared entry point for processing support conversations."""

from app.agent.graph import support_graph
from app.models import ChatResponse


def process_support_message(
    message: str,
    order_id: str | None = None,
    customer_email: str | None = None,
) -> ChatResponse:
    """Run a customer message through the support workflow."""
    result = support_graph.invoke(
        {
            "message": message,
            "order_id": order_id or None,
            "customer_email": customer_email or None,
            "escalated": False,
        }
    )

    return ChatResponse(
        response=result.get(
            "response",
            "I was unable to process that request. Please try again.",
        ),
        action=result.get("action", "UNKNOWN"),
        escalated=result.get("escalated", False),
    )
