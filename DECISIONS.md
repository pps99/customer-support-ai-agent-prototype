# Decision Log

## D1 — Deterministic authorization after probabilistic classification

**Decision:** Use the model to classify requests and draft grounded answers, but
use application code to authorize actions.

**Rejected:** Allowing the model to call refund, address-change, or compensation
tools directly.

**Reason and trade-off:** Deterministic rules are testable and prevent prompt
wording from bypassing financial and identity controls. This is less flexible
than model-only routing and requires the intent taxonomy to stay aligned with
the graph.

## D2 — Narrow automatic-action boundary

**Decision:** Automatically cancel only a verified order whose persisted status
is exactly `processing`. Escalate refunds, compensation, damaged items, warranty
decisions, duplicate charges, and delivery-address changes.

**Rejected:** Automating all actions described by a customer or treating policy
eligibility as authorization.

**Evidence:** The supplied policies identify financial, authorization, identity,
and evidence-dependent outcomes as mandatory human-review cases.

## D3 — Ground answers in retrieved policy text

**Decision:** Retrieve approved Markdown chunks from ChromaDB and instruct the
model to answer only from that context.

**Rejected:** Answering policy questions from the model's general knowledge or
putting every policy into every prompt.

**Trade-off:** Retrieval reduces unsupported context and is easy to update, but
introduces embedding availability and relevance-threshold failure modes.

## D4 — Clarify uncertainty instead of guessing

**Decision:** Require order ID and email for order operations and convert intent
confidence below `0.65` to `UNKNOWN`.

**Rejected:** Guessing missing identifiers or executing a low-confidence action.

**Trade-off:** This can ask unnecessary follow-up questions, but false negatives
are safer than unauthorized mutations.

## D5 — Portable local persistence for the prototype

**Decision:** Use atomic JSON replacement for orders and a durable local JSON
escalation queue.

**Rejected:** Keeping mutations only in memory, which allowed the UI to claim a
cancellation that vanished on the next request. A hosted database and ticketing
system were also rejected for this time-bounded, portable prototype.

**Trade-off:** The local store demonstrates truthful outcomes across restarts but
is not suitable for multiple processes or production PII.

## D6 — One shared service for API and UI

**Decision:** Both FastAPI and Gradio call `process_support_message`.

**Rejected:** Duplicating workflow logic in each interface.

**Reason:** A shared boundary gives both interfaces the same safety behavior,
request IDs, sources, and failure containment.

## D7 — Explicit failure categories and minimal observability

**Decision:** Distinguish no relevant knowledge from retrieval failure and
unexpected workflow failure. Log request ID, action, escalation flag, latency,
and exception trace without logging customer message content.

**Rejected:** Swallowing every failure as `UNKNOWN` or returning stack traces.

**Trade-off:** Standard logs are enough to demonstrate the design but still need
a production metrics/tracing backend and retention policy.
