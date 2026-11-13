# TIKVARON

**Where Hope Sings.**

TIKVARON Engineering Intelligence is a multi-agent engineering quality system. Release `v0.2.0` includes AI pull-request review, deterministic security scanning, architecture intelligence, dependency intelligence, incident correlation, documentation impact analysis, and JUnit-based test intelligence.

## Source release

The complete tested v0.2.0 source, package metadata, tests, and documentation are committed under `releases/.archive-data/` as ordered Base64 segments. This is a transport format for the GitHub content API, not a different source release. Each workflow concatenates the segments in lexical order, decodes the ZIP, verifies it with `unzip -t`, and extracts the original project.

For local use, download the segments and reconstruct the release, or use the workflow artifacts after CI.

## GitHub Actions setup

1. Add repository Actions secret `OPENAI_API_KEY` under Settings → Secrets and variables → Actions. Never commit the key.
2. Optionally add Actions variable `TIKVARON_OPENAI_MODEL` (default: `gpt-6.1-sol`).
3. Merge the deployment pull request after reviewing it. The PR review workflow becomes active after it is on the default branch.
4. Run **Actions → TIKVARON Engineering Intelligence — Live Validation** manually. Opt into the billable OpenAI smoke test and/or provide exactly three comma-separated existing open PR numbers for the read-only pilot.

The PR review workflow uses `pull_request_target` but checks out only the trusted base commit and obtains PR changes through the GitHub API. It never checks out or executes contributor-controlled PR code. The proposed hardened workflow requires a maintainer to apply the `ai-review` label before a billable review can run; see the security follow-up pull request. Reviews are advisory; no merge gate is enabled.

See [`DEPLOYMENT.md`](DEPLOYMENT.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/SECURITY.md`](docs/SECURITY.md), and [`docs/EVALUATION.md`](docs/EVALUATION.md).
