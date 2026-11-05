# Architecture

## Deployment boundary

Single Windows PC, one store, one billing counter. Electron hosts React and supervises a local FastAPI backend. SQLite is the local source of truth for products, aliases, stock, sales, and operations.

## Component responsibilities

| Component | Responsibility | Must not |
|---|---|---|
| Electron main | Window/backend lifecycle, restricted IPC | Calculate bill |
| React renderer | Capture interactions and display state | Trust client prices or write DB |
| FastAPI routes | Validate DTOs and call services | Hold business logic |
| Speech adapter | Local audio preprocessing and ASR | Change stock |
| NLP parser | Extract phrases, quantity, units, command | Invent catalog items |
| Product matcher | Resolve aliases to catalog candidates | Silently choose ambiguous SKU |
| Billing service | Reprice, validate, calculate | Trust client totals |
| Inventory service | Import, adjustments, movements | Change stock without ledger |
| Print service | Build receipt and queue jobs | Create sale or deduct stock |
| SQLite | Persistent source of truth | Be accessed from renderer |

## Runtime

1. Electron starts the packaged backend as a child process.
2. Backend loads configuration, opens SQLite, applies approved migrations, and exposes health on loopback.
3. Electron waits for backend readiness.
4. React calls the local API.
5. ASR is loaded lazily or at startup depending on measured RAM/startup behavior.
6. Shutdown is graceful and closes DB connections.

## Voice pipeline

Push-to-talk -> local audio capture -> validation/resampling -> offline ASR -> transcript metadata -> normalization -> number/fraction parser -> unit parser -> product phrase extraction -> alias/exact/fuzzy catalog matching -> operator review -> proposed cart.

ASR quality, parser validity, and product-match score are separate measurements. High transcript confidence does not guarantee a unique product match.

## Matching policy

- Exact alias may preselect a candidate but remains visible.
- Multiple catalog candidates require operator choice.
- Fuzzy candidate thresholds are calibrated on a test set.
- Unknown item remains unresolved and can be searched manually.
- Brand and pack size distinguish SKUs.
- Inactive or out-of-stock items cannot silently reach checkout.

## Billing transaction

At confirmation, re-read prices and stock inside a DB transaction. Calculate totals and write sale, invoice line snapshots, payment, stock movements, and stock balance atomically. Use idempotency key to prevent duplicate sale.

Printing is post-commit. Printer error changes print job status only.

## Offline and customer-data boundary

All normal workflows are local. Bind API to 127.0.0.1. Customer mutable data is outside install directory, for example under %ProgramData%\VoiceGroceryPOS. Sample data is development-only.
