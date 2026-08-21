"""Accessible Gradio interface for demonstrating the support agent."""

from typing import Any

import gradio as gr

from app.chat_service import process_support_message


WELCOME_MESSAGE = {
    "role": "assistant",
    "content": (
        "Hello! I can explain approved footwear policies, look up verified "
        "orders, check cancellation eligibility, and route sensitive requests "
        "to a prototype review queue. What would you like help with?"
    ),
}

ACTION_LABELS = {
    "ASK_CLARIFICATION": "More information needed",
    "CANCELLATION_BLOCKED": "Cancellation safely blocked",
    "CANCELLATION_FAILED": "Cancellation not completed",
    "ESCALATE": "Saved for prototype human review",
    "KNOWLEDGE_NOT_FOUND": "No verified policy found",
    "KNOWLEDGE_RESPONSE": "Grounded policy answer",
    "KNOWLEDGE_SERVICE_UNAVAILABLE": "Policy service unavailable",
    "ORDER_CANCELLED": "Verified order cancelled",
    "ORDER_NOT_FOUND": "Order could not be verified",
    "ORDER_STATUS": "Verified order lookup",
    "SERVICE_UNAVAILABLE": "Support service unavailable",
}

UI_THEME = gr.themes.Soft(primary_hue="orange", neutral_hue="slate")
UI_CSS = """
    .app-shell { max-width: 1180px; margin: 0 auto; }
    .hero { padding: 0.5rem 0 0.25rem; }
    .demo-note { border-left: 4px solid #f97316; padding-left: 1rem; }
"""


def respond(
    message: str,
    history: list[dict[str, Any]],
    order_id: str | None,
    customer_email: str | None,
) -> str:
    """Handle one support message and format its evidence for the UI."""
    del history  # The workflow currently treats each message independently.

    result = process_support_message(
        message=message,
        order_id=(order_id or "").strip() or None,
        customer_email=(customer_email or "").strip() or None,
    )

    action = result.action or "UNKNOWN"
    details = [f"**Outcome:** {ACTION_LABELS.get(action, action)}"]
    if result.sources:
        details.append(f"**Sources:** {', '.join(result.sources)}")
    if result.request_id:
        details.append(f"**Request ID:** `{result.request_id[:8]}`")

    return f"{result.response}\n\n---\n" + "  \n".join(details)


def submit_message(
    message: str,
    history: list[dict[str, Any]] | None,
    order_id: str | None,
    customer_email: str | None,
) -> tuple[str, list[dict[str, Any]]]:
    """Append a user message and the agent response to chat history."""
    clean_message = (message or "").strip()
    current_history = list(history or [WELCOME_MESSAGE])
    if not clean_message:
        return "", current_history

    answer = respond(
        clean_message,
        current_history,
        order_id,
        customer_email,
    )
    current_history.extend(
        [
            {"role": "user", "content": clean_message},
            {"role": "assistant", "content": answer},
        ]
    )
    return "", current_history


def reset_chat() -> tuple[list[dict[str, str]], str]:
    """Reset the conversation while retaining optional order details."""
    return [WELCOME_MESSAGE], ""


def create_ui() -> gr.Blocks:
    """Build the recruiter-friendly browser demonstration."""
    with gr.Blocks(
        title="Footwear Support Agent — Engineering Prototype",
        fill_width=True,
    ) as demo:
        with gr.Column(elem_classes="app-shell"):
            gr.Markdown(
                """
                # Footwear Support Agent

                **Engineering prototype · Grounded answers · Deterministic safety controls**

                Ask a general policy question, verify a sample order, or try a
                sensitive request to see when the system refuses or escalates.
                """,
                elem_classes="hero",
            )

            with gr.Row():
                with gr.Column(scale=7, min_width=480):
                    chatbot = gr.Chatbot(
                        value=[WELCOME_MESSAGE],
                        label="Support conversation",
                        height=520,
                        layout="bubble",
                        buttons=["copy"],
                        placeholder="Start with an example or type a question below.",
                        elem_id="support-chat",
                    )
                    message = gr.Textbox(
                        label="Your question",
                        placeholder="For example: What is your return policy?",
                        lines=2,
                        max_lines=5,
                        autofocus=True,
                        submit_btn=False,
                        info="Do not enter real customer or payment information.",
                    )
                    with gr.Row():
                        send = gr.Button("Send message", variant="primary")
                        clear = gr.Button("Clear conversation", variant="secondary")

                with gr.Column(scale=4, min_width=320):
                    gr.Markdown(
                        """
                        ## Quick demo

                        1. Select an example below.
                        2. Add sample order details only when needed.
                        3. Inspect the outcome, policy sources, and request ID.
                        """,
                        elem_classes="demo-note",
                    )

                    with gr.Accordion("Sample order verification", open=True):
                        order_id = gr.Textbox(
                            label="Order ID",
                            placeholder="ORD-1001",
                            info="Required for status and cancellation requests.",
                        )
                        customer_email = gr.Textbox(
                            label="Customer email",
                            placeholder="alice@example.com",
                            type="email",
                            info="Must exactly match the sample order.",
                        )
                        gr.Markdown(
                            "Sample records: `ORD-1001 / alice@example.com` "
                            "(shipped) and `ORD-1002 / bob@example.com` "
                            "(processing)."
                        )

                    gr.Markdown(
                        """
                        ### Safety boundary

                        - Refunds, compensation, warranty decisions, damaged
                          items, duplicate charges, and address changes are not
                          automated.
                        - Escalations are saved locally for demonstration; no
                          real support team is notified.
                        - Order actions require matching sample credentials.

                        [Open API documentation](/docs)
                        """
                    )

            gr.Markdown("## Suggested scenarios")
            gr.Examples(
                examples=[
                    ["What is your return policy?", "", ""],
                    ["Where is my order?", "ORD-1001", "alice@example.com"],
                    ["Cancel my shipped order", "ORD-1001", "alice@example.com"],
                    ["Refund my order immediately", "ORD-1001", "alice@example.com"],
                ],
                example_labels=[
                    "Grounded policy answer",
                    "Verified order lookup",
                    "Safety rule blocks cancellation",
                    "Sensitive action goes to review",
                ],
                inputs=[message, order_id, customer_email],
                label="Click a scenario to fill the form, then send it.",
            )

        submit_inputs = [message, chatbot, order_id, customer_email]
        submit_outputs = [message, chatbot]
        send.click(
            fn=submit_message,
            inputs=submit_inputs,
            outputs=submit_outputs,
            api_name="chat",
        )
        message.submit(
            fn=submit_message,
            inputs=submit_inputs,
            outputs=submit_outputs,
        )
        clear.click(
            fn=reset_chat,
            outputs=[chatbot, message],
            queue=False,
        )

    return demo
