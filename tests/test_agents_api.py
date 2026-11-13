from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tikvaron_engineering.agents_api import (
    DEFAULT_SESSION_SPEND_LIMIT_CENTS,
    MAX_DIFF_BYTES,
    review_pull_request_with_agents,
)


class FakeStream:
    def __init__(self, events, result, session_id="sess_test_123"):
        self.events = events
        self.result = result
        self.session_id = session_id
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
    def make_client(self, *, events=None, output_text="## Review\nNo actionable findings.", session_id="sess_test_123"):
        if events is None:
            events = [
                SimpleNamespace(
                    type="agent.session.turn.completed",
                    turn=SimpleNamespace(subagent_id=None),
                    session_id=session_id,
                )
            ]
        stream = FakeStream(
            events,
            SimpleNamespace(
                output_text=output_text,
                session_id=session_id,
                spend_control=SimpleNamespace(consumed=15, limit=100),
                usage=SimpleNamespace(input_tokens=100, output_tokens=30, total_tokens=130),
            ),
            session_id=session_id,
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
        self.assertEqual(kwargs["spend_control"], {"limit": DEFAULT_SESSION_SPEND_LIMIT_CENTS})
        self.assertTrue(stream.entered)
        self.assertTrue(stream.exited)
        self.assertEqual(telemetry["session_id"], "sess_test_123")
        self.assertEqual(telemetry["session_cleanup"], "deleted")
        self.assertEqual(telemetry["spend_limit_cents"], 100)
        self.assertEqual(telemetry["spend_control"]["consumed"], 15)
        self.assertEqual(telemetry["usage"]["total_tokens"], 130)
        self.assertTrue(telemetry["root_turn_completed"])
        self.assertTrue(telemetry["completed"])
        self.assertEqual(client.sessions.deleted, ["sess_test_123"])

    def test_subagent_failure_does_not_abort_root_and_is_disclosed(self):
        events = [
            SimpleNamespace(
                type="agent.session.turn.failed",
                turn=SimpleNamespace(subagent_id="subagent_1"),
                session_id="sess_test_123",
            ),
            SimpleNamespace(
                type="agent.session.turn.completed",
                turn=SimpleNamespace(subagent_id=None),
                session_id="sess_test_123",
            ),
        ]
        client, _ = self.make_client(events=events)
        telemetry = {}

        result = review_pull_request_with_agents("diff", client=client, telemetry=telemetry)

        self.assertIn("Coverage caveat", result)
        self.assertIn("1 specialist subagent turn(s) did not complete", result)
        self.assertEqual(telemetry["subagent_failures"], ["agent.session.turn.failed"])
        self.assertTrue(telemetry["root_turn_completed"])
        self.assertEqual(client.sessions.deleted, ["sess_test_123"])

    def test_root_turn_failure_fails_closed_and_deletes_session(self):
        events = [
            SimpleNamespace(
                type="agent.session.turn.failed",
                turn=SimpleNamespace(subagent_id=None),
                session_id="sess_test_123",
            )
        ]
        client, stream = self.make_client(events=events)
        telemetry = {}

        with self.assertRaisesRegex(RuntimeError, "root turn did not complete"):
            review_pull_request_with_agents("diff", client=client, telemetry=telemetry)

        self.assertTrue(stream.exited)
        self.assertEqual(client.sessions.deleted, ["sess_test_123"])
        self.assertEqual(telemetry["failure_type"], "RuntimeError")
        self.assertFalse(telemetry["completed"])

    def test_stream_close_before_root_completion_fails_closed(self):
        events = [SimpleNamespace(type="agent.session.idle", session_id="sess_test_123")]
        client, _ = self.make_client(events=events)
        telemetry = {}

        with self.assertRaisesRegex(RuntimeError, "before the root turn completed"):
            review_pull_request_with_agents("diff", client=client, telemetry=telemetry)

        self.assertEqual(client.sessions.deleted, ["sess_test_123"])
        self.assertFalse(telemetry["root_turn_completed"])

    def test_session_id_from_event_is_used_for_cleanup(self):
        events = [
            SimpleNamespace(
                type="agent.session.turn.completed",
                turn=SimpleNamespace(subagent_id=None),
                session_id="sess_from_event",
            )
        ]
        client, _ = self.make_client(events=events, session_id=None)

        review_pull_request_with_agents("diff", client=client)

        self.assertEqual(client.sessions.deleted, ["sess_from_event"])

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

    def test_failure_lifecycle_event_fails_closed(self):
        client, _ = self.make_client(
            events=[SimpleNamespace(type="agent.session.environment.failed", session_id="sess_test_123")]
        )
        with self.assertRaisesRegex(RuntimeError, "environment.failed"):
            review_pull_request_with_agents("diff", client=client)
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

    def test_session_spend_limit_can_be_set_and_is_validated(self):
        client, _ = self.make_client()
        with patch.dict(os.environ, {"TIKVARON_AGENTS_SESSION_SPEND_LIMIT_CENTS": "250"}):
            review_pull_request_with_agents("diff", client=client)
        self.assertEqual(client.sessions.kwargs["spend_control"], {"limit": 250})

        client, _ = self.make_client()
        with patch.dict(os.environ, {"TIKVARON_AGENTS_SESSION_SPEND_LIMIT_CENTS": "0"}):
            with self.assertRaisesRegex(ValueError, "between 1 and 10000"):
                review_pull_request_with_agents("diff", client=client)
        self.assertIsNone(client.sessions.kwargs)

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
