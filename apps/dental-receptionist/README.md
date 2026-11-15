# TIKVARON Dental Receptionist — staging starter

A Next.js staging foundation for the TIKVARON dental receptionist. It uses a server-side OpenAI Responses API call for text conversation when explicitly configured.

## Current scope

- Conversational text demo with recent-turn context held in the browser session.
- API key is read only on the server from `OPENAI_API_KEY`.
- Model is selected through server environment variable `OPENAI_MODEL`.
- OpenAI request uses `store: false`.
- No database, clinic records, phone number, booking system, voice transport, or staff handover is connected.
- No real clinic facts are configured. The assistant must not invent hours, fees, availability, or bookings.
- Do not enter real patient or health information.

## Local setup

1. Install Node.js 20.9 or later.
2. Run `npm install` in this directory.
3. Copy `.env.example` to `.env.local` and add approved staging values.
4. Run `npm run dev` and open http://localhost:3000.

## Vercel

Set the project root directory to `apps/dental-receptionist`. Add `OPENAI_API_KEY` as a sensitive server-side environment variable and `OPENAI_MODEL` as a server-side variable only after model selection and spend approval. Start with Preview only. Never expose either variable with a `NEXT_PUBLIC_` prefix.

Do not add production patient data. Before any live clinic pilot, complete privacy, data residency, retention, security, escalation, and human-oversight review. Confirm the chosen model and current API pricing first.

## Not yet implemented

Real-time voice, telephony/SIP, appointment booking, clinic knowledge-base management, authenticated staff handover, audit trail, consent capture, rate limiting, abuse protection, and production monitoring.