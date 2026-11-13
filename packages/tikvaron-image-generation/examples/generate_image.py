"""Minimal example: python examples/generate_image.py"""
from pathlib import Path

from tikvaron_image_generation import ImageGenerationClient


output = Path("artifacts/tikvaron-example.png")
result = ImageGenerationClient().generate(
    "An illustrated baby otter wearing a tiny orange scarf, children's-book-style",
    output,
    quality="high",
)
print(f"Saved {len(result.paths)} image(s): {', '.join(map(str, result.paths))}")
