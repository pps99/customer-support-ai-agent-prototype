import logging
import re

from app.config import MIN_INTENT_CONFIDENCE
from app.escalation_service import create_escalation
from app.llm.knowledge_answer import generate_answer_from_context
from app.llm.intent_parser import safe_parse_intent
from app.order_service import get_order, cancel_order
from app.rag.retriever import MAX_RELEVANT_DISTANCE, search_policy
from app.safety import check_action


logger = logging.getLogger(__name__)

ORDER_ID_PATTERN = re.compile(r"\bORD-\d+\b", re.IGNORECASE)
EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)
NON_ORDER_ACTION_PATTERN = re.compile(
    r"\b(refund|return|warranty|damaged|duplicate|compensation|address)\b",
    re.IGNORECASE,
)


def _user_messages(state) -> list[str]:
    messages = [
        item["content"]
        for item in state.get("history", [])
        if item.get("role") == "user" and isinstance(item.get("content"), str)
    ]
    messages.append(state["message"])
    return messages


def _pending_order_intent(state) -> str | None:
    """Recover an order intent when the UI is waiting for a requested field."""
    assistant_messages = [
        item["content"].lower()
        for item in state.get("history", [])
        if item.get("role") == "assistant"
        and isinstance(item.get("content"), str)
    ]
    if not assistant_messages:
        return None

    latest_assistant_message = assistant_messages[-1]
    current_message = state["message"]
    is_order_id_reply = (
        "provide your order id" in latest_assistant_message
        and ORDER_ID_PATTERN.search(current_message)
    )
    is_email_reply = (
        "provide the email address associated with the order"
        in latest_assistant_message
        and EMAIL_PATTERN.search(current_message)
    )
    if not (is_order_id_reply or is_email_reply):
        return None

    conversation = " ".join(_user_messages(state)).lower()
    if re.search(r"\bcancel(?:lation|led|ing)?\b", conversation):
        return "ORDER_CANCEL"
    if re.search(r"\b(status|track|tracking|where|shipped|delivery)\b", conversation):
        return "ORDER_STATUS"
    return None


def _clear_order_intent(message: str) -> str | None:
    """Recognize explicit order actions without depending on model availability."""
    if NON_ORDER_ACTION_PATTERN.search(message):
        return None

    has_order_reference = bool(
        re.search(r"\border\b", message, re.IGNORECASE)
        or ORDER_ID_PATTERN.search(message)
    )
    if not has_order_reference:
        return None

    if re.search(r"\bcancel(?:lation|led|ing)?\b", message, re.IGNORECASE):
        return "ORDER_CANCEL"
    if re.search(
        r"\b(status|track|tracking|where|shipped|delivery)\b",
        message,
        re.IGNORECASE,
    ):
        return "ORDER_STATUS"
    return None


def _apply_user_supplied_order_fields(state) -> None:
    """Carry explicit order fields forward from user-authored messages only."""
    for message in _user_messages(state):
        order_match = ORDER_ID_PATTERN.search(message)
        email_match = EMAIL_PATTERN.search(message)
        if order_match:
            state["order_id"] = order_match.group(0).upper()
        if email_match:
            state["customer_email"] = email_match.group(0)


def parse_request_node(state):
    pending_intent = _pending_order_intent(state)
    if pending_intent:
        state["intent"] = pending_intent
        state["confidence"] = 1.0
        _apply_user_supplied_order_fields(state)
        return state

    clear_order_intent = _clear_order_intent(state["message"])
    if clear_order_intent:
        state["intent"] = clear_order_intent
        state["confidence"] = 1.0
        order_match = ORDER_ID_PATTERN.search(state["message"])
        email_match = EMAIL_PATTERN.search(state["message"])
        if order_match:
            state["order_id"] = order_match.group(0).upper()
        if email_match:
            state["customer_email"] = email_match.group(0)
        return state

    parsed = safe_parse_intent(
        state["message"],
        history=state.get("history"),
    )

    state["intent"] = parsed.intent
    state["confidence"] = parsed.confidence

    if parsed.confidence < MIN_INTENT_CONFIDENCE:
        state["intent"] = "UNKNOWN"

    if parsed.order_id:
        state["order_id"] = parsed.order_id

    if parsed.customer_email:
        state["customer_email"] = parsed.customer_email

    return state


