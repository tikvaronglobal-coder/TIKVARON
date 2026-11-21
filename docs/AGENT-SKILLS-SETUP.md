# TIKVARON Agent Skills Setup

This integration stages two MIT-licensed upstream skill collections for Codex CLI and repository-scoped Codex use.

## Imported collections

| Collection | Skills | Pinned upstream revision |
|---|---:|---|
| Trader Skill | 11 | `5189e79b9a480755a3733ac9713f5353981dbe18` |
| Instagram Agent Skill | 13 | `d03c56bb598be770c60b201f94237e5d1a4268a6` |

Upstream repositories:
- https://github.com/Jakeschincariol/trader-skill
- https://github.com/Jakeschincariol/instagram-agent-skill

The installer copies complete skill directories, including supporting scripts, JSON data, templates, and tests where present. It pins upstream revisions to avoid silently changing code on future installs.

## Install into Codex

From a local clone of this repository:

```bash
bash scripts/install-agent-skills.sh --scope project
```

This installs to `.agents/skills/` in the TIKVARON repository. To install for the current OS user across projects:

```bash
bash scripts/install-agent-skills.sh --scope user
```

Codex's documented user skill location is `~/.agents/skills`; project skills live under `.agents/skills`. After installation, restart Codex if the skills do not appear, then use `/skills` or `$skill-name`.

## Validation

Run a validation-only pass before installation:

```bash
bash scripts/install-agent-skills.sh --check
```

This checks the pinned revisions, confirms 11 + 13 skill folders and valid skill metadata, compiles all Python files, and runs the Trader repository's offline unittest suite. It does not install files.

## Safety configuration

The imported skills are third-party instructions and scripts. Review them before use. The TIKVARON policy is installed as `tikvaron-approval-policy`.

For an additional hard block, add this to `~/.codex/config.toml` (or the relevant Codex config file) before using the imported trader skills:

```toml
[[skills.config]]
name = "trader-broker"
enabled = false
```

Do not enable a live brokerage connector. Keep any future paper-trading integration isolated from live credentials.

No Instagram publishing connector, browser automation, login, or credentials are installed. The Instagram skills are for research and draft creation only. Publish and send manually after review.

## Scope and limitations

- This repository PR prepares the repeatable installation path; it cannot write files onto a phone or another computer's local Codex installation.
- The local install command must be run on the computer where Codex CLI is installed.
- Standalone Codex skills are not automatically installed into the Android ChatGPT app. ChatGPT desktop has its own skill support; mobile availability and account controls can differ.
- No live trades, social posts, comments, follows, DMs, or paid API calls are performed by this installer.
