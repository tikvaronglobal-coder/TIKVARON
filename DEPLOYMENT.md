# TIKVARON Engineering Intelligence — deployment guide

## Release

The complete v0.2.0 release ZIP is committed under `releases/.archive-data/` as lexically ordered Base64 segments because the connected GitHub content API accepts text blobs. Every workflow reconstructs the archive, runs `unzip -t`, and extracts the original project before installing or testing it. The parts are immutable as a set; do not edit individual parts.

## Required configuration

- Add `OPENAI_API_KEY` as a GitHub Actions repository secret (Settings → Secrets and variables → Actions). Never commit or paste the key into chat.
- The optional Actions variable `TIKVARON_OPENAI_MODEL` keeps the existing model selection. After a successful Astra smoke test, optionally set `TIKVARON_ASTRA_MODEL=gpt-6-astra`; this validated Astra override takes precedence in the PR-review workflow.
- Enable GitHub Actions and allow the PR review workflow to write pull-request comments.
- The hardened PR review workflow uses a maintainer-applied `ai-review` label as an explicit spend-approval step. Create that repository label if it does not already exist; do not apply it to PRs unless a billable review is intended.

## Rollout

1. Review and merge the integration pull request.
2. Add or verify the `OPENAI_API_KEY` repository secret directly in GitHub. Never provide the key in chat or source files.
3. Open **Actions → TIKVARON Engineering Intelligence — Live Validation**. Set `run_astra_smoke=true` and leave the model input at `gpt-6-astra` to run exactly one Responses API authentication and inference request. The job is manual, billable, and disabled by default. It installs the official OpenAI Python SDK, disables SDK retries, verifies an exact response sentinel, and uploads a result artifact with model, request ID, and token usage.
4. Only after the Astra smoke test passes, set the repository Actions variable `TIKVARON_ASTRA_MODEL` to `gpt-6-astra` to route the PR Review Engine to Astra. Both the smoke test and PR reviewer use the Responses API. Astra and Sol reasoning requests use `low` or higher; `none` is unsupported for these models. The smoke test sends `reasoning={"effort": "low"}`, uses `max_output_tokens=64`, and sets `store=false`.
5. Run the three-PR pilot with exactly three comma-separated existing open PR numbers. This pilot is read-only: it fetches diffs, redacts likely credentials, executes the reviewers, and uploads a JSON record. It does not post comments or modify PR state.
6. Have a maintainer label true positives, false positives, false negatives, severity agreement, and usefulness before enabling enforcement. Recall cannot be calculated without an independent ground-truth defect set.

## Permissions and safety

- CI: `contents: read`.
- PR review: `contents: read`, `pull-requests: write`.
- Live pilot and Astra smoke test: `contents: read`; the pilot additionally has `pull-requests: read`.
- PR review checks out only the trusted base commit. It never checks out or executes PR-head code.
- The Astra smoke test receives `OPENAI_API_KEY` only in the inference step and never writes the credential to artifacts or logs. It is manual and defaults to off.
- Automated findings are advisory. No merge blocking, approval, auto-merge, or deployment is enabled by default.
