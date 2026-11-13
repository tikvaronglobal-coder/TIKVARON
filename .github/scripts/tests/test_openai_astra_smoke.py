from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

# The smoke script only needs these SDK names at import time; tests inject a
# fake client so the test suite never sends a network request.
if "openai" not in sys.modules:
    openai_stub = types.ModuleType("openai")
    openai_stub.OpenAI = object
    openai_stub.APIError = type("APIError", (Exception,), {})
    sys.modules["openai"] = openai_stub

smoke = importlib.import_module("openai_astra_smoke")


class FakeResponses:
    def __init__(self, output_text: str = smoke.EXPECTED_OUTPUT):
        self.output_text = output_text
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return types.SimpleNamespace(
            output_text=self.output_text,
            model="gpt-6-astra",
            _request_id="req_tikvaron_test",
            usage=types.SimpleNamespace(input_tokens=13, output_tokens=5, total_tokens=18),
        )


class FakeClient:
    def __init__(self, output_text: str = smoke.EXPECTED_OUTPUT):
        self.responses = FakeResponses(output_text)


class AstraSmokeTests(unittest.TestCase):
    def test_uses_responses_api_and_records_a_successful_inference(self):
        client = FakeClient()
        with tempfile.TemporaryDirectory() as temporary:
            result_path = Path(temporary) / "result.json"
            env = {
                "OPENAI_API_KEY": "test-key",
                "TIKVARON_ASTRA_MODEL": "gpt-6-astra",
                "TIKVARON_REASONING_EFFORT": "low",
                "TIKVARON_SMOKE_RESULT_PATH": str(result_path),
            }
            with patch.dict(os.environ, env, clear=True), patch.object(smoke, "OpenAI", return_value=client), contextlib.redirect_stdout(io.StringIO()):
                exit_code = smoke.main()

            self.assertEqual(exit_code, 0)
            self.assertEqual(client.responses.kwargs["model"], "gpt-6-astra")
            self.assertEqual(client.responses.kwargs["reasoning"], {"effort": "low"})
            self.assertEqual(client.responses.kwargs["max_output_tokens"], 64)
            self.assertIs(client.responses.kwargs["store"], False)
            self.assertEqual(
                client.responses.kwargs["input"],
                "Reply with exactly this token and no other text: TIKVARON_ASTRA_INFERENCE_OK",
            )
            self.assertNotIn("api_key", client.responses.kwargs)
            self.assertTrue(result_path.read_bytes().endswith(b"\n"))
            record = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(record["status"], "passed")
            self.assertEqual(record["endpoint"], "v1/responses")
            self.assertEqual(record["request_id"], "req_tikvaron_test")
            self.assertEqual(
                record["usage"],
                {"input_tokens": 13, "output_tokens": 5, "total_tokens": 18},
            )

    def test_rejects_a_nonmatching_inference_sentinel(self):
        client = FakeClient("not-the-sentinel")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True), patch.object(smoke, "OpenAI", return_value=client), contextlib.redirect_stderr(io.StringIO()):
            exit_code = smoke.main()
        self.assertEqual(exit_code, 1)

    def test_blocks_when_api_key_is_missing(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(smoke, "OpenAI") as openai_client, contextlib.redirect_stderr(io.StringIO()):
            exit_code = smoke.main()
        self.assertEqual(exit_code, 2)
        openai_client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
