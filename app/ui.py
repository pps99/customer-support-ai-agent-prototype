"""Accessible Gradio interface for demonstrating the support agent."""

from typing import Any

import gradio as gr

from app.chat_service import process_support_message


WELCOME_MESSAGE = {
    "role": "assistant",
    "content": (
        "Welcome to the support workflow demo. I can answer from approved "
        "policies, remember verification details across turns, look up orders, "
        "and route sensitive actions to human review. What would you like to try?"
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
    :root {
        --brand-orange: #f97316;
        --brand-amber: #fb923c;
        --ink: #172033;
        --muted: #64748b;
        --panel: rgba(255, 255, 255, 0.92);
    }

    .gradio-container {
        background:
            radial-gradient(circle at 8% 0%, rgba(251, 146, 60, 0.16), transparent 28rem),
            radial-gradient(circle at 96% 18%, rgba(59, 130, 246, 0.10), transparent 24rem),
            #f8fafc;
    }

    .app-shell {
        max-width: 1240px;
        margin: 0 auto;
        padding: 1.25rem 1rem 2.5rem;
    }

    #hero-panel {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 24px;
        background: linear-gradient(135deg, #111827 0%, #1e293b 62%, #7c2d12 140%);
        box-shadow: 0 24px 55px rgba(15, 23, 42, 0.16);
        color: white;
        margin-bottom: 1.1rem;
    }

    #hero-panel::after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: -70px;
        top: -110px;
        border-radius: 999px;
        background: rgba(249, 115, 22, 0.20);
        filter: blur(2px);
    }

    .hero-content { position: relative; z-index: 1; padding: 2rem 2.2rem; }
    .hero-kicker {
        color: #fdba74;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }
    .hero-title {
        margin: 0.35rem 0 0.5rem;
        color: white;
        font-size: clamp(2rem, 4vw, 3.2rem);
        line-height: 1.05;
        letter-spacing: -0.04em;
    }
    .hero-copy {
        max-width: 720px;
        color: #cbd5e1;
        font-size: 1rem;
        line-height: 1.65;
    }
    .capability-row { display: flex; flex-wrap: wrap; gap: 0.55rem; margin-top: 1.2rem; }
    .capability-chip {
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.08);
        color: #f8fafc;
        padding: 0.42rem 0.72rem;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .chat-panel, .control-panel, .scenario-panel {
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        background: var(--panel);
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.07);
        padding: 1rem;
    }
    .control-panel { padding: 1.1rem; }
    .section-eyebrow {
        color: var(--brand-orange);
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.13em;
        text-transform: uppercase;
    }
    .section-title { color: var(--ink); font-size: 1.18rem; font-weight: 800; margin-top: 0.15rem; }
    .section-copy { color: var(--muted); font-size: 0.88rem; margin-top: 0.2rem; }

    #support-chat {
        border: 0;
        border-radius: 16px;
        background: #f8fafc;
        margin-top: 0.6rem;
    }
    #message-box textarea { font-size: 1rem; }
    #send-button { font-weight: 800; box-shadow: 0 8px 18px rgba(249, 115, 22, 0.22); }

    .demo-step {
        display: grid;
        grid-template-columns: 2rem 1fr;
        gap: 0.7rem;
        padding: 0.75rem 0;
        border-bottom: 1px solid #e2e8f0;
    }
    .demo-step:last-child { border-bottom: 0; }
    .step-number {
        display: grid;
        place-items: center;
        width: 1.8rem;
        height: 1.8rem;
        border-radius: 9px;
        background: #fff7ed;
        color: #c2410c;
        font-size: 0.74rem;
        font-weight: 900;
    }
    .step-title { color: var(--ink); font-size: 0.9rem; font-weight: 800; }
    .step-copy { color: var(--muted); font-size: 0.79rem; line-height: 1.45; }
    .safety-note {
        margin-top: 0.8rem;
        border: 1px solid #fed7aa;
        border-radius: 14px;
        background: #fff7ed;
        color: #9a3412;
        padding: 0.8rem 0.9rem;
        font-size: 0.82rem;
        line-height: 1.5;
    }
    .scenario-panel { margin-top: 1rem; }

    @media (max-width: 760px) {
        .app-shell { padding: 0.7rem 0.4rem 1.5rem; }
        .hero-content { padding: 1.5rem 1.25rem; }
        .chat-panel, .control-panel, .scenario-panel { border-radius: 16px; }
    }
"""

HERO_HTML = """
<div class="hero-content">
  <div class="hero-kicker">Sunnystep customer care · AI-assisted</div>
  <h1 class="hero-title">How can we help?</h1>
  <div class="hero-copy">
    Get answers about footwear policies, check an order, or ask us to route a
    sensitive issue to the right person.
  </div>
  <div class="capability-row">
    <span class="capability-chip">Policy answers</span>
    <span class="capability-chip">Order tracking</span>
    <span class="capability-chip">Cancellation checks</span>
    <span class="capability-chip">Human support</span>
  </div>
