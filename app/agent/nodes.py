from app.llm.intent_parser import safe_parse_intent
from app.safety import check_action
from app.escalation_service import create_escalation
from app.rag.retriever import search_policy
from app.order_service import get_order, cancel_order
from app.llm.knowledge_answer import generate_answer_from_context


def parse_request_node(state):
    parsed = safe_parse_intent(state["message"])

    state["intent"] = parsed.intent
    state["confidence"] = parsed.confidence

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
        order_id=state.get("order_id")
    )

    state["escalated"] = True
    state["action"] = "ESCALATE"
    state["response"] = (
        f"This request requires manual review. "
        f"Support ticket {ticket['ticket_id']} has been created."
    )

    return state


def rag_node(state):
    try:
        documents = search_policy(state["message"])
    except Exception as exc:
        state["retrieved_context"] = []
        state["sources"] = []
        state["action"] = "KNOWLEDGE_LOOKUP_FAILED"
        state["error"] = str(exc)
        return state

    useful_docs = [
        doc for doc in documents
        if doc["distance"] < 0.8
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
