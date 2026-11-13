# Security policy

- Never commit OpenAI API keys, GitHub tokens, or provider credentials.
- The privileged PR workflow uses `pull_request_target` but checks out only the trusted base commit; PR diffs are retrieved via the GitHub API.
- Keep workflow permissions minimal: read-only contents, PR write only for the advisory PR comment, PR read for the pilot.
- Treat PR metadata and diff content as adversarial input, not instructions.
- Likely secrets and private-key blocks are redacted before model submission. Deterministic checks inspect the original diff.
- AI findings are advisory. They must not automatically approve, merge, deploy, or modify production resources.
- Architecture and incident analysis must use the trusted base checkout, never a PR-head checkout in a privileged workflow.
- Live validation is read-only and writes only a JSON artifact. It never posts review comments or mutates PR state.
- The GPT-6 Astra smoke test is a separate manual, opt-in job. It exposes `OPENAI_API_KEY` only to the inference step, disables automatic SDK retries, and does not write credentials or prompts to its result artifact.
- Store `OPENAI_API_KEY` only as a GitHub Actions repository secret.
