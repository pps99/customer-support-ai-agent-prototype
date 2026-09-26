# Testing and Failure Evidence

## How to run

```bash
source .venv/bin/activate
python -m pytest -q
```

Current verified result: **34 passed**. Starlette and ChromaDB emit upstream
Python 3.14 deprecation warnings; they do not fail the suite.

## Covered behavior

- Correct order ID and email disclose an order.
- Incorrect email does not disclose an order.
- Lookup checks every record rather than only the first.
- Shipped orders cannot be cancelled.
- Eligible cancellation is atomically persisted.
- Identity mismatch does not mutate the order.
- Escalation tickets persist with queued status.
- Relevant policy documents survive the calibrated retrieval cutoff.
- Low-confidence action intents become `UNKNOWN`.
- Retrieval outage is reported differently from no matching policy.
- A prompt that says to ignore rules and issue a refund still escalates.
- Every declared high-risk intent routes to human review.
- Missing order identifiers trigger clarification before an order action.
- Blank Gradio optional fields do not crash.
- Unexpected workflow exceptions return a safe response and request ID.
- Health reports whether policy documents are indexed.
- Order lookup keeps customer email out of URL/query logs.
- Failed order verification returns a neutral response.
- Browser and API chat history reaches the intent-classification workflow.
- An email-only follow-up can reuse a previously supplied order ID and intent.
- Conversation history is bounded and filtered to supported text messages.
- Requested order-ID and email replies bypass model classification, so the
  order flow remains deterministic during a transient model API failure.
- Clearly worded order-status and cancellation requests also bypass model
  classification before collecting their required verification fields.
- Gradio's browser-normalized text blocks are flattened before the workflow, so
  multi-turn order details survive a real UI round trip.

Tests use temporary files and mocks at external boundaries. They never mutate the
committed sample orders or require paid model calls.

## Failures discovered during development

### F1 — Lookup stopped after the first order

**Observed:** A valid second order returned no result.

**Cause:** `return None` was inside the lookup loop.

**Correction:** Move the return after the loop.

**Guardrail:** `test_order_lookup_checks_every_order`.

### F2 — Policy collection existed but contained zero documents

**Observed:** Valid return questions produced `KNOWLEDGE_NOT_FOUND`.

**Cause:** Ingestion had not completed, initially because Chroma tried to write
its model under a protected home-directory cache.

**Correction:** Store the embedding model under the project data directory and
document ingestion as a required setup step.

### F3 — Relevant documents were discarded

**Observed:** Return-policy chunks had L2 distances near `1.01–1.13` but the
hardcoded cutoff was `0.8`.

**Correction:** Calibrate the prototype cutoff to `1.5` and name/document it.

**Guardrail:** `test_rag_node_keeps_relevant_policy_documents`.

### F4 — Blank UI fields caused an exception

**Observed:** Gradio supplied `None`; the handler called `.strip()` on it.

**Correction:** Normalize missing optional inputs before calling the workflow.

**Guardrail:** `test_respond_accepts_empty_optional_fields`.

### F5 — Cancellation claimed success without durable effect

**Observed:** The service mutated a freshly loaded Python object but never wrote
it back to disk.

**Correction:** Persist the entire validated change using an atomic replacement
under a process lock.

**Guardrail:** `test_successful_cancellation_is_persisted` and
`test_identity_mismatch_does_not_modify_order`.

## What remains unproven

- Live-model intent accuracy and grounded-answer faithfulness at useful scale.
- Retrieval recall across paraphrases, typos, and multilingual requests.
- Multiple-worker concurrency and crash recovery.
- Load, latency, and external API quota behavior.
- Real authentication, ticket-system delivery, and PII controls.
- Indirect prompt injection embedded inside policy documents.

## Next evaluation

Build a versioned labeled dataset containing normal, ambiguous, adversarial, and
out-of-scope requests. Report intent confusion matrix, unsafe-action escape rate,
clarification rate, retrieval recall@3, grounded-answer citation correctness,
latency percentiles, and failure-containment rate in CI.
