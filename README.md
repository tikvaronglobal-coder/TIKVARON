# TIKVARON Engineering Intelligence System

TIKVARON Engineering Intelligence starts with an AI-assisted pull-request review engine and a separate low-latency Responses API utility.

## Components

- **Multi-agent PR reviewer**: uses the OpenAI beta Responses endpoint to run specialist passes for correctness, security, and missing tests, then returns the root agent's reconciled review.
- **Fast single-agent Responses helper**: uses the standard Responses endpoint with the Ultrafast service tier for latency-sensitive, non-review tasks.
- **GitHub Actions integration**: reviews pull requests and posts the result as a PR review comment.

## Local setup

Python 3.11 or newer is required.

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
export OPENAI_API_KEY="your-api-key"
~~~

Run a multi-agent review against a saved unified diff:

~~~bash
python -m tikvaron_engineering.cli --diff ./pr.diff --output ./review.md --metrics ./review-metrics.json
~~~

Use the single-agent fast path from Python:

~~~python
from tikvaron_engineering import run_fast_response

print(run_fast_response("Explain why the sky is blue in one sentence."))
~~~

## Configuration

| Environment variable | Default | Purpose |
|---|---|---|
| OPENAI_API_KEY | — | OpenAI API credential |
| TIKVARON_REVIEW_MODEL | gpt-6.1-sol | Model for multi-agent PR review |
| TIKVARON_FAST_MODEL | gpt-6-astra | Model for ordinary Responses requests |
| TIKVARON_FAST_SERVICE_TIER | ultrafast | Service tier for the fast path |

Ultrafast is a latency-oriented service tier and may have different rate limits and pricing from the standard tier. Use it only where the latency benefit is worth the cost. The multi-agent review uses the responses_multi_agent=v1 beta capability.

## GitHub Actions setup

1. In the repository, open **Settings → Secrets and variables → Actions**.
2. Add a repository secret named **OPENAI_API_KEY** containing the OpenAI API key. Do not commit the key to the repository or put it in workflow YAML.
3. Add the `ai-review` label to a pull request to authorize a paid review, or use the workflow's manual dispatch with a PR number. This label gate prevents arbitrary public PR updates from repeatedly triggering billed model calls.

For security, the workflow uses pull_request_target so the workflow definition comes from the trusted base branch. It checks out only the PR base revision and retrieves the proposed diff through GitHub CLI; it never checks out or executes the PR head. Paid reviews require a maintainer-applied `ai-review` label or an authorized manual dispatch. The diff is capped at 200 KB. GitHub Actions are pinned to immutable release commit SHAs. Do not change the checkout ref to the PR head, run scripts from the diff, remove the approval gate, or otherwise execute untrusted PR content while repository secrets are available. Review any change to this workflow security model carefully.

## Tests

Run the offline unit tests:

~~~bash
python -m unittest discover -s tests -v
~~~

The tests mock the OpenAI client. They verify SDK routing, root-agent result extraction, and provider-usage capture but do not verify live API credentials, model access, service-tier entitlement, or actual review quality.

The CLI can write a telemetry JSON file containing the response ID, model, provider-returned usage record, workflow/PR identifiers when present, diff size, and request latency. GitHub Actions retains this file as a 30-day artifact. Calculate monetary cost only from the captured token details and the applicable official model rates for the request date; if usage or applicable rates are unavailable, report cost as unmeasured rather than estimating it.
