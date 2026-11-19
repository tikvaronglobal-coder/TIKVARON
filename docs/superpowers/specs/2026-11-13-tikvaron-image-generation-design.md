# TIKVARON Image Generation Component — Design

**Date:** 2026-11-13

## Intent

Add a reusable, installable Python component to TIKVARON for creating and editing image assets through OpenAI's GPT Image models. It should be usable from TIKVARON applications, scripts, and automation without coupling creative media work to Engineering Intelligence's pull-request review pipeline.

## Goals

- Provide a small Python package at `packages/tikvaron-image-generation`.
- Support single-shot generation and edits through the OpenAI Images API.
- Support multi-turn image generation/editing through the Responses API, including `previous_response_id`.
- Support streamed Responses API generation with partial-image files and a final image.
- Save base64 image outputs to files with safe file permissions.
- Expose a small CLI for generate, edit, Responses, and stream workflows.
- Normalize image moderation blocks into a clear, safe error without exposing credentials.
- Include offline unit tests and an opt-in, manually dispatched live smoke test.

## Non-goals

- Changing ChatGPT's global settings, model selection, or built-in tools.
- Deploying a hosted MCP server or custom ChatGPT app in this change; the current repository has no application backend or hosted service endpoint.
- Making billable API calls during normal CI.
- Storing API keys, prompts, or image bytes in Git.
- Changing the existing Engineering Intelligence package, review spend gate, or the open GPT-6 Astra PR.

## Approaches considered

1. **Add image generation inside Engineering Intelligence.** Rejected because image creation is not an engineering-review concern and would expand the review package's dependency and security surface.
2. **Create a separate installable Python package in this repository.** Chosen because it isolates dependencies and spend, is importable from other TIKVARON services, and can be validated independently without modifying the pinned Engineering Intelligence archive.
3. **Build a hosted MCP/ChatGPT app first.** Deferred because the repository currently has no deployed backend or app endpoint. A hosted MCP adapter can be added later once TIKVARON has a deployment target and authentication model.

## Design decisions

- Package name: `tikvaron-image-generation`; import name: `tikvaron_image_generation`.
- Default image model: `gpt-image-2.5-sunburst`.
- Default Responses orchestrator: `gpt-6-astra`, a currently documented model supporting the Responses image-generation tool.
- Credentials come from the standard `OPENAI_API_KEY` environment variable via the OpenAI SDK. Never accept a key in CLI arguments or log it.
- One-shot generation and editing use the Images API. Multi-turn and streamed operations use the Responses API.
- CI is offline and mock-based. A separate manual workflow dispatch is the only path that sends a live image-generation request.
- ChatGPT requests to create or edit images continue to use ChatGPT's native image-generation capability when available; this package is for TIKVARON application/API usage, not a way to change ChatGPT's platform configuration.

## Safety and operational constraints

- No external image request without an explicit command or manually dispatched workflow.
- Validate empty prompts and unsupported action/partial-image arguments before calling the API.
- Do not write credentials or raw base64 image data to logs or workflow artifacts.
- Use restrictive file permissions for generated output and avoid overwriting unexpected files silently where practical.
- Convert `moderation_blocked` into a specific exception that recommends neutral prompt/input changes; never retry blocked prompts automatically.
- Preserve caller control over output location and avoid automatic publishing, deployment, or external sharing.

## Acceptance criteria

- Unit tests cover generation, editing, multi-turn Responses, streamed partial/final image events, missing output, invalid input, and moderation errors without network calls.
- Package installs in an isolated Python environment and exposes a working `tikvaron-image` command.
- CI runs formatting/lint, compilation, and tests without `OPENAI_API_KEY`.
- The live workflow is opt-in, uses `OPENAI_API_KEY` only in the request step, and uploads the generated image as a short-retention artifact.
- The change is delivered through a reviewable pull request; it does not merge itself.
