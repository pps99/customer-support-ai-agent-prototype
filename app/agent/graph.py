from langgraph.graph import END, START, StateGraph

from app.agent.state import AgentState
from app.agent.nodes import (
    parse_request_node,
    check_required_fields_node,
    safety_node,
    escalation_node,
    rag_node,
    generate_knowledge_response_node,
    order_lookup_node,
    cancel_order_node,
    unknown_node,
)


def after_required_fields(state):
    if state.get("action") == "ASK_CLARIFICATION":
        return "end"

    return "safety"


def route_after_safety(state):
    if state.get("allowed") is False:
        return "escalate"

    intent = state.get("intent")

    if intent in {
        "POLICY_INFORMATION",
        "PRODUCT_INFORMATION",
        "RETURN_REQUEST",
    }:
        return "rag"

    if intent == "ORDER_STATUS":
        return "order_lookup"

    if intent == "ORDER_CANCEL":
        return "cancel_order"

    return "unknown"


builder = StateGraph(AgentState)
builder.add_node("parse_request", parse_request_node)
builder.add_node("check_required_fields", check_required_fields_node)
builder.add_node("safety", safety_node)
builder.add_node("escalate", escalation_node)
builder.add_node("rag", rag_node)
builder.add_node("generate_knowledge_response", generate_knowledge_response_node)
builder.add_node("order_lookup", order_lookup_node)
builder.add_node("cancel_order", cancel_order_node)
builder.add_node("unknown", unknown_node)

builder.add_edge(START, "parse_request")
builder.add_edge("parse_request", "check_required_fields")

builder.add_conditional_edges(
    "check_required_fields",
    after_required_fields,
    {
        "safety": "safety",
        "end": END,
    },
)

builder.add_conditional_edges(
    "safety",
    route_after_safety,
    {
        "escalate": "escalate",
        "rag": "rag",
        "order_lookup": "order_lookup",
        "cancel_order": "cancel_order",
        "unknown": "unknown",
    },
)

builder.add_edge("rag", "generate_knowledge_response")
builder.add_edge("generate_knowledge_response", END)
builder.add_edge("order_lookup", END)
builder.add_edge("cancel_order", END)
builder.add_edge("unknown", END)
builder.add_edge("escalate", END)

support_graph = builder.compile()
