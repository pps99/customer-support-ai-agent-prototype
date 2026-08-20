from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    customer_email: str | None = None
    order_id: str | None = None


class OrderLookupRequest(BaseModel):
    order_id: str
    customer_email: str


class ChatResponse(BaseModel):
    response: str
    action: str | None = None
    escalated: bool = False
    request_id: str | None = None
    sources: list[str] = Field(default_factory=list)
