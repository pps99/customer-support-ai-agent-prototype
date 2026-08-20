# AI Tool Disclosure

AI coding tools were used as an implementation and review partner for repository
inspection, refactoring suggestions, test generation, Gradio integration,
documentation drafting, and diagnosis of runtime traces.

AI output was not treated as correct by default. Important generated or
AI-assisted output that was rejected, corrected, or substantially improved:

- A narrow keyword classifier recognized only exact phrases. It was replaced by
  the existing typed intent workflow plus deterministic safety routing.
- Initial order lookup returned after inspecting the first record. A later-order
  regression test exposed and now guards the correction.
- The first Chroma integration relied on its default home cache, which failed in
  the execution environment. The cache was redirected to a writable generated
  project directory.
- The first Gradio handler assumed optional inputs were always strings. A real UI
  traceback showed they may be `None`; normalization and a regression test were
  added.
- An arbitrary retrieval cutoff rejected policy chunks that diagnostics showed
  were relevant. The value was adjusted using observed distances and covered by
  a test; broader calibration remains a known limitation.
- Cancellation logic initially returned success after an in-memory-only change.
  This was rejected as a misleading business outcome and replaced with atomic
  persistence and tests.
- Early exception handling collapsed distinct retrieval failures into “not
  found.” It now preserves operational failure categories and avoids leaking
  internal errors to customers.

Human judgment determined the final safety boundary, the claims the system may
make, the known limitations, and what evidence is sufficient. All submitted code
should be understood and defensible by the candidate; AI assistance does not
transfer responsibility for its behavior.
