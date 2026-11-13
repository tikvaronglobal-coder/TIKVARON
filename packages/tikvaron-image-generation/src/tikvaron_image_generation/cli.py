"""Command-line interface for the TIKVARON image-generation package."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .service import ImageGenerationClient, ImageGenerationError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tikvaron-image",
        description="Generate, edit, and iteratively refine images with TIKVARON.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="Generate images with the Images API")
    _add_prompt_output(generate)
    _add_quality_size(generate)
    generate.add_argument("--count", type=int, default=1)

    edit = commands.add_parser("edit", help="Edit one or more reference images")
    _add_prompt_output(edit)
    edit.add_argument("--image", action="append", required=True, type=Path)
    edit.add_argument("--mask", type=Path)
    _add_quality_size(edit)
    edit.add_argument("--count", type=int, default=1)

    stream_images = commands.add_parser(
        "stream-images", help="Save progressive preview events from the Images API"
    )
    _add_prompt_output(stream_images)
    _add_quality_size(stream_images)
    stream_images.add_argument("--partial-images", type=int, default=2)

    upload = commands.add_parser("upload", help="Upload a reference image for Responses API use")
    upload.add_argument("--image", required=True, type=Path)

    respond = commands.add_parser(respond, help="Generate or refine using the Responses API")
    _add_prompt_output(respond)
    _add_quality_size(respond)
    _add_conversation_options(respond)
    respond.add_argument("--reference-image", action="append", type=Path, default=[])
    respond.add_argument("--reference-file-id", action="append", default=[])
    respond.add_argument("--mask-file-id")


    stream = commands.add_parser("stream", help="Stream partial and final image outputs")
    _add_prompt_output(stream)
    _add_quality_size(stream)
    _add_conversation_options(stream)
    stream.add_argument("--partial-images", type=int, default=2)

    return parser


def _add_prompt_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--output", required=True, type=Path)


def _add_quality_size(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--quality", default="auto")
    parser.add_argument("--size", default="auto")


def _add_conversation_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--previous-response-id")
    parser.add_argument("--action", choices=("auto", "generate", "edit"), default="auto")


def _serialize_result(result: object) -> dict[str, object]:
    paths = getattr(result, "paths", ())
    partial_paths = getattr(result, "partial_paths", ())
    return {
        "model": getattr(result, "model", None),
        "response_id": getattr(result, "response_id", None),
        "paths": [str(Path(path)) for path in paths],
        "partial_paths": [str(Path(path)) for path in partial_paths],
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        generator = ImageGenerationClient()
        if args.command == "upload":
            file_id = generator.upload_vision_file(args.image)
            print(json.dumps({"status": "uploaded", "file_id": file_id}, indent=2))
            return 0
        if args.command == "generate":
            result = generator.generate(
                args.prompt,
                args.output,
                quality=args.quality,
                size=args.size,
                n=args.count,
            )
        elif args.command == "edit":
            references = args.image[0] if len(args.image) == 1 else args.image
            result = generator.edit(
                args.prompt,
                references,
                args.output,
                mask=args.mask,
                quality=args.quality,
                size=args.size,
                n=args.count,
            )
        elif args.command == "stream-images":
            result = generator.stream_with_images(
                args.prompt,
                args.output,
                partial_images=args.partial_images,
                quality=args.quality,
                size=args.size,
            )
        elif args.command == "respond":
            result = generator.generate_with_responses(
                args.prompt,
                args.output,
                previous_response_id=args.previous_response_id,
                action=args.action,
                quality=args.quality,
                size=args.size,
                reference_images=args.reference_image,
                reference_file_ids=args.reference_file_id,
                mask_file_id=args.mask_file_id,
            )
        elif args.command == "stream":
            result = generator.stream_with_responses(
                args.prompt,
                args.output,
                previous_response_id=args.previous_response_id,
                action=args.action,
                partial_images=args.partial_images,
                quality=args.quality,
                size=args.size,
            )
    except (ImageGenerationError, ValueError, FileNotFoundError, RuntimeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        return 2

    record = {"status": "completed", **_serialize_result(result)}
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by the installed entry point
    raise SystemExit(main())
