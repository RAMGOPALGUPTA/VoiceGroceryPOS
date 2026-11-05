# Architecture Decision Records

## ADR-001 — Offline-first single machine
**Decision:** Local Windows PC, SQLite, local ASR.  
**Reason:** Billing must continue without internet; single counter does not need distributed infrastructure.

## ADR-002 — Electron + React + FastAPI
**Decision:** Electron hosts React and supervises Python backend.  
**Reason:** Familiar UI stack, Windows packaging and Python speech/Excel ecosystem.

## ADR-003 — SQLite for pilot
**Decision:** SQLite is initial source of truth.  
**Reason:** Single-machine, low-admin deployment. Revisit PostgreSQL only when centralized multi-machine use is required.

## ADR-004 — ASR stays replaceable
**Decision:** Adapter interface and benchmark candidates on target PC.  
**Reason:** Code-mixed accuracy, latency, RAM, licensing and package size require evidence.

## ADR-005 — Deterministic billing
**Decision:** Backend database prices/stock and Decimal calculations are authoritative.  
**Reason:** Speech/LLM must never invent prices or invoice totals.

## ADR-006 — Operator confirmation
**Decision:** Review ambiguous products and confirm every checkout.  
**Reason:** Recognition errors must not silently become sales.

## ADR-007 — Print after sale commit
**Decision:** Commit sale first, then queue/retry printing.  
**Reason:** Printer failures must not undo a valid sale or cause duplicate deductions.
