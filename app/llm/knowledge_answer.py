import os

from app.llm.client import get_openai_client


def generate_answer_from_context(
    question: str,
    context: str,
) -> str:
    client = get_openai_client()

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6-luna",
    )

    prompt = f"""
                You are a customer support assistant for a footwear retailer.

                Answer the customer's question using ONLY the policy context below.

                Rules:
                - Do not use outside knowledge.
                - Do not invent policies, prices, timelines, or eligibility.
                - Do not claim that an action was completed unless the application actually performed it.
                - If the context is insufficient, say that the available policy does not provide enough information.
                - Keep the response concise and helpful.

                Policy context:
                {context}

                Customer question:
                {question}
                """

    response = client.responses.create(
        model=model,
        input=prompt,
    )

    return response.output_text.strip()
