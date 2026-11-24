# TIKVARON Sales Growth

Private Next.js application for validating TIKVARON's HubSpot CRM integration.

## Current implementation
- Dedicated application isolated at `apps/sales-growth`.
- Server-only HubSpot Service Key authentication using `HUBSPOT_PRIVATE_APP_TOKEN`.
- Read-only exact-email search for `tikvaron-integration-test@example.com`.
- No create, update, or delete CRM operations.
- Preview Basic Auth guard: when a service key is configured, `TIKVARON_PREVIEW_PASSWORD` is required.
- The browser never receives the HubSpot credential.

## Vercel Preview environment
Set these as sensitive environment variables for Preview only:
- `HUBSPOT_PRIVATE_APP_TOKEN`: HubSpot Service Key with `crm.objects.contacts.read` scope (write scope is not needed for this read-only test).
- `TIKVARON_PREVIEW_PASSWORD`: long unique Preview password.

Keep Vercel Deployment Protection enabled. Do not add either variable to Production. The application intentionally does not perform CRM writes in this first validation stage.

## Local verification
- `npm test`
- `npm run typecheck`
- `npm run build`

Node.js 20.9 or later is required.