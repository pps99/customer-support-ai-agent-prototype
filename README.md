# Footwear Support Agent

A small FastAPI application that handles footwear customer-support requests.
It includes order lookup and cancellation logic, safety-based escalation, and a
LangGraph workflow with policy retrieval from ChromaDB.

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
└── test_orders.py
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
uvicorn app.main:app --reload
```

Open the browser chat interface at `http://127.0.0.1:8000/ui`.

Interactive API documentation remains available at
`http://127.0.0.1:8000/docs`.

## Test

```bash
python -m pytest
```
