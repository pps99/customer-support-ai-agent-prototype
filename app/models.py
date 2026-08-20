from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    customer_email: Optional[str] = None
    order_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    action: Optional[str] = None
    escalated: bool = False
