from types import SimpleNamespace
import unittest

from tikvaron_engineering.ai import review_pull_request, run_fast_response


class FakeBetaResponses:
    def __init__(self, response):
        self.response = response
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.response


class FakeResponses:
    def __init__(self, response):
        self.response = response
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.response


class FakeClient:
    def __init__(self, *, beta_response=None, regular_response=None):
        self.beta = SimpleNamespace(
            responses=FakeBetaResponses(beta_response)
        )
        self.responses = FakeResponses(regular_response)


class AIReviewTests(unittest.TestCase):
    def test_multi_agent_review_uses_beta_and_extracts_root_final(self):
        response = SimpleNamespace(
            id="resp_test_123",
            service_tier="standard",
            usage={
                "input_tokens": 120,
                "output_tokens": 42,
                "total_tokens": 162,
            },
            output=[
                SimpleNamespace(
                    type="message",
                    agent=SimpleNamespace(agent_name="/security"),
                    phase="final_answer",
                    content=[SimpleNamespace(type="output_text", text="ignore")],
                ),
                SimpleNamespace(
                    type="message",
                    agent=SimpleNamespace(agent_name="/root"),
                    phase="final_answer",
                    content=[SimpleNamespace(type="output_text", text="## Review\nNo findings.")],
                ),
            ],
        )
        client = FakeClient(beta_response=response)
        telemetry = {}

        result = review_pull_request(
            "diff --git a/a.py b/a.py",
            client=client,
            telemetry=telemetry,
        )

        self.assertEqual(result, "## Review\nNo findings.")
        self.assertTrue(client.beta.responses.kwargs["multi_agent"]["enabled"])
        self.assertEqual(client.beta.responses.kwargs["multi_agent"]["max_concurrent_subagents"], 3)
        self.assertEqual(client.beta.responses.kwargs["betas"], ["responses_multi_agent=v1"])
        self.assertEqual(telemetry["response_id"], "resp_test_123")
        self.assertEqual(telemetry["usage"]["total_tokens"], 162)
        self.assertEqual(telemetry["endpoint"], "beta.responses")

    def test_multi_agent_review_rejects_empty_diff(self):
        with self.assertRaises(ValueError):
            review_pull_request("  ", client=FakeClient())

    def test_multi_agent_review_requires_root_final_answer(self):
        client = FakeClient(beta_response=SimpleNamespace(output=[]))
        with self.assertRaises(RuntimeError):
            review_pull_request("diff", client=client)

    def test_fast_response_uses_regular_responses_endpoint(self):
        client = FakeClient(regular_response=SimpleNamespace(output_text="Hello"))

        result = run_fast_response("Say hello", client=client)

        self.assertEqual(result, "Hello")
        self.assertEqual(client.responses.kwargs["model"], "gpt-6-astra")
        self.assertEqual(client.responses.kwargs["service_tier"], "ultrafast")

    def test_fast_response_rejects_empty_prompt(self):
        with self.assertRaises(ValueError):
            run_fast_response("", client=FakeClient())


if __name__ == "__main__":
    unittest.main()
