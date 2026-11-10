# Development Roadmap

The implementation order protects billing correctness before AI integration.

| Milestone | Scope | Exit criteria |
|---|---|---|
| M0 — Blueprint | Requirements, architecture, schemas, API, security, tests | Documentation reviewed |
| M1 — Foundation | FastAPI, SQLite, SQLAlchemy, Alembic, 10–15 sample products | CRUD, constraints, migrations pass |
| M2 — Inventory | Excel/CSV preview, validation, SKU mapping, stock modes, dashboard | Duplicate and rollback tests pass |
| M3 — Manual POS | Product search, cart, unit conversion, preview, confirm, stock ledger, invoices | Decimal and transaction tests pass |
| M4 — ASR benchmark | Candidate offline ASR behind adapter | Candidate selected using target PC metrics |
| M5 — NLP/matching | Mixed-language normalization, numbers, units, aliases, ambiguity | Evaluation corpus and safe review pass |
| M6 — Voice workflow | Push-to-talk, transcript review, cart corrections | Ambiguous items cannot bypass review |
| M7 — Printing | Spooler/verified ESC-POS, queue, retry, receipt | Print/reprint tests pass |
| M8 — Packaging | Electron, backend lifecycle, PyInstaller, installer | Clean offline Windows install passes |
| M9 — Store pilot | Backup, owner inventory import, operator training | Owner signs off |

## Pilot

One Windows PC, one counter, 10–15 illustrative products. Operator reviews proposed items and final total. No real inventory until test backup/import is verified.

## Later scope

Barcode scanner, purchase receiving, supplier/customer ledger, verified GST configuration, native Gurmukhi/Devanagari receipt rendering, multiple counters/stores, synchronization, analytics and reorder suggestions.


## Implementation update — 2026-11-10

- Initial Electron + React POS workspace committed.
- Product catalogue create/read/update/deactivate and search endpoints committed.
- Category creation/listing and product aliases committed.
- Stock adjustments write a stock movement and reject negative resulting stock.
- Backend and frontend have not yet been run on the target Windows machine; do not treat these features as hardware-verified.
