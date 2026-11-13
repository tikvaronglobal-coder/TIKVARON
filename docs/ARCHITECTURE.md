# TIKVARON Engineering Intelligence Architecture

## Design

The product is a deterministic-first, evidence-grounded set of agents orchestrated over a pull-request diff and a trusted repository checkout.

- PR Review: model-based defect reasoning with strict structured output and diff-grounded path/line checks.
- Security: deterministic scanning of added lines, secret redaction before model submission, and risk aggregation.
- Architecture: Python AST and JavaScript/TypeScript import graph analysis over the trusted base checkout.
- Dependency: conservative exact-version extraction and read-only OSV advisory lookup.
- Incident: correlation against reviewed incident records in `.tikvaron/incidents.json`.
- Documentation: identifies likely documentation gaps associated with changed components.
- Test Intelligence: converts JUnit XML into machine-readable summaries and CI artifacts.

## Trust boundaries

The privileged pull_request_target workflow checks out only the trusted base SHA. It requests the PR diff through GitHub's API and never checks out, installs, imports, or executes PR-head code. All PR content is untrusted model input.

## Operational behavior

Reviews are advisory and idempotently update one bot comment. Failures do not publish partial reviews. Oversized diffs, invalid structured output, and unsupported model responses fail closed. Live API tests and the three-PR validation pilot are separate manual workflows because they incur cost and require explicit inputs.

## Limits

Architecture graph support is intentionally scoped to Python AST imports and common JS/TS import forms. Dependency extraction is conservative and does not replace full lockfile resolution or an SBOM. OSV is a vulnerability signal, not proof of exploitability. Incident correlation depends on the quality of supplied incident records.
