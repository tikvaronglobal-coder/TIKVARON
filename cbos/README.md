# TIKVARON CBOS — Working Snapshot

This directory stores the current CBOS application source, partnership governance policy, and partner prospect/outreach register.

- `policy/TIKVARON_Partnership_Ownership_Policy.md` — canonical readable ownership and partnership controls.
- `partnerships/TIKVARON_Partnership_Register_2026-11-16.csv` — 20 organisation records: 14 inquiry-sent, 4 proposed/not-contacted and 2 on-hold.
- `register/source/` — exact HTML application source split into eight ordered chunks to preserve the full source through GitHub's text-file API. After cloning, run `python cbos/register/assemble_register.py` to reconstruct the standalone HTML file.

The HTML app is a standalone local application, not cloud-synced or multi-user. Browser data is local to the browser profile; export backups regularly. No secrets, API keys, passwords or credentials belong in this repository.

Fifteen outbound messages across fourteen organisation records were verified in Gmail Sent on 17 November 2026 (UTC+3 local date). QSTP has two separately addressed messages. Sent does not mean received, accepted or partnered.

This snapshot is on a dedicated review branch. It has not been merged into `main` and does not deploy the application.
