HIGH_RISK_ACTIONS = {
    "REFUND_REQUEST",
    "COMPENSATION_REQUEST",
    "CHANGE_DELIVERY_ADDRESS",
    "DAMAGED_ITEM",
    "WARRANTY_CLAIM",
    "DUPLICATE_CHARGE",
}


def check_action(intent: str) -> dict[str, bool | str | None]:
    if intent in HIGH_RISK_ACTIONS:
        return {
            "allowed": False,
            "risk_level": "HIGH",
            "reason": "HUMAN_REVIEW_REQUESTED"
        }

    return {
        "allowed": True,
        "risk_level": "LOW",
        "reason": None
    }
