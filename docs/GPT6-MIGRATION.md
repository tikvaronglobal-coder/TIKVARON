# GPT-6 model family migration

## Model assignments

TIKVARON already uses the GPT-6 family for its engineering intelligence workloads:

- **PR review:** `gpt-6.1-sol` remains the default for multi-agent code review. It provides strong coding and reasoning capability at lower cost than Astra.
- **High-capability inference:** `gpt-6-astra` remains the explicit model for the manual authentication and inference smoke test. After the test succeeds, maintainers may set the Actions variable `TIKVARON_ASTRA_MODEL=gpt-6-astra` to route PR review traffic to Astra.
- **High-volume workloads:** Evaluate `gpt-6-luna` for repeatable, cost-sensitive tasks before assigning it production traffic.

The repository's `TIKVARON_OPENAI_MODEL` variable continues to provide the existing model selection. The optional Astra override takes precedence only after a successful smoke test. Model changes should be compared on representative reviews for finding quality, latency, token use, and cost per successful task.

## API migration

The Astra smoke test now uses the OpenAI Responses API. It sends one text input and reads the result from `response.output_text`; it no longer reads Chat Completions `choices[0].message.content`.

The smoke request:

- uses `reasoning={"effort": "low"}`, because GPT-6 Astra and GPT-6.1 Sol do not support `none`;
- uses `max_output_tokens=64`;
- sets `store=false` for this stateless check;
- disables SDK retries so the opt-in test sends at most one API request;
- validates the exact `TIKVARON_ASTRA_INFERENCE_OK` sentinel and records model, request ID, and token usage.

The multi-agent PR-review engine already uses Responses for its tool-enabled workflow. Keep tool orchestration on Responses. When reasoning effort is not `none`, omit unsupported sampling and log-probability parameters such as `temperature`, `top_p`, `top_logprobs`, and `logprobs`.

## Verification

CI runs the focused smoke-script unit tests without making a live API request. The real authentication and inference check remains a manual GitHub Actions dispatch, and is disabled by default. Set `run_astra_smoke=true` in **Actions → TIKVARON Engineering Intelligence — Live Validation** only when the API call is intended.

## Official references

- [Using GPT-6 and migration guidance](https://developers.openai.com/api/docs/guides/latest-model)
- [Reasoning models and GPT-6 compatibility](https://developers.openai.com/api/docs/guides/reasoning)
- [Migrate to the Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [OpenAI model catalog](https://developers.openai.com/api/docs/models)
