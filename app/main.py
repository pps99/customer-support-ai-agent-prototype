import logging

import gradio as gr
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from app.chat_service import process_support_message
from app.models import ChatRequest, ChatResponse, OrderLookupRequest
from app.order_service import get_order
from app.rag.retriever import collection
from app.ui import create_ui


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
app = FastAPI(title="Footwear Customer Support Agent")


@app.get("/", include_in_schema=False)
def home() -> RedirectResponse:
    """Open the browser chat interface by default."""
    return RedirectResponse(url="/ui")


@app.get("/health")
def health_check() -> dict[str, str | int]:
    policy_documents = collection.count()
    return {
        "status": "ok" if policy_documents else "degraded",
        "policy_documents": policy_documents,
    }


@app.post("/orders/lookup")
def order_lookup(request: OrderLookupRequest):
    """Look up an order without placing customer email in the request URL."""
    order = get_order(request.order_id, request.customer_email)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found or customer identity does not match",
        )

    return order


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Process a support message through the complete agent workflow."""
    return process_support_message(
        message=request.message,
        order_id=request.order_id,
        customer_email=request.customer_email,
    )


app = gr.mount_gradio_app(app, create_ui(), path="/ui")
