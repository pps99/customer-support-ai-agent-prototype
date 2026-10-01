# Footwear Support Agent

A working prototype that answers from approved footwear policies, retrieves
verified order information, persists eligible cancellations, and sends unsafe
requests to a durable local human-review queue. FastAPI provides the API and
Gradio provides the browser interface.

## Architecture

```text
FastAPI / Gradio
       │
       ▼
 shared chat service ── request ID + outcome logging
       │
       ▼
 intent parsing ── confidence gate ── required-field checks
       │
       ▼
 deterministic safety policy
   ├── unsafe action ──► persistent escalation queue
   ├── order action ───► verified JSON order service
   ├── knowledge ──────► Chroma retrieval ─► grounded response
   └── uncertain ─────► clarification
```

Deterministic application code recognizes clear order-status/cancellation flows,
collects requested verification fields across turns, and enforces safety
boundaries. The language model classifies less explicit requests and writes
grounded policy responses; it does not decide whether a sensitive action is
allowed.

### Agent node workflow

```mermaid
flowchart TD
    startNode([START]) --> parseRequest[parse_request]
    parseRequest --> requiredFields[check_required_fields]

    requiredFields -->|Missing order ID or email| clarificationExit([END: clarification])
    requiredFields -->|Required fields ready| safetyCheck[safety]

    safetyCheck -->|Unsafe action| escalation[escalate]
    safetyCheck -->|Policy, product, or return| policyRetrieval[rag]
    safetyCheck -->|Order status| orderLookup[order_lookup]
    safetyCheck -->|Order cancellation| cancelOrder[cancel_order]
    safetyCheck -->|Unknown intent| unknownRequest[unknown]

    policyRetrieval --> knowledgeResponse[generate_knowledge_response]

    escalation --> terminalNode([END])
    knowledgeResponse --> terminalNode
    orderLookup --> terminalNode
    cancelOrder --> terminalNode
    unknownRequest --> terminalNode
```

Every branch in this diagram corresponds to a node or conditional route in
`app/agent/graph.py`. Unsafe requests terminate through escalation, while
missing identity details terminate with a clarification rather than an action.

## Project structure

```text
app/
├── agent/             # LangGraph state, nodes, and routing
├── llm/               # OpenAI client and prompt helpers
├── rag/               # Policy ingestion and semantic retrieval
├── config.py          # Shared paths and settings
├── chat_service.py    # Shared agent entry point for API and UI
├── main.py            # FastAPI endpoints
├── models.py          # API request and response models
├── ui.py              # Gradio chat interface
├── order_service.py   # Order lookup and cancellation rules
├── escalation_service.py
└── safety.py
data/
├── orders.json
└── policies/
tests/
├── test_orders.py
├── test_nodes.py
├── test_escalations.py
├── test_chat_service.py
└── test_ui.py
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy your local configuration into `.env` and provide an OpenAI API key:

```dotenv
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-5.6-luna
```

Build the local policy index before using knowledge lookup:

```bash
python -c "from app.rag.ingest import ingest; ingest()"
```

## Run

```bash
# uvicorn app.main:app --reload
python -m uvicorn app.main:app --reload
```

Open the browser chat interface at `http://127.0.0.1:8000/ui`.

Interactive API documentation remains available at
`http://127.0.0.1:8000/docs`.

For multi-turn API conversations, send the prior `user` and `assistant`
messages in the optional `history` array:

```json
{
  "message": "alice@example.com",
  "history": [
    {"role": "user", "content": "Check status for ORD-1001"},
    {"role": "assistant", "content": "Please provide your email."}
  ]
}
```

## Test

```bash
python -m pytest
```

The current suite contains 25 deterministic tests. See [TESTING.md](TESTING.md)
for successful cases, discovered failures, and remaining evaluation gaps.
