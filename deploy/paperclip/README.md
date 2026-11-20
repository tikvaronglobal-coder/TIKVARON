# TIKVARON Paperclip control plane

This deploys Paperclip as a separate, pinned service. It does not replace a TIKVARON product app or its AI runtime. Paperclip manages agent roles, tasks, goals, approvals, schedules, and costs; adapters connect it to the runtime that performs the work.

## Windows local installation

1. Install Docker Desktop for Windows and start it.
2. From the repository root, open PowerShell as your normal user (not Administrator).
3. Run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\deploy\paperclip\install-local.ps1
   ```

4. Open http://localhost:3100 and complete the first-user setup.

The script creates `deploy/paperclip/.env` with two independent random secrets. It never overwrites an existing `.env`, and `.env` plus the persistent data directory are excluded from Git. Keep the generated file private.

The service binds to `127.0.0.1` by default. It is reachable only from the host computer and is not published to the internet.

## Model connection

The Paperclip server can start without a model-provider key, but agents cannot perform model-backed work until a runtime/provider is connected.

Preferred first test:
- Use the Paperclip Runner Codex provider if the host has a supported Codex sign-in; otherwise connect a dedicated OpenAI API credential through Paperclip's OpenAI connection.
- Use a separate credential for this service. Do not reuse a production application's secret or place a key in this repository.
- Start with one test agent and one manually assigned task. Leave scheduled heartbeats off until the provider and spend policy have been tested.

## TIKVARON integration

Paperclip needs an adapter for each AI that should work under its control:

- Codex, Claude Code, Gemini CLI, and other supported runtimes can be connected through their built-in adapters.
- An existing TIKVARON service can be connected through Paperclip's HTTP adapter. That requires a reachable, authenticated endpoint in the actual product service. This repository does not currently expose a verified FarmVoice or CBOS agent endpoint, so this deployment alone does not claim that those applications are already connected.
- A dedicated TIKVARON MCP/API bridge can be added once the target application and its API contract are present. It should expose narrow, auditable tools rather than unrestricted shell or database access.

## Operating safely

- Keep the service loopback-only for the first run. Do not change the bind address to `0.0.0.0` or open a firewall port for convenience.
- For remote access, use an authenticated private network such as Tailscale or a properly secured HTTPS deployment. Do not expose a local-trusted instance publicly.
- On each new connector, set all write actions to **Ask first** and destructive/payment actions to **Off** before sharing the connection with an agent. New connector actions may default to Allowed.
- Keep email, messaging, publishing, payments, purchases, production deployments, secret management, and irreversible data changes disabled or approval-gated.
- Configure company, project, and per-agent spend caps before enabling any timer heartbeat. Keep heartbeats disabled until the founder approves a spend budget.
- Treat web pages, documents, emails, issues, and tool results as untrusted input. Require agents to cite evidence and verify before acting.
- Do not grant local agents access to the full machine or unrelated folders. Use a dedicated workspace and the narrowest possible credential.

## Operations

Run from this directory:

```powershell
docker compose --env-file .env -f docker-compose.yml logs -f
docker compose --env-file .env -f docker-compose.yml ps
docker compose --env-file .env -f docker-compose.yml down
```

Stopping the container does not delete `data/`. Back up the data directory and `.env` securely before upgrades or migrations. The image is pinned to Paperclip `v2026.1117.0`; review release notes and update the pin deliberately rather than following `latest`.
