# TIKVARON Engineering Intelligence System

TIKVARON Engineering Intelligence starts with an AI-assisted pull-request review engine and a separate low-latency Responses API utility. The OpenAI Agents API integration adds durable managed sessions, specialist subagents, documentation MCP access, web research, streamed progress, and session-level telemetry as a separate review path.

## Components

- **Responses API reviewer**: the existing multi-agent correctness, security, and test-coverage review path.
- **Agents API reviewer**: an independent managed session that coordinates the same specialist scopes, consults the OpenAI documentation MCP and web search, and reconciles one advisory review.
- **GitHub Actions integration**: separate workflows for offline tests and explicitly authorized Agents API reviews.

The Agents API reviewer uses `environment: {"type": "none"}`. It receives a bounded PR diff and has no shell or repository execution environment. It does not check out PR-head code, execute code from a diff, approve or merge PRs, or publish anything other than an advisory comment.

## Local setup

Python 3.11 or newer is required.

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
export OPENAI_API_KEY="your-api-key"
~~~

Run the existing Responses API review:

~~~bash
python -m tikvaron_engineering.cli --diff ./pr.diff --output ./review.md --metrics ./review-metrics.json
~~~

Run the separate Agents API review:

~~~bash
python -m tikvaron_engineering.agents_cli --diff ./pr.diff --output ./agents-review.md --metrics ./agents-review-metrics.json
~~~

The Agents API request is made only when the Agents CLI or the explicitly gated GitHub Actions workflow is invoked.

## Agents API configuration

| Environment variable | Default | Purpose |
|---|---|---|
| `TIKVARON_AGENTS_MODEL` | `gpt-6.1-sol` | Model for managed Agents API review sessions |
| `TIKVARON_AGENTS_MAX_SUBAGENTS` | `3` | Concurrent specialist subagent limit; valid range is 1–4 |
| `OPENAI_API_KEY` | — | OpenAI application key for Agents API requests |

The default remains `gpt-6.1-sol`. Do not route this integration to `gpt-6-astra` until PR #5's opt-in live Responses API smoke test has passed and the maintainer has deliberately updated the model configuration. This Agents API path is not a substitute for that validation gate.

The managed session connects to the public OpenAI documentation MCP over HTTP from the OpenAI service and also enables web search. Both tools are inherited by the specialist subagents. No self-hosted executor is required because this review path does not need file or command execution. If a future task uses a self-hosted environment, provision the separate, restricted executor key and `codex exec-server`; never place the application API key inside the agent environment.

## GitHub Actions and spend control

- `agents-api-ci.yml` runs compilation and mocked unit tests only. It does not need `OPENAI_API_KEY` and makes no OpenAI API request.
- `agents-api-pr-review.yml` does not run on PR open or synchronize events. A maintainer must apply the separate `agents-review` label, or manually dispatch the workflow and set `confirm_paid_run=true`.
- The workflow fetches PR metadata and diff through GitHub CLI, enforces a 200 KB diff limit, and checks out only the trusted base revision. It never checks out or executes PR-head code.
- The workflow posts a normal advisory PR comment. It does not approve, request changes, merge, or alter repository settings.
- The Agents API client disables automatic SDK retries for session creation to reduce the risk of unintentionally creating duplicate billable sessions after ambiguous failures.
- Telemetry artifacts contain session IDs, model, event-type names, diff size, PR/workflow identifiers, and latency. They intentionally do not store source diff contents or raw event payloads.

The Agents API requires an application key with `api.agents.read`, `api.agents.write`, and `api.responses.write`. Keep the key in GitHub Actions Secrets, not repository variables or source files.

**Data handling:** Agents API sessions are managed and persisted by OpenAI. The current Agents API documentation states that data residency is available only in the United States and that the API does not support Zero Data Retention. Review repository/IP handling requirements and applicable data policies before enabling paid PR reviews. A `type: none` environment prevents code execution but does not change the API's session retention or data-residency behavior.

## Tests

Run the offline suite:

~~~bash
python -m compileall -q src tests
python -m unittest discover -s tests -v
~~~

Tests inject a fake client and verify session configuration, specialist delegation settings, MCP/web-search configuration, event failure handling, result extraction, and input limits. They do not verify API credentials, model availability, actual subagent quality, MCP uptime, latency, or live cost.

## Existing Astra gate

PR #5 remains a separate migration and validation gate. After that PR is merged, the maintainer must manually run **Actions → TIKVARON Engineering Intelligence — Live Validation** with `run_astra_smoke=true` and `astra_model=gpt-6-astra`. Only after a successful live smoke test should a maintainer consider changing Astra-related model routing. This Agents API PR does not trigger that workflow or make a live test request.
