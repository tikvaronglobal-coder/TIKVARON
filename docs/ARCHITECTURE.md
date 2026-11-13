# TIKVARON Engineering Intelligence Architecture

## Design

The product is a deterministic-first, evidence-grounded set of agents orchestrated over a pull-request diff and a trusted repository checkout.

- PR Review: model-based defect reasoning with strict structured output and diff-grounded path/line checks. The multi-agent reviewer uses the OpenAI Responses API so it can orchestrate model tools.
- Security: deterministic scanning of added lines, secret redaction before model submission, and risk aggregation.
- Architecture: Python AST and JavaScript/TypeScript import graph analysis over the trusted base checkout.
- Dependency: conservative exact-version extraction and read-only OSV advisory lookup.
- Incident: correlation against reviewed incident records in `.tikvaron/incidents.json`.
- Documentation: identifies likely documentation gaps associated with changed components.
- Test Intelligence: converts JUnit XML into machine-readable summaries and CI artifacts.
- Astra authentication test: a separate manual workflow makes one Responses API request to verify API-key authentication and text inference. It uses low reasoning effort, disables response storage, disables SDK retries, verifies an exact sentinel, and records the model, request ID, and token usage. It is not a PR review and does not run automatically.
- Responses API tools: an optional research/retrieval layer provides hosted web search, vector-store file search, namespaced read-only repository functions, deferred tool discovery, and approval-gated remote MCP. External tools are disabled unless explicitly configured; the default PR review does not silently acquire new external capabilities.

## Tool orchestration

The optional runtime lives in `tikvaron_engineering.responses_tools`. It uses a strict function-schema namespace named `engineering`, exposes trusted workflow metadata and changed-path labels, and executes only its small local read-only allowlist. Function calls are serialized and bounded. Unknown functions, malformed arguments, and exceeded tool-call limits fail closed.

Web search is opt-in. File search requires an explicitly supplied vector-store ID. Remote MCP requires an HTTPS endpoint and human approval. The helper is installed into the restored release by the tracked deployment overlay; the pinned source ZIP is not modified.

## Trust boundaries

The privileged `pull_request_target` workflow checks out only the trusted base SHA. It requests the PR diff through GitHub's API and never checks out, installs, imports, or executes PR-head code. All PR content is untrusted model input. Changed paths returned by the helper are labels parsed from that input and are never opened or executed.

## Operational behavior

Reviews are advisory and idempotently update one bot comment. Failures do not publish partial reviews. Oversized diffs, invalid structured output, and unsupported model responses fail closed. Live API tests and the three-PR validation pilot are separate manual workflows because they incur cost and require explicit inputs. The Astra smoke test is independently opt-in and its result is recorded as a small CI artifact. The Responses API tools tests use fakes and do not call the live API.

## Limits

Architecture graph support is intentionally scoped to Python AST imports and common JS/TS import forms. Dependency extraction is conservative and does not replace full lockfile resolution or an SBOM. OSV is a vulnerability signal, not proof of exploitability. Incident correlation depends on the quality of supplied incident records.
