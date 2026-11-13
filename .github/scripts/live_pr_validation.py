"""Read-only validation against exactly three real PRs in this repository."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from time import perf_counter
from datetime import datetime, timezone

PACKAGE_ROOT = Path.cwd().resolve()
REPOSITORY_ROOT = Path(os.environ.get("GITHUB_WORKSPACE", PACKAGE_ROOT)).resolve()
sys.path.insert(0, str(PACKAGE_ROOT / "src"))

from tikvaron_engineering.github_api import GitHubClient  # noqa: E402
from tikvaron_engineering.pipeline import EngineeringIntelligencePipeline  # noqa: E402

INPUT_PRICE_PER_MILLION = float(os.getenv("TIKVARON_INPUT_PRICE_PER_MILLION", "2"))
OUTPUT_PRICE_PER_MILLION = float(os.getenv("TIKVARON_OUTPUT_PRICE_PER_MILLION", "10"))


def main() -> None:
    required = ("GITHUB_TOKEN", "GITHUB_REPOSITORY", "OPENAI_API_KEY", "TIKVARON_VALIDATION_PR_NUMBERS")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        print(f"LIVE PR VALIDATION BLOCKED: missing {', '.join(missing)}", file=sys.stderr)
        raise SystemExit(2)

    repository = os.environ["GITHUB_REPOSITORY"]
    try:
        numbers = [int(item.strip()) for item in os.environ["TIKVARON_VALIDATION_PR_NUMBERS"].split(",") if item.strip()]
    except ValueError as exc:
        raise SystemExit("PR numbers must be integers, comma-separated.") from exc
    if len(numbers) != 3 or len(set(numbers)) != 3:
        raise SystemExit("Set exactly three unique PR numbers, e.g. 12,34,56.")

    github = GitHubClient(os.environ["GITHUB_TOKEN"])
    pipeline = EngineeringIntelligencePipeline()
    results = []
    for number in numbers:
        metadata = github.get_pull_request_info(repository, number)
        if metadata.get("state") != "open":
            raise RuntimeError(f"PR #{number} is not open; pilot requires reviewable open PRs.")
        diff = github.get_pull_request_diff(repository, number)
        context = "\n".join([
            f"Title: {metadata.get('title', '')}",
            f"Base: {(metadata.get('base') or {}).get('ref', '')}",
            f"Head: {(metadata.get('head') or {}).get('ref', '')}",
            f"Description: {(metadata.get('body') or '')[:3000]}",
        ])
        started = perf_counter()
        review = pipeline.review(diff, pull_request_context=context, repository_root=REPOSITORY_ROOT)
        latency_ms = round((perf_counter() - started) * 1000, 2)
        record = review.to_dict()
        usage = record.get("usage") or {}
        input_tokens = int(usage.get("input_tokens") or 0)
        output_tokens = int(usage.get("output_tokens") or 0)
        estimated_cost_usd = (
            input_tokens * INPUT_PRICE_PER_MILLION
            + output_tokens * OUTPUT_PRICE_PER_MILLION
        ) / 1_000_000
        results.append({
            "repository": repository,
            "pr_number": number,
            "url": metadata.get("html_url"),
            "base_sha": (metadata.get("base") or {}).get("sha"),
            "head_sha": (metadata.get("head") or {}).get("sha"),
            "title": metadata.get("title"),
            "changed_files": metadata.get("changed_files"),
            "latency_ms": latency_ms,
            "usage": usage,
            "estimated_cost_usd": round(estimated_cost_usd, 8),
            "review": record,
            "human_scoring": {
                "true_positives": None,
                "false_positives": None,
                "false_negatives": None,
                "severity_calibration_notes": None,
                "maintainer": None,
            },
        })
        print(f"Validated {repository}#{number}: {len(review.findings)} finding(s), {latency_ms} ms")

    output = PACKAGE_ROOT / "artifacts" / "live-pr-validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({
        "created_at": datetime.now(timezone.utc).isoformat(),
        "repository": repository,
        "model": results[0]["review"]["model"],
        "pr_count": len(results),
        "read_only": True,
        "pricing_assumption_usd_per_million": {
            "input": INPUT_PRICE_PER_MILLION,
            "output": OUTPUT_PRICE_PER_MILLION,
        },
        "totals": {
            "input_tokens": sum(int(item["usage"].get("input_tokens") or 0) for item in results),
            "output_tokens": sum(int(item["usage"].get("output_tokens") or 0) for item in results),
            "estimated_cost_usd": round(sum(item["estimated_cost_usd"] for item in results), 8),
            "latency_ms": sum(item["latency_ms"] for item in results),
        },
        "note": "Review runs are live. Accuracy/precision/recall remain unscored until maintainers annotate findings; false negatives require an independent defect ground truth.",
        "pull_requests": results,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"LIVE PR VALIDATION PASSED: {output}")


if __name__ == "__main__":
    main()
