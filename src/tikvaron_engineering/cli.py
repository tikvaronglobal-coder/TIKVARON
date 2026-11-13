"""Command-line entry point used by the GitHub Actions PR-review workflow."""

from __future__ import annotations

import argparse
from pathlib import Path

from .ai import review_pull_request


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a GitHub pull-request diff")
    parser.add_argument("--diff", required=True, help="Path to a unified diff file")
    parser.add_argument("--output", required=True, help="Path for the Markdown review")
    args = parser.parse_args()

    diff_path = Path(args.diff)
    output_path = Path(args.output)
    review = review_pull_request(diff_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(review.rstrip() + "\n", encoding="utf-8")
    print(review)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
