# TIKVARON Image Generation

A reusable Python component for generating, editing, iterating on, and streaming image assets with OpenAI GPT Image models.

## Install

The repository stores the core service and its offline service tests in a compressed source bundle. Restore those two files once from this directory, then install:

```bash
tar -xJf core-sources.tar.xz
python -m pip install -e ".[dev]"
export OPENAI_API_KEY="your-project-api-key"
```

The OpenAI SDK reads `OPENAI_API_KEY` from the environment. Never put credentials in source files, command-line arguments, notebooks, or generated artifacts.

Defaults can be changed without code edits:

- `TIKVARON_IMAGE_MODEL` — defaults to `gpt-image-2.5-sunburst`.
- `TIKVARON_IMAGE_RESPONSES_MODEL` — defaults to `gpt-6-astra`.

## Python API

```python
from tikvaron_image_generation import ImageGenerationClient

images = ImageGenerationClient()

# Single-shot generation through the Images API.
result = images.generate(
    "A children's book drawing of a veterinarian listening to a baby otter's heartbeat",
    "artifacts/baby-otter.png",
    quality="high",
)
print(result.paths)

# Editing with one or more references and an optional mask.
edited = images.edit(
    "Recolor the vase to cobalt blue; keep everything else unchanged",
    "assets/kitchen.png",
    "artifacts/kitchen-edited.png",
    mask="assets/vase-mask.png",
)

# Multi-turn image refinement through the Responses API.
first = images.generate_with_responses(
    "A gray tabby cat hugging an otter with an orange scarf",
    "artifacts/cat-and-otter.png",
    action="generate",
)
refined = images.generate_with_responses(
    "Now make the same scene photorealistic",
    "artifacts/cat-and-otter-realistic.png",
    previous_response_id=first.response_id,
    action="edit",
)

# Stream partial previews and the final image through Responses.
streamed = images.stream_with_responses(
    "A river made of white owl feathers in a winter landscape",
    "artifacts/owl-feather-river.png",
    partial_images=2,
)
print(streamed.partial_paths, streamed.paths)

# Or stream preview events directly from the Images API.
previews = images.stream_with_images(
    "A river made of white owl feathers",
    "artifacts/owl-feather-river-preview.png",
    partial_images=2,
)
print(previews.partial_paths)

# Upload a local image once and reference it by File ID in a Responses request.
file_id = images.upload_vision_file("assets/product.png")
with_reference = images.generate_with_responses(
    "Create a gift basket containing the reference item",
    "artifacts/gift-basket.png",
    action="generate",
    reference_file_ids=[file_id],
)
```

The API methods return `ImageResult` with saved file paths, model name, optional Responses `response_id`, partial-preview paths, and any revised prompt metadata. Files are saved with owner-only permissions. Responses reference images may be supplied as local paths (encoded as data URLs) or File IDs; `upload_vision_file` creates a `purpose="vision"` File and returns its ID. Uploaded Files remain in the OpenAI project until you delete them separately. A Responses tool mask can be provided using `mask_file_id`. `stream_with_images` saves preview events only; use `stream_with_responses` when you also need the completed final image saved. Invalid or missing image payloads raise `ImageGenerationError`; moderation blocks raise `ImageGenerationModerationError` with the moderation stage and categories where available.

## CLI

```bash
tikvaron-image generate --prompt "A friendly baby otter" --output artifacts/otter.png --quality high

tikvaron-image edit --prompt "Make the scarf orange" --image cat.png --image otter.png --output artifacts/scene.png

tikvaron-image respond --prompt "Make it realistic" --output artifacts/realistic.png --previous-response-id resp_...

tikvaron-image stream --prompt "A snowy river" --output artifacts/river.png --partial-images 2

tikvaron-image stream-images --prompt "A snowy river" --output artifacts/river-preview.png --partial-images 2

tikvaron-image upload --image assets/product.png
tikvaron-image respond --prompt "Create a gift basket with the reference product" --output artifacts/basket.png --reference-file-id file_... --action generate
```

CLI output is JSON metadata; it never prints base64 image data.

## Tests and live validation

After restoring the core source bundle, offline tests use a fake SDK client and never send an OpenAI request:

```bash
tar -xJf core-sources.tar.xz
python -m pip install -e ".[dev]"
python -m compileall -q src scripts tests
pytest -q
ruff check .
```

The GitHub Actions workflow restores the bundle and runs those checks without `OPENAI_API_KEY`. A separate manual `workflow_dispatch` input named `run_live_smoke` defaults to `false`; enabling it sends one billable image-generation request and uploads the generated smoke image for three days.

## TIKVARON / ChatGPT boundary

This package is for TIKVARON services and developer workflows. It does not change ChatGPT's global model, settings, or built-in image tools. In ChatGPT, use the native image-generation feature when available; connect a future TIKVARON-hosted app or MCP endpoint separately if ChatGPT needs to invoke a deployed TIKVARON service.
