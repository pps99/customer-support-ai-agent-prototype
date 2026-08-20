"""Gradio interface for the footwear support agent."""

from typing import Any

import gradio as gr

from app.chat_service import process_support_message


def respond(
    message: str,
    history: list[dict[str, Any]],
    order_id: str | None,
    customer_email: str | None,
) -> str:
    """Handle one message submitted through the browser UI."""
    del history  # The graph currently handles each request independently.

    result = process_support_message(
        message=message,
        order_id=(order_id or "").strip() or None,
        customer_email=(customer_email or "").strip() or None,
    )

    details = f"Action: {result.action or 'UNKNOWN'}"
    if result.escalated:
        details += " · Escalated to support"
    if result.sources:
        details += f" · Sources: {', '.join(result.sources)}"
    if result.request_id:
        details += f" · Request: {result.request_id[:8]}"

    return f"{result.response}\n\n_{details}_"


def create_ui() -> gr.ChatInterface:
    """Build the browser-based support chat interface."""
    return gr.ChatInterface(
        fn=respond,
        title="Footwear Support Agent",
        description=(
            "Ask about orders, cancellations, returns, shipping, sizing, "
            "warranties, or footwear products."
        ),
        additional_inputs=[
            gr.Textbox(label="Order ID", placeholder="ORD-1001"),
            gr.Textbox(
                label="Customer email",
                placeholder="alice@example.com",
            ),
        ],
        examples=[
            ["Can I return my shoes?", "", ""],
            ["Where is my order?", "ORD-1001", "alice@example.com"],
            ["Cancel my order", "ORD-1002", "bob@example.com"],
        ],
    )
