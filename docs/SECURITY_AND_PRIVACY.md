# Security and Privacy

## Local data

- Voice, inventory, sales, billing and printing remain local.
- No external API is required for normal use.
- Do not upload audio, transcripts, inventory, invoices, or customer data.
- Audio is temporary and deleted after processing by default.
- Diagnostic retention must be explicit and consented.

## Network

- FastAPI binds to 127.0.0.1 only.
- No LAN exposure by default.
- Restrict CORS to packaged Electron and local development origins.

## Electron

- Context isolation on.
- Node integration off.
- Narrow validated preload IPC.
- Restrict navigation and new windows.
- Apply Content Security Policy.
- Never execute shell commands from user/voice text.

## Imports and persistence

- Validate spreadsheet type, size, worksheets, row count and cells.
- Never execute macros.
- Preview before commit.
- Transactions for billing and stock.
- Audit manual edits, import commits, voids/returns and reprints.
- Back up before migration/import and test restore.
- Store DB/backups with suitable Windows permissions.
- Keep business data, recordings, credentials and live DB out of GitHub.

Offline-first does not itself guarantee security: Windows patching, access control, disk health, backups and physical access still matter.
