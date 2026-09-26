from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    customer_email: str | None = None
    order_id: str | None = None
    history: list[ChatMessage] = Field(default_factory=list)


class OrderLookupRequest(BaseModel):
    order_id: str
    customer_email: str


class ChatResponse(BaseModel):
    response: str
    action: str | None = None
    escalated: bool = False
    request_id: str | None = None
    sources: list[str] = Field(default_factory=list)
