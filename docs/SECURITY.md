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
- The optional Responses API tool layer does not run in CI or the standard PR review path. Web search and file search are disabled unless explicitly enabled or configured.
- The only built-in local functions are read-only. They return a small set of GitHub workflow metadata or parse changed-path labels from an untrusted diff; they do not run shell commands, open diff-supplied paths, write files, or change GitHub state.
- Tool calls are serialized and limited to four rounds. Unknown function names and invalid arguments fail closed.
- Remote MCP connections require HTTPS and explicit human approval. Never replace `require_approval="always"` with automatic approval for an unreviewed server.
- A vector-store ID is configuration, not proof that its contents are safe. Populate vector stores only with approved, access-controlled engineering documents and review their retention and access policies.
- Store `OPENAI_API_KEY` only as a GitHub Actions repository secret.
