import json
import logging
import os
from typing import Literal

from pydantic import BaseModel, Field

from app.llm.client import get_openai_client


logger = logging.getLogger(__name__)

IntentType = Literal[
    "PRODUCT_INFORMATION",
    "POLICY_INFORMATION",
    "ORDER_STATUS",
    "ORDER_CANCEL",
    "RETURN_REQUEST",
    "REFUND_REQUEST",
    "DAMAGED_ITEM",
    "WARRANTY_CLAIM",
    "DUPLICATE_CHARGE",
    "COMPENSATION_REQUEST",
    "CHANGE_DELIVERY_ADDRESS",
    "UNKNOWN",
]


class ParsedIntent(BaseModel):
    intent: IntentType
    order_id: str | None = None
    customer_email: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


def parse_intent(message: str) -> ParsedIntent:
    client = get_openai_client()

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6-luna"
    )

    prompt = f"""
                You classify customer-support requests for a footwear retailer.

                Allowed intents:

                - PRODUCT_INFORMATION
                - POLICY_INFORMATION
                - ORDER_STATUS
                - ORDER_CANCEL
                - RETURN_REQUEST
                - REFUND_REQUEST
                - DAMAGED_ITEM
                - WARRANTY_CLAIM
                - DUPLICATE_CHARGE
                - COMPENSATION_REQUEST
                - CHANGE_DELIVERY_ADDRESS
                - UNKNOWN

                Rules:

                1. Extract order_id only if it is explicitly present.
                2. Extract customer_email only if it is explicitly present.
                3. Never invent missing information.
                4. If the request is ambiguous or does not match an intent, use UNKNOWN.
                5. confidence must be between 0.0 and 1.0.
                6. Return ONLY valid JSON.

                Return JSON in exactly this format:

                {{
                    "intent": "ORDER_STATUS",
                    "order_id": "ORD-1001",
                    "customer_email": "alice@example.com",
                    "confidence": 0.95
                }}

                If a value is missing, return null.

                Customer message:

                {message}
            """

    response = client.responses.create(
        model=model,
        input=prompt,
    )

    raw_text = response.output_text.strip()

    data = json.loads(raw_text)

    return ParsedIntent.model_validate(data)


def safe_parse_intent(message: str) -> ParsedIntent:
    try:
        return parse_intent(message)

    except Exception:
        logger.exception("intent_parsing_failed")
        return ParsedIntent(
            intent="UNKNOWN",
            order_id=None,
            customer_email=None,
            confidence=0.0
        )
