from typing import Literal, Optional
from pydantic import BaseModel, Field
import json
import os

from app.llm.client import get_openai_client


IntentType = Literal[
    "PRODUCT_INFORMATION",
    "POLICY_INFORMATION",
    "ORDER_STATUS",
    "ORDER_CANCEL",
    "RETURN_REQUEST",
    "REFUND_REQUEST",
    "DAMAGED_ITEM",
    "UNKNOWN"
]


class ParsedIntent(BaseModel):
    intent: IntentType
    order_id: Optional[str] = None
    customer_email: Optional[str] = None
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
        return ParsedIntent(
            intent="UNKNOWN",
            order_id=None,
            customer_email=None,
            confidence=0.0
        )
