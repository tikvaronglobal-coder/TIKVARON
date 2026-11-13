"""Run one explicit GPT-6 Astra authentication and inference smoke test.

This script is invoked only by the manually dispatched, opt-in workflow. It
uses the Responses API without tools, makes a single request (SDK retries are
disabled), and never prints the API key or request headers.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

from openai import APIError, OpenAI

EXPECTED_OUTPUT = "TIKVARON_ASTRA_INFERENCE_OK"
DEFAULT_MODEL = "gpt-6-astra"


def write_result(result: dict[str, object]) -> None:
    output_path = os.getenv("TIKVARON_SMOKE_RESULT_PATH")
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    stream = sys.stdout if result.get("status") == "passed" else sys.stderr
    print(json.dumps(result, indent=2), file=stream)


def main() -> int:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("TIKVARON_ASTRA_MODEL", DEFAULT_MODEL).strip()
    reasoning_effort = os.getenv("TIKVARON_REASONING_EFFORT", "low").strip()

    if not api_key:
        write_result({
            "status": "blocked",
            "model_requested": model,
            "reason": "OPENAI_API_KEY is not configured as a GitHub Actions secret.",
        })
        return 2
    if not model:
        write_result({"status": "blocked", "reason": "TIKVARON_ASTRA_MODEL is empty."})
        return 2

    client = OpenAI(api_key=api_key, timeout=60.0, max_retries=0)
    try:
        response = client.responses.create(
            model=model,
            input=(
                "Reply with exactly this token and no other text: "
                f"{EXPECTED_OUTPUT}"
            ),
            reasoning={"effort": reasoning_effort},
            max_output_tokens=64,
            store=False,
        )
    except APIError as exc:
        write_result({
            "status": "failed",
            "model_requested": model,
            "endpoint": "v1/responses",
            "error_type": type(exc).__name__,
            "http_status": getattr(exc, "status_code", None),
            "request_id": getattr(exc, "request_id", None),
            "reason": "OpenAI rejected or could not complete the smoke-test request. Check API key access, project permissions, usage tier, and model availability.",
        })
        return 1
    except Exception as exc:  # Keep unexpected errors safe to print in CI logs.
        write_result({
            "status": "failed",
            "model_requested": model,
            "endpoint": "v1/responses",
            "error_type": type(exc).__name__,
            "reason": "Unexpected smoke-test error; no credential data was logged.",
        })
        return 1

    content = (getattr(response, "output_text", None) or "").strip()
    request_id = getattr(response, "_request_id", None)
    usage = getattr(response, "usage", None)
    usage_record = {
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }

    if content != EXPECTED_OUTPUT:
        write_result({
            "status": "failed",
            "model_requested": model,
            "model_returned": getattr(response, "model", None),
            "endpoint": "v1/responses",
            "request_id": request_id,
            "usage": usage_record,
            "reason": "The API returned a response, but the exact inference sentinel did not match.",
        })
        return 1

    write_result({
        "status": "passed",
        "model_requested": model,
        "model_returned": getattr(response, "model", None),
        "endpoint": "v1/responses",
        "request_id": request_id,
        "reasoning_effort": reasoning_effort,
        "usage": usage_record,
        "inference_check": "exact sentinel matched",
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
