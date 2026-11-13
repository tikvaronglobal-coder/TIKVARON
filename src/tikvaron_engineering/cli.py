"""Command-line entry point used by the GitHub Actions PR-review workflow."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from .ai import REVIEW_MODEL, review_pull_request


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a GitHub pull-request diff")
    parser.add_argument("--diff", required=True, help="Path to a unified diff file")
    parser.add_argument("--output", required=True, help="Path for the Markdown review")
    parser.add_argument(
        "--metrics",
        help="Optional path for request usage and latency metadata (JSON)",
    )
    args = parser.parse_args()

    diff_path = Path(args.diff)
    output_path = Path(args.output)
    diff = diff_path.read_text(encoding="utf-8")

    metadata: dict[str, object] = {}
    started_at = datetime.now(timezone.utc)
    start = time.perf_counter()
    review = review_pull_request(diff, telemetry=metadata)
    completed_at = datetime.now(timezone.utc)
    metadata.update(
        {
            "model": metadata.get("model", REVIEW_MODEL),
            "repository": os.getenv("GITHUB_REPOSITORY"),
            "pr_number": os.getenv("PR_NUMBER"),
            "pr_head_sha": os.getenv("PR_HEAD_SHA"),
            "workflow_run_id": os.getenv("GITHUB_RUN_ID"),
            "workflow_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
            "diff_bytes": len(diff.encode("utf-8")),
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "latency_seconds": round(time.perf_counter() - start, 3),
        }
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(review.rstrip() + "\n", encoding="utf-8")

    if args.metrics:
        metrics_path = Path(args.metrics)
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True, default=str) + "\n",
            encoding="utf-8",
        )

    print(review)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
