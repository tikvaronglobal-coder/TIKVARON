# CBOS QA Status — 17 November 2026

## Checks completed
- Extracted the inline JavaScript and ran `node --check`: no syntax error reported.
- Parsed the HTML with Python's standard-library HTML parser: one document root, one inline script, no duplicate element IDs.
- Verified the embedded Partnership & Ownership view contains ownership/IP safeguards, customer/data controls, partner evaluation criteria, agreement checklist, risk assessment, approval gates, founder authority rules and central partner register.
- Parsed the CSV: 20 organisation records (14 inquiry-sent, 4 proposed/not contacted, 2 on hold).
- Checked all 15 known Gmail thread IDs: each outbound target message had the SENT label and expected recipient. This verifies sending only, not receipt, acceptance or partnership formation.

## Browser test limitation
A Chromium/Playwright interaction test was attempted, but the execution environment returned `ERR_BLOCKED_BY_ADMINISTRATOR` for both local-file and localhost navigation. Therefore tab switching, form submission, filtering, CSV export, JSON backup/restore and persistence have **not** been verified in a live browser here.

## Known limitations
- The app has browser-local storage with a memory fallback when persistent storage is unavailable. Memory fallback is session-only; export backups before closing if the browser reports temporary memory.
- This is not a cloud-synced or multi-user database.
- The 1,171-system inventory is an expanded working inventory, not the earlier verified baseline of 72 systems across 44 categories.
- The partner register is a working prospect/outreach register. Inquiry-sent entries await responses; proposed prospects are not contacted; on-hold entries are not approved.
- No accessibility audit, security review or legal review is claimed complete.

**Release status:** Working snapshot committed to a dedicated GitHub branch for review. Not merged to main. Not deployed.
