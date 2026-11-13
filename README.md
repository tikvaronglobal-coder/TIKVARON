# TIKVARON

**Where Hope Sings.**

TIKVARON Engineering Intelligence is a multi-agent engineering quality system. Release `v0.2.0` includes AI pull-request review, deterministic security scanning, architecture intelligence, dependency intelligence, incident correlation, documentation impact analysis, and JUnit-based test intelligence.

## Source release

The complete tested v0.2.0 source, package metadata, tests, and documentation are committed under `releases/.archive-data/` as ordered Base64 segments. This is a transport format for the GitHub content API, not a different source release. Each workflow concatenates the segments in lexical order, decodes the ZIP, verifies it with `unzip -t`, and extracts the original project.

For local use, download the segments and reconstruct the release, or use the workflow artifacts after CI.

## GitHub Actions setup

1. Add repository Actions secret `OPENAI_API_KEY` under Settings → Secrets and variables → Actions. Never commit the key or paste it into chat.
2. Run **Actions → TIKVARON Engineering Intelligence — Live Validation** with `run_astra_smoke=true` to make one explicit GPT-6 Astra Responses API request. The default model input is `gpt-6-astra`; the job records status, request ID, and token usage without logging credentials. This paid request is opt-in and defaults to off.
3. After the Astra smoke test passes, optionally add Actions variable `TIKVARON_ASTRA_MODEL` with value `gpt-6-astra`. The PR review workflow gives this validated Astra override precedence over `TIKVARON_OPENAI_MODEL`. If it is unset, the existing model setting/default remains in effect.
4. The PR review workflow becomes active after it is on the default branch. A maintainer must apply the `ai-review` label to a PR to authorize a billable review.
5. For the three-PR read-only validation pilot, enter exactly three comma-separated existing open PR numbers in the same Live Validation workflow.

The PR review workflow uses `pull_request_target` but checks out only the trusted base commit and obtains PR changes through the GitHub API. It never checks out or executes contributor-controlled PR code. Reviews are advisory; no merge gate is enabled.

The Astra authentication/inference check and the multi-agent PR-review engine both use the Responses API. The smoke test uses `reasoning.effort=low`, disables response storage, and makes one request with SDK retries disabled. See [`DEPLOYMENT.md`](DEPLOYMENT.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/SECURITY.md`](docs/SECURITY.md), and [`docs/EVALUATION.md`](docs/EVALUATION.md).