</div>
"""

SUPPORT_OPTIONS_HTML = """
<div>
  <div class="section-eyebrow">Support options</div>
  <div class="section-title">What can I help with?</div>
  <div class="section-copy">Choose a starting point or write your own question.</div>
  <div class="demo-step">
    <div class="step-number">01</div>
    <div><div class="step-title">Returns and policies</div>
    <div class="step-copy">Get answers based on our approved support policies.</div></div>
  </div>
  <div class="demo-step">
    <div class="step-number">02</div>
    <div><div class="step-title">Track an order</div>
    <div class="step-copy">Verify your sample order ID and email to check its status.</div></div>
  </div>
  <div class="demo-step">
    <div class="step-number">03</div>
    <div><div class="step-title">Cancellation eligibility</div>
    <div class="step-copy">Check whether an order is still eligible for cancellation.</div></div>
  </div>
  <div class="demo-step">
    <div class="step-number">04</div>
    <div><div class="step-title">Complex issues</div>
    <div class="step-copy">Route refunds, damaged items, and account changes for review.</div></div>
  </div>
</div>
"""


def _content_text(content: Any) -> str:
    """Convert Gradio's normalized text blocks back into plain chat text."""
    if isinstance(content, str):
        return content
    if isinstance(content, dict) and content.get("type") == "text":
        text = content.get("text")
        return text if isinstance(text, str) else ""
    if isinstance(content, list):
        return "\n".join(
            text for item in content if (text := _content_text(item))
        )
    return ""


def normalize_chat_history(
    history: list[dict[str, Any]] | None,
) -> list[dict[str, str]]:
    """Keep supported roles and flatten browser-round-tripped message content."""
    normalized = []
    for item in history or []:
        role = item.get("role")
        content = _content_text(item.get("content"))
        if role in {"user", "assistant"} and content:
            normalized.append({"role": role, "content": content})
    return normalized


def respond(
    message: str,
    history: list[dict[str, Any]],
    order_id: str | None,
    customer_email: str | None,
) -> str:
    """Handle one support message and format its evidence for the UI."""
    result = process_support_message(
        message=message,
        order_id=(order_id or "").strip() or None,
        customer_email=(customer_email or "").strip() or None,
        history=normalize_chat_history(history),
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
    current_history = normalize_chat_history(history) or [WELCOME_MESSAGE]
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
            gr.HTML(HERO_HTML, elem_id="hero-panel")

            with gr.Row():
                with gr.Column(
                    scale=7,
                    min_width=480,
                    elem_classes="chat-panel",
                ):
                    gr.HTML(
                        """
                        <div class="section-eyebrow">Live workflow</div>
                        <div class="section-title">Support conversation</div>
                        <div class="section-copy">
                          Each answer exposes its decision outcome, evidence, and request ID.
                        </div>
                        """
                    )
                    chatbot = gr.Chatbot(
                        value=[WELCOME_MESSAGE],
                        show_label=False,
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
                        elem_id="message-box",
                    )
                    with gr.Row():
                        send = gr.Button(
                            "Send message →",
                            variant="primary",
                            elem_id="send-button",
                        )
                        clear = gr.Button("Clear conversation", variant="secondary")

                with gr.Column(
                    scale=4,
                    min_width=320,
                    elem_classes="control-panel",
                ):
                    gr.HTML(SUPPORT_OPTIONS_HTML)

                    with gr.Accordion("Order verification", open=True):
                        order_id = gr.Textbox(
                            label="Order ID",
                            placeholder="ORD-1001",
                            info="Optional shortcut; the chat can also ask for it.",
                        )
                        customer_email = gr.Textbox(
                            label="Customer email",
                            placeholder="alice@example.com",
                            type="email",
                            info="Use sample data only.",
                        )
                        gr.Markdown(
                            "**Sample identities**  \n"
                            "`ORD-1001` · `alice@example.com`  \n"
                            "`ORD-1002` · `bob@example.com`"
                        )

                    gr.HTML(
                        """
                        <div class="safety-note">
                          <strong>Safety boundary</strong><br>
                          Refunds, compensation, warranty decisions, damaged items,
                          duplicate charges, and address changes always require human review.
                          This prototype creates a local demonstration record only.
                        </div>
                        """
                    )
                    gr.Markdown("[Open interactive API documentation →](/docs)")

            with gr.Column(elem_classes="scenario-panel"):
                gr.HTML(
                    """
                    <div class="section-eyebrow">Quick starts</div>
                    <div class="section-title">Try a common support request</div>
                    <div class="section-copy">
                      Select an example to fill the form, then send it when you are ready.
                    </div>
                    """
                )
                gr.Examples(
                    examples=[
                        [
                            "Can I return shoes after trying them outdoors?",
                            "",
                            "",
                        ],
                        ["What is the status of my order?", "", ""],
                        [
                            "Cancel my shipped order",
                            "ORD-1001",
                            "alice@example.com",
                        ],
                        [
                            "Refund my order immediately",
                            "ORD-1001",
                            "alice@example.com",
                        ],
                        [
                            "My shoes arrived damaged. Send me a replacement.",
                            "ORD-1001",
                            "alice@example.com",
                        ],
                        ["Do you ship internationally, and how long does it take?", "", ""],
                    ],
                    example_labels=[
                        "Returns after outdoor wear",
                        "Track an order",
                        "Cancel a shipped order",
                        "Request a refund",
                        "Report damaged shoes",
                        "International shipping",
                    ],
                    inputs=[message, order_id, customer_email],
                    label="Example questions",
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