def check_required_fields_node(state):
    intent = state.get("intent")

    if intent in {"ORDER_STATUS", "ORDER_CANCEL"}:
        if not state.get("order_id"):
            state["action"] = "ASK_CLARIFICATION"
            state["response"] = "Please provide your order ID."
            return state

        if not state.get("customer_email"):
            state["action"] = "ASK_CLARIFICATION"
            state["response"] = (
                "Please provide the email address associated with the order."
            )
            return state

    return state


def safety_node(state):
    result = check_action(state["intent"])

    state["allowed"] = result["allowed"]
    state["risk_level"] = result["risk_level"]

    return state


def escalation_node(state):
    ticket = create_escalation(
        reason=state["intent"],
        message=state["message"],
        order_id=state.get("order_id"),
    )

    state["escalated"] = True
    state["action"] = "ESCALATE"
    state["response"] = (
        "This request is outside the prototype's automatic-action boundary. "
        f"Review record {ticket['ticket_id']} was saved locally for demonstration. "
        "No real support team has been notified."
    )

    return state


def rag_node(state):
    try:
        documents = search_policy(state["message"])
    except Exception as exc:
        logger.exception(
            "policy_retrieval_failed request_id=%s",
            state.get("request_id"),
        )
        state["retrieved_context"] = []
        state["sources"] = []
        state["action"] = "KNOWLEDGE_LOOKUP_FAILED"
        state["error"] = str(exc)
        return state

    useful_docs = [
        doc for doc in documents
        if doc["distance"] <= MAX_RELEVANT_DISTANCE
    ]

    state["retrieved_context"] = useful_docs
    state["sources"] = list({
        doc["source"]
        for doc in useful_docs
        if doc.get("source")
    })

    state["action"] = "KNOWLEDGE_LOOKUP"

    return state


def generate_knowledge_response_node(state):
    documents = state.get(
        "retrieved_context",
        []
    )

    if not documents:
        if state.get("action") == "KNOWLEDGE_LOOKUP_FAILED":
            state["response"] = (
                "The policy service is temporarily unavailable. "
                "Please try again or contact support."
            )
            state["action"] = "KNOWLEDGE_SERVICE_UNAVAILABLE"
        else:
            state["response"] = (
                "I could not find enough verified information "
                "to answer that question."
            )
            state["action"] = "KNOWLEDGE_NOT_FOUND"
        return state

    context = "\n\n".join(
        f"[Source: {doc['source']}]\n{doc['text']}"
        for doc in documents
    )

    try:
        response = generate_answer_from_context(
            question=state["message"],
            context=context,
        )

        state["response"] = response
        state["action"] = "KNOWLEDGE_RESPONSE"

    except Exception as exc:
        logger.exception(
            "knowledge_generation_failed request_id=%s",
            state.get("request_id"),
        )
        state["response"] = (
            "I found relevant policy information, "
            "but I was unable to generate a reliable answer. "
            "Please try again or contact support."
        )

        state["action"] = "KNOWLEDGE_RESPONSE_FAILED"
        state["error"] = str(exc)

    return state


def order_lookup_node(state):
    order = get_order(
        state["order_id"],
        state["customer_email"]
    )

    if not order:
        state["response"] = (
            "I could not verify an order "
            "with those details."
        )
        state["action"] = "ORDER_NOT_FOUND"

        return state

    state["response"] = (
        f"Order {order['order_id']} "
        f"is currently {order['status']}."
    )

    state["action"] = "ORDER_STATUS"

    return state


def cancel_order_node(state):
    result = cancel_order(
        state["order_id"],
        state["customer_email"]
    )

    if result["success"]:
        state["response"] = (
            f"Order {state['order_id']} "
            "has been cancelled."
        )

        state["action"] = "ORDER_CANCELLED"

        return state

    if result["reason"] == "ORDER_NOT_CANCELLABLE":
        state["response"] = (
            "This order can no longer be "
            "automatically cancelled."
        )

        state["action"] = "CANCELLATION_BLOCKED"

        return state

    state["response"] = (
        "I could not complete the cancellation."
    )

    state["action"] = "CANCELLATION_FAILED"

    return state


def unknown_node(state):
    state["response"] = (
        "I'm not confident I understand the request. "
        "Could you provide more details?"
    )

    state["action"] = "ASK_CLARIFICATION"

    return state
