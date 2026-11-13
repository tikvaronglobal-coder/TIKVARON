# Responses API tool integration

TIKVARON's optional tool layer is implemented in
\`.github/scripts/responses_tools.py\` and overlaid into the restored
\`tikvaron_engineering\` package as \`tikvaron_engineering.responses_tools\`.
The pinned v0.2.0 source ZIP remains unchanged.

## Capability mapping

| Responses API capability | TIKVARON engineering use | Default |
|---|---|---|
| \`web_search\` | Research current advisories, vendor docs, and API changes | Disabled |
| \`file_search\` | Retrieve approved internal engineering knowledge from a vector store | Disabled until a vector-store ID is supplied |
| Namespace functions + \`tool_search\` | Organize read-only repository tools and defer the changed-path helper | Enabled in the optional helper |
| Strict function calling | Obtain repository metadata and changed paths through validated JSON schemas | Read-only allowlist |
| Remote MCP | Connect an approved documentation service | Disabled until an HTTPS URL is supplied; approval required |

GPT-6 Astra supports the Responses API and these tool types. Tool availability
is model-dependent; check the selected model's documentation before enabling
a new capability.

## Usage

The helper is a reusable Python integration. It does not run during CI and is
not wired into the normal PR-review workflow automatically.

\`\`\`python
from openai import OpenAI
from tikvaron_engineering.responses_tools import run_responses_agent

client = OpenAI(max_retries=0, timeout=60.0)
result = run_responses_agent(
    client,
    "Review the supplied diff and identify changes that need further research.",
    diff=diff_text,
    enable_web_search=True,
    vector_store_id=None,  # Set only after creating an approved vector store.
    mcp_server_url=None,   # Set only for an approved HTTPS MCP service.
)
print(result)
\`\`\`

The default model is \`gpt-6.1-sol\`, preserving the existing TIKVARON review
model. Select Astra only after PR #5's manual authentication/inference gate has
passed and a maintainer intentionally configures it.

## Tool behavior and controls

- Web search is included only when \`enable_web_search=True\`.
- File search is included only when a real \`vector_store_id\` is supplied. The
  repository does not invent or create a vector store for the operator.
- The \`engineering\` namespace exposes \`get_repository_context\` and a
  deferred \`list_changed_paths\` function. Both are read-only. The latter
  parses path labels from the supplied diff; it never opens or executes them.
- \`tool_search\` lets the model discover the deferred function. The runtime
  serializes local tool calls with \`parallel_tool_calls=False\`, enforces a
  four-round ceiling, and fails closed on unknown functions or invalid input.
- MCP requires an absolute HTTPS URL and uses \`require_approval="always"\`.
  The helper raises \`ToolApprovalRequired\` rather than silently approving a
  remote tool. A trusted application must handle the approval continuation.
- Responses are created with \`store=False\`. The caller should disable SDK
  retries for any explicitly metered live run and retain the existing workflow
  approval gates.
- No GitHub token, OpenAI key, or provider secret is exposed through the
  repository-context function.

## Validation

Offline unit tests use fake Responses API objects. They validate the tool
manifest, strict schemas, deferred discovery, function-call round trips,
read-only outputs, untrusted diff-path handling, and MCP approval behavior.
They do not make an OpenAI request, need API credentials, or verify external
service access.

## Official references

- [Responses API web search](https://developers.openai.com/api/docs/guides/tools-web-search)
- [Responses API file search](https://developers.openai.com/api/docs/guides/tools-file-search)
- [Function calling, namespaces, and tool search](https://developers.openai.com/api/docs/guides/function-calling)
- [Tool search guide](https://developers.openai.com/api/docs/guides/tools-tool-search)
- [Remote MCP servers](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)
- [GPT-6 Astra model capabilities](https://developers.openai.com/api/docs/models/gpt-6-astra)
