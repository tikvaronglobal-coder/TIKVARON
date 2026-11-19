"""Explicitly invoked, single-request live image-generation smoke test."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from tikvaron_image_generation import ImageGenerationClient


def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "reason": "OPENAI_API_KEY is not configured for this opt-in job.",
                }
            ),
            file=sys.stderr,
        )
        return 2

    output_path = Path(
        os.getenv("TIKVARON_IMAGE_SMOKE_OUTPUT", "artifacts/tikvaron-image-smoke.png")
    )
    try:
        result = ImageGenerationClient().generate(
            "Create a simple abstract TIKVARON validation image: one cobalt-blue circle "
            "centered on a warm cream background, with no text or logos.",
            output_path,
            quality="low",
            size="1024x1024",
            n=1,
        )
    except Exception as exc:  # Avoid printing SDK request headers or credential material.
        print(
            json.dumps(
                {
                    "status": "failed",
                    "error_type": type(exc).__name__,
                    "reason": (
                        "The live image smoke test did not complete; check the API model "
                        "and project access."
                    ),
                }
            ),
            file=sys.stderr,
        )
        return 1

    print(
        json.dumps(
            {
                "status": "passed",
                "model": result.model,
                "paths": [str(path) for path in result.paths],
                "image_count": len(result.paths)
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by the workflow
    raise SystemExit(main())
