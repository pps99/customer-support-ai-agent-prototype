from typing import TypedDict, Optional, Any


class AgentState(TypedDict, total=False):
    message: str

    intent: Optional[str]
    confidence: Optional[float]

    order_id: Optional[str]
    customer_email: Optional[str]

    risk_level: Optional[str]
    allowed: Optional[bool]

    retrieved_context: list[dict[str, Any]]
    sources: list[str]

    action: Optional[str]
    escalated: bool

    response: Optional[str]
    error: Optional[str]
