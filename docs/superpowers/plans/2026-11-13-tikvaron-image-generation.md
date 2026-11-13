# TIKVARON Image Generation Component Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a separately installable TIKVARON Python package for OpenAI image generation, image editing, multi-turn Responses API workflows, and image streaming.

**Architecture:** Keep all implementation under `packages/tikvaron-image-generation` so the existing pinned Engineering Intelligence release remains unchanged. A small service wrapper accepts an injectable SDK client for testing; the CLI uses standard environment-based OpenAI authentication; a separate manual GitHub Actions workflow is the only live-test path.

**Tech Stack:** Python 3.12, OpenAI Python SDK 2.x, pytest, Ruff, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-11-13-tikvaron-image-generation-design.md`

## Global Constraints

- Default image model is `gpt-image-2.5-sunburst`.
- Default Responses API orchestrator is `gpt-6-astra`.
- Read credentials only from `OPENAI_API_KEY`; never store or print them.
- Never make billable API requests from ordinary CI.
- Do not modify the Engineering Intelligence release archive or its PR-review spend gate.

## Review Focus

- Empty or whitespace-only prompt: reject before invoking the SDK.
- OpenAI returns no image-generation output: raise a clear domain error and do not create an empty file.
- Invalid or malformed base64 output: fail closed and do not report success.
- Moderation blocks in Images or Responses calls: surface a safe typed error; do not retry.
- Multi-image requests and multiple reference files: close file handles reliably and preserve deterministic output naming.

---

### Task 1: Package scaffold and Images API generate/edit

**Files:**
- Create: `packages/tikvaron-image-generation/pyproject.toml`
- Create: `packages/tikvaron-image-generation/src/tikvaron_image_generation/__init__.py`
- Create: `packages/tikvaron-image-generation/src/tikvaron_image_generation/service.py`
- Test: `packages/tikvaron-image-generation/tests/test_service.py`

**Interfaces:**
- Produces: `ImageGenerationClient(client=None, image_model=None, responses_model=None)`.
- Produces: `generate(prompt, output_path, *, quality="auto", size="auto", n=1)` and `edit(prompt, image, output_path, *, mask=None, quality="auto", size="auto", n=1)`, returning `ImageResult`.

- [ ] **Step 1: Write failing tests** for blank prompt rejection, injected-client generation saving returned base64, and editing with file/mask inputs.
- [ ] **Step 2: Run the focused tests** and confirm they fail because the package API does not exist.
- [ ] **Step 3: Implement the package scaffold and Images API methods** with deterministic output paths and restrictive output permissions.
- [ ] **Step 4: Run focused tests** and confirm they pass.
- [ ] **Step 5: Run the package test suite and commit** with `feat(image-generation): add Images API client`.

### Task 2: Responses API multi-turn and streaming

**Files:**
- Modify: `packages/tikvaron-image-generation/src/tikvaron_image_generation/service.py`
- Modify: `packages/tikvaron-image-generation/tests/test_service.py`

**Interfaces:**
- Produces: `generate_with_responses(prompt, output_path, *, previous_response_id=None, action="auto", quality="auto", size="auto")`.
- Produces: `stream_with_responses(prompt, output_path, *, partial_images=2, previous_response_id=None, action="auto", quality="auto", size="auto")`.
- Both return an `ImageResult` including the response ID and saved paths.

- [ ] **Step 1: Write failing tests** for Responses API tool arguments, previous-response chaining, extraction of `image_generation_call.result`, partial-image persistence, and final-image persistence.
- [ ] **Step 2: Run the focused tests** and verify the expected missing-method failures.
- [ ] **Step 3: Implement multi-turn and streaming methods** using the documented Responses API events and `previous_response_id`.
- [ ] **Step 4: Run focused tests** and confirm they pass.
- [ ] **Step 5: Run full package tests and commit** with `feat(image-generation): add Responses and streaming support`.

### Task 3: CLI, documentation, and examples

**Files:**
- Create: `packages/tikvaron-image-generation/src/tikvaron_image_generation/cli.py`
- Create: `packages/tikvaron-image-generation/README.md`
- Create: `packages/tikvaron-image-generation/examples/generate_image.py`
- Modify: `packages/tikvaron-image-generation/pyproject.toml`
- Test: `packages/tikvaron-image-generation/tests/test_cli.py`

**Interfaces:**
- Produces: `tikvaron-image generate`, `tikvaron-image edit`, `tikvaron-image respond`, and `tikvaron-image stream`.
- CLI output is JSON metadata with output paths and response ID; it never prints base64 image contents.

- [ ] **Step 1: Write failing CLI tests** for command routing, argument validation, and JSON metadata output.
- [ ] **Step 2: Run the focused tests** and confirm failure.
- [ ] **Step 3: Implement the CLI, entry point, and examples**.
- [ ] **Step 4: Run CLI tests** and confirm they pass.
- [ ] **Step 5: Run the full suite and commit** with `feat(image-generation): add CLI and usage docs`.

### Task 4: CI and opt-in live validation

**Files:**
- Create: `.github/workflows/image-generation.yml`
- Create: `packages/tikvaron-image-generation/scripts/live_smoke.py`
- Modify: `README.md`

**Interfaces:**
- CI runs on relevant pushes/PRs and performs package install, compilation, tests, and lint with no API secret.
- Manual workflow input `run_live_smoke` defaults to `false`; only the live job receives `OPENAI_API_KEY`.
- The live smoke test writes one generated PNG and a JSON result; upload only after a successful response.

- [ ] **Step 1: Write a unit test** for the live-smoke runner's missing-key block and mocked successful output.
- [ ] **Step 2: Run the focused test** and confirm failure.
- [ ] **Step 3: Implement the live smoke runner, path-filtered CI, and opt-in manual workflow** with pinned GitHub Actions.
- [ ] **Step 4: Run all package tests, compilation, and Ruff**.
- [ ] **Step 5: Commit** with `ci(image-generation): add isolated CI and opt-in live smoke`.

### Task 5: Final review and pull request

**Files:**
- Review all files in this feature branch.

- [ ] Verify requirements against the design spec and Review Focus.
- [ ] Run the complete package verification commands from a clean install.
- [ ] Inspect the final diff for credential leakage, unsafe workflow permissions, or accidental changes to Engineering Intelligence.
- [ ] Create a pull request against `main`; do not merge it or dispatch a live billable run.

## Verification Commands

Run from `packages/tikvaron-image-generation`:

- `python -m pip install -e ".[dev]"`
- `python -m compileall -q src scripts tests`
- `pytest -q`
- `ruff check .`

The default verification path must not require `OPENAI_API_KEY` and must not contact the OpenAI API.
