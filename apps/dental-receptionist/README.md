# TIKVARON Dental Receptionist — staging starter

A Next.js staging foundation for the TIKVARON dental receptionist. It uses a server-side OpenAI Responses API call for text conversation when explicitly configured.

## Current scope

- Conversational text demo with recent-turn context held in the browser session.
- API key is read only on the server from `OPENAI_API_KEY`.
- Model is selected through server environment variable `OPENAI_MODEL`.
- OpenAI request uses `store: false`.
- When a billable API key is configured, HTTP Basic Auth protects the app and API through Next.js middleware.
- The deployment fails closed if `OPENAI_API_KEY` is set but `TIKVARON_PREVIEW_PASSWORD` is missing.
- OpenAI refusal content is returned to the interface as the assistant's safety response.
- GitHub Actions are pinned to verified immutable commit SHAs.
- No database, clinic records, phone number, booking system, voice transport, or staff handover is connected.
- No real clinic facts are configured. The assistant must not invent hours, fees, availability, or bookings.
- Do not enter real patient or health information.

## Local setup

1. Install Node.js 20.9 or later.
2. Run `npm install` in this directory.
3. Copy `.env.example` to `.env.local` and add approved staging values.
4. Run `npm run dev` and open http://localhost:3000.
5. If using a billable API key locally, set a strong `TIKVARON_PREVIEW_PASSWORD`; the browser will request HTTP Basic Auth credentials. Use any username and that password.

## Vercel

Set the project root directory to `apps/dental-receptionist`. Add these as sensitive/server-side Preview environment variables only after approval:

- `OPENAI_API_KEY`: project-scoped staging key.
- `OPENAI_MODEL`: approved model name.
- `TIKVARON_PREVIEW_PASSWORD`: a long, unique password stored in a password manager.

The app and API return HTTP 503 if a billable key is present without the password. Keep Vercel Deployment Protection enabled as an additional layer. Never expose these variables with a `NEXT_PUBLIC_` prefix. Do not add production patient data or enable a billable key until access protection and a spending limit have been configured and tested.

Before any live clinic pilot, complete privacy, data residency, retention, security, escalation, and human-oversight review. Confirm the chosen model and current API pricing first.

## Not yet implemented

Real-time voice, telephony/SIP, appointment booking, clinic knowledge-base management, authenticated staff handover, audit trail, consent capture, distributed rate limiting, and production monitoring. Basic Auth protects access to the staging deployment; it is not a substitute for production-grade user accounts and per-user quotas.
