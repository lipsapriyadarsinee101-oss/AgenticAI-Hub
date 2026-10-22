# Configuration, operations, and validation

## Runtime settings
OLLAMA_HOST and OLLAMA_MODEL configure every local model adapter.
OLLAMA_EMBED_MODEL configures LlamaIndex embeddings.
Langflow settings are documented in LANGFLOW.md.
Langfuse Python SDK 5 targets Langfuse v4; use a compatible service.
LANGFUSE_BASE_URL, LANGFUSE_PUBLIC_KEY, and LANGFUSE_SECRET_KEY configure the SDK.

## Current controls
- Question validation: nonempty, at most 4000 characters.
- No arbitrary code execution or file-writing tools exposed to models.
- Bounded local document reads and numeric arithmetic.
- Framework iteration/recursion limits and 120-second model request timeouts where configured.
- Unique run directories; JSONL stage durations; failure type artifacts.
- Optional metadata-only stage tracing; explicit enablement required.
- Missing dependencies and configuration fail visibly; no silent downgrade to demo.

Timeouts apply per request, not to an entire job. Retrieval embeddings can also make multiple
requests. There is no global deadline, cancellation system, retry backoff, persistent graph
checkpoint, token budget, or hosted API in this starter.

## Before public deployment
Use a durable worker queue and enforce wall-clock deadlines at the worker boundary.
Add authentication, authorization, rate limits, per-user storage isolation, and secret management.
Persist and version the vector index. Pin and audit dependencies after integration validation.
Add provider token/cost tracking, retention policies, and factual evaluation sets.
Treat document text as untrusted data; prompting alone is not a full prompt-injection defense.
Review model outputs before consequential use. Filename citation checks are only structural.

## Manual live validation
1. In a fresh virtual environment install each selected extra.
2. Start Ollama, download the configured model and embedding model.
3. Run graph, rag, crew and smol modes separately with an evidence-backed question.
4. Confirm actual tool usage using each framework's local diagnostics.
5. Run all mode and verify source references survive every transformation.
6. Build a Langflow flow, run langflow mode, inspect langflow.json.
7. Run all --with-langflow --trace and confirm observations reach your Langfuse service.
8. Stop Ollama and rerun: confirm a nonzero exit and failure.json.
9. Use an unknown topic: confirm the report acknowledges missing evidence.

These live checks were not executed during initial generation. Offline tests cover the
demo, calculator, retrieval, logs, validation, failure handling, and Langflow HTTP contract
with a mocked HTTP transport, not actual model compatibility.

## Privacy
Local result.json stores user input, retrieved evidence, and outputs.
Do not commit runs or secrets. Stage tracing omits content but may expose stage names,
timing and framework errors through the SDK. Framework libraries can have their own telemetry;
review their settings separately.

