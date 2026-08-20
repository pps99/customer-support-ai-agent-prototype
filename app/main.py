from fastapi import FastAPI, HTTPException

from app.agent.graph import support_graph
from app.models import ChatRequest, ChatResponse
from app.order_service import get_order


app = FastAPI(title="Footwear Customer Support Agent")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/orders/{order_id}")
def order_lookup(order_id: str, email: str):
    order = get_order(order_id, email)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found or customer identity does not match",
        )

    return order


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Process a support message through the complete agent workflow."""
    initial_state = {
        "message": request.message,
        "order_id": request.order_id,
        "customer_email": request.customer_email,
        "escalated": False,
    }

    result = support_graph.invoke(initial_state)

    return ChatResponse(
        response=result.get(
            "response",
            "I was unable to process that request. Please try again.",
        ),
        action=result.get("action", "UNKNOWN"),
        escalated=result.get("escalated", False),
    )
