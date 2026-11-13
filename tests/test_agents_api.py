from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tikvaron_engineering.agents_api import (
    MAX_DIFF_BYTES,
    review_pull_request_with_agents,
)


class FakeStream:
    def __init__(self, events, result):
        self.events = events
        self.result = result
        self.session_id = "sess_test_123"
        self.entered = False
        self.exited = False

    def with_result_collection(self):
        return self

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self.exited = True
        return False

    def __iter__(self):
        return iter(self.events)

    def get_final_result(self):
        return self.result


class FakeSessions:
    def __init__(self, stream):
        self.stream = stream
        self.kwargs = None
        self.deleted = []

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.stream

    def delete(self, session_id):
        self.deleted.append(session_id)


class FakeClient:
    def __init__(self, stream):
        self.sessions = FakeSessions(stream)
        self.beta = SimpleNamespace(agents=SimpleNamespace(sessions=self.sessions))


class AgentsApiReviewTests(unittest.TestCase):
    def make_client(self, *, events=None, output_text="## Review\nNo actionable findings."):
        stream = FakeStream(
            events or [SimpleNamespace(type="agent.session.turn.completed")],
            SimpleNamespace(output_text=output_text, session_id="sess_test_123"),
        )
        return FakeClient(stream), stream

    def test_creates_no_environment_multi_agent_session_and_extracts_output(self):
        client, stream = self.make_client()
        telemetry = {}

        result = review_pull_request_with_agents(
            "diff --git a/app.py b/app.py\n+return True",
            client=client,
            telemetry=telemetry,
        )

        self.assertIn("No actionable findings", result)
        kwargs = client.sessions.kwargs
        self.assertEqual(kwargs["environment"], {"type": "none"})
        self.assertTrue(kwargs["stream"])
        self.assertTrue(kwargs["agent"]["multi_agent"]["enabled"])
        self.assertEqual(kwargs["agent"]["multi_agent"]["max_concurrent_subagents"], 3)
        self.assertEqual(kwargs["agent"]["model"], "gpt-6.1-sol")
        self.assertEqual(kwargs["agent"]["tools"][0]["server_label"], "openai_docs")
        self.assertEqual(kwargs["agent"]["tools"][0]["connection_origin"], "service")
        self.assertEqual(kwargs["agent"]["tools"][1], {"type": "web_search"})
        self.assertTrue(stream.entered)
        self.assertTrue(stream.exited)
        self.assertEqual(telemetry["session_id"], "sess_test_123")
        self.assertEqual(telemetry["session_cleanup"], "deleted")
        self.assertEqual(client.sessions.deleted, ["sess_test_123"])
        self.assertTrue(telemetry["completed"])

    def test_empty_diff_is_rejected_before_session_creation(self):
        client, _ = self.make_client()
        with self.assertRaises(ValueError):
            review_pull_request_with_agents(" \n", client=client)
        self.assertIsNone(client.sessions.kwargs)

    def test_oversized_diff_is_rejected_before_session_creation(self):
        client, _ = self.make_client()
        with self.assertRaises(ValueError):
            review_pull_request_with_agents("x" * (MAX_DIFF_BYTES + 1), client=client)
        self.assertIsNone(client.sessions.kwargs)

    def test_failure_event_fails_closed(self):
        client, stream = self.make_client(events=[{"type": "agent.session.turn.failed"}])
        with self.assertRaisesRegex(RuntimeError, "turn.failed"):
            review_pull_request_with_agents("diff", client=client)
        self.assertTrue(stream.exited)
        self.assertEqual(client.sessions.deleted, ["sess_test_123"])

    def test_blank_final_output_is_rejected_and_session_is_deleted(self):
        client, _ = self.make_client(output_text="  ")
        with self.assertRaisesRegex(RuntimeError, "without a final review"):
            review_pull_request_with_agents("diff", client=client)
        self.assertEqual(client.sessions.deleted, ["sess_test_123"])

    def test_session_retention_can_be_enabled_for_debugging(self):
        client, _ = self.make_client()
        with patch.dict(os.environ, {"TIKVARON_AGENTS_KEEP_SESSIONS": "true"}):
            telemetry = {}
            review_pull_request_with_agents("diff", client=client, telemetry=telemetry)
        self.assertEqual(client.sessions.deleted, [])
        self.assertEqual(telemetry["session_cleanup"], "retained_by_configuration")

    def test_astra_model_is_blocked_until_pr5_gate_is_explicitly_passed(self):
        client, _ = self.make_client()
        with patch.dict(os.environ, {"TIKVARON_AGENTS_MODEL": "gpt-6-astra"}, clear=False):
            os.environ.pop("TIKVARON_ASTRA_VALIDATION_PASSED", None)
            with self.assertRaisesRegex(ValueError, "until PR #5"):
                review_pull_request_with_agents("diff", client=client)
        self.assertIsNone(client.sessions.kwargs)

    def test_astra_model_can_be_unlocked_only_with_validation_flag(self):
        client, _ = self.make_client()
        with patch.dict(
            os.environ,
            {
                "TIKVARON_AGENTS_MODEL": "gpt-6-astra",
                "TIKVARON_ASTRA_VALIDATION_PASSED": "true",
            },
        ):
            review_pull_request_with_agents("diff", client=client)
        self.assertEqual(client.sessions.kwargs["agent"]["model"], "gpt-6-astra")

    def test_subagent_limit_is_validated_before_session_creation(self):
        client, _ = self.make_client()
        with patch.dict(os.environ, {"TIKVARON_AGENTS_MAX_SUBAGENTS": "9"}):
            with self.assertRaisesRegex(ValueError, "between 1 and 4"):
                review_pull_request_with_agents("diff", client=client)
        self.assertIsNone(client.sessions.kwargs)


if __name__ == "__main__":
    unittest.main()
