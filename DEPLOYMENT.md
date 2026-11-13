# TIKVARON Engineering Intelligence — deployment guide

## Release

The complete v0.2.0 release ZIP is committed under `releases/.archive-data/` as lexically ordered Base64 segments because the connected GitHub content API accepts text blobs. Every workflow reconstructs the archive, runs `unzip -t`, and extracts the original project before installing or testing it. The parts are immutable as a set; do not edit individual parts.

## Required configuration

- Add `OPENAI_API_KEY` as a repository Actions secret (Settings → Secrets and variables → Actions). Never commit or paste the key into chat.
- Optionally set Actions variable `TIKVARON_OPENAI_MODEL`; default is `gpt-6.1-sol`.
- Enable GitHub Actions and allow the PR review workflow to write pull-request comments.

## Rollout

1. Review and merge the feature branch / deployment PR.
2. Add the `OPENAI_API_KEY` repository secret directly in GitHub. The GitHub content integration cannot create repository secrets.
3. Run the manual live validation workflow with `run_openai_smoke=true` for one billable API connectivity test.
4. Run it with exactly three comma-separated existing open PR numbers. This pilot is read-only: it fetches diffs, redacts likely credentials, executes the reviewers, and uploads a JSON record. It does not post comments or modify PR state.
5. Have a maintainer label true positives, false positives, false negatives, severity agreement, and usefulness before enabling enforcement. Recall cannot be calculated without an independent ground-truth defect set.

## Permissions and safety

- CI: `contents: read`.
- PR review: `contents: read`, `pull-requests: write`.
- Live pilot: `contents: read`, `pull-requests: read`.
- PR review checks out only the trusted base commit. It never checks out or executes PR-head code.
- Automated findings are advisory. No merge blocking, approval, auto-merge, or deployment is enabled by default.
