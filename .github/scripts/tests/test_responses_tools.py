from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from responses_tools import (
    ToolApprovalRequired,
    ToolExecutionError,
    build_responses_tools,
    run_responses_agent,
)


class FakeResponses:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if not self.responses:
            raise AssertionError("Unexpected extra Responses API call")
        return self.responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.responses = FakeResponses(responses)


class ResponsesToolsTests(unittest.TestCase):
    def test_web_and_file_search_are_opt_in(self):
        default_tools = build_responses_tools()
        self.assertNotIn("web_search", [tool["type"] for tool in default_tools])
        self.assertNotIn("file_search", [tool["type"] for tool in default_tools])

        configured = build_responses_tools(
            enable_web_search=True,
            vector_store_id="vs_tikvaron_docs",
        )
        self.assertIn("web_search", [tool["type"] for tool in configured])
        file_search = next(tool for tool in configured if tool["type"] == "file_search")
        self.assertEqual(file_search["vector_store_ids"], ["vs_tikvaron_docs"])
        with self.assertRaises(ValueError):
            build_responses_tools(vector_store_id="   ")

    def test_namespace_contains_strict_functions_and_deferred_tool(self):
        tools = build_responses_tools(enable_tool_search=True)
        namespace = next(tool for tool in tools if tool["type"] == "namespace")
        self.assertEqual(namespace["name"], "engineering")
        by_name = {tool["name"]: tool for tool in namespace["tools"]}
        self.assertTrue(by_name["get_repository_context"]["strict"])
        self.assertTrue(by_name["list_changed_paths"]["strict"])
        self.assertTrue(by_name["list_changed_paths"]["defer_loading"])
        self.assertIn("tool_search", [tool["type"] for tool in tools])

    def test_mcp_requires_https_and_explicit_approval(self):
        with self.assertRaises(ValueError):
            build_responses_tools(mcp_server_url="http://example.com/mcp")
        tools = build_responses_tools(
            mcp_server_url="https://developers.openai.com/mcp",
            mcp_server_label="openai_docs",
        )
        mcp = next(tool for tool in tools if tool["type"] == "mcp")
        self.assertEqual(mcp["require_approval"], "always")

    def test_local_function_call_round_trip_is_read_only_and_bounded(self):
        first = SimpleNamespace(
            id="resp_first",
            output=[
                SimpleNamespace(
                    type="function_call",
                    name="engineering.list_changed_paths",
                    call_id="call_123",
                    arguments='{"limit": 10}',
                )
            ],
        )
        final = SimpleNamespace(id="resp_final", output=[], output_text="Reviewed two changed files.")
        client = FakeClient([first, final])
        diff = (
            "diff --git a/src/a.py b/src/a.py\n"
            "diff --git a/tests/test_a.py b/tests/test_a.py\n"
        )

        result = run_responses_agent(client, "Summarize the changes.", diff=diff)

        self.assertEqual(result, "Reviewed two changed files.")
        self.assertEqual(len(client.responses.calls), 2)
        continuation = client.responses.calls[1]
        self.assertEqual(continuation["previous_response_id"], "resp_first")
        self.assertFalse(continuation["store"])
        tool_output = continuation["input"][0]
        self.assertEqual(tool_output["type"], "function_call_output")
        self.assertEqual(tool_output["call_id"], "call_123")
        self.assertEqual(
            json.loads(tool_output["output"]),
            {"paths": ["src/a.py", "tests/test_a.py"]},
        )

    def test_repository_context_exposes_only_workflow_metadata(self):
        final = SimpleNamespace(id="resp_final", output=[], output_text="Context loaded.")
        with patch.dict(
            os.environ,
            {
                "GITHUB_REPOSITORY": "tikvaronglobal-coder/TIKVARON",
                "GITHUB_REF": "refs/heads/main",
                "GITHUB_SHA": "abc123",
                "OPENAI_API_KEY": "must-not-be-returned",
            },
            clear=True,
        ):
            first = SimpleNamespace(
                id="resp_first",
                output=[
                    SimpleNamespace(
                        type="function_call",
                        name="get_repository_context",
                        call_id="call_context",
                        arguments="{}",
                    )
                ],
            )
            client = FakeClient([first, final])
            result = run_responses_agent(client, "Read repository context.")
        self.assertEqual(result, "Context loaded.")
        payload = json.loads(client.responses.calls[1]["input"][0]["output"])
        self.assertEqual(payload["repository"], "tikvaronglobal-coder/TIKVARON")
        self.assertNotIn("OPENAI_API_KEY", payload)

    def test_unsupported_function_fails_closed(self):
        first = SimpleNamespace(
            id="resp_first",
            output=[
                SimpleNamespace(
                    type="function_call",
                    name="delete_repository",
                    call_id="call_bad",
                    arguments="{}",
                )
            ],
        )
        client = FakeClient([first])
        with self.assertRaises(ToolExecutionError):
            run_responses_agent(client, "Do something unsafe.")

    def test_mcp_approval_is_never_automatically_accepted(self):
        first = SimpleNamespace(
            id="resp_first",
            output=[
                SimpleNamespace(
                    type="mcp_approval_request",
                    id="approval_123",
                )
            ],
        )
        client = FakeClient([first])
        with self.assertRaises(ToolApprovalRequired) as raised:
            run_responses_agent(
                client,
                "Search the docs.",
                mcp_server_url="https://developers.openai.com/mcp",
            )
        self.assertEqual(raised.exception.approval_request_id, "approval_123")
        self.assertEqual(len(client.responses.calls), 1)


if __name__ == "__main__":
    unittest.main()
