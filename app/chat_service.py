"""Shared entry point for processing support conversations."""

import logging
import time
import uuid
from typing import Any

from app.agent.graph import support_graph
from app.models import ChatResponse


logger = logging.getLogger(__name__)


def process_support_message(
    message: str,
    order_id: str | None = None,
    customer_email: str | None = None,
    history: list[dict[str, Any]] | None = None,
) -> ChatResponse:
    """Run a customer message through the support workflow."""
    request_id = str(uuid.uuid4())
    started_at = time.perf_counter()

    try:
        result = support_graph.invoke(
            {
                "message": message,
                "history": history or [],
                "request_id": request_id,
                "order_id": order_id or None,
                "customer_email": customer_email or None,
                "escalated": False,
            }
        )
    except Exception:
        logger.exception("support_request_failed request_id=%s", request_id)
        return ChatResponse(
            response=(
                "The support service is temporarily unavailable. "
                "Please try again later."
            ),
            action="SERVICE_UNAVAILABLE",
            request_id=request_id,
        )

    elapsed_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        "support_request_completed request_id=%s action=%s escalated=%s "
        "duration_ms=%.1f",
        request_id,
        result.get("action", "UNKNOWN"),
        result.get("escalated", False),
        elapsed_ms,
    )

    return ChatResponse(
        response=result.get(
            "response",
            "I was unable to process that request. Please try again.",
        ),
        action=result.get("action", "UNKNOWN"),
        escalated=result.get("escalated", False),
        request_id=request_id,
        sources=result.get("sources", []),
    )
