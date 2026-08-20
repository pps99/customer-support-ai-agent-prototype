from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    message: str
    request_id: str

    intent: str | None
    confidence: float | None

    order_id: str | None
    customer_email: str | None

    risk_level: str | None
    allowed: bool | None

    retrieved_context: list[dict[str, Any]]
    sources: list[str]

    action: str | None
    escalated: bool

    response: str | None
    error: str | None
