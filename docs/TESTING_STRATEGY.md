# Testing Strategy

## Unit tests

- Decimal calculations and rounding.
- Number/fraction parsing.
- Unit conversion and incompatible unit rejection.
- Text normalization.
- Alias collisions.
- Fuzzy matching thresholds.
- Invoice numbers and idempotency.
- Import validators and stock modes.

## Integration tests

- SQLite migrations and foreign keys.
- Product CRUD and alias search.
- Import preview/commit/rollback.
- Sale transaction and insufficient-stock rollback.
- Duplicate confirmation request.
- Invoice snapshot after price/name edits.
- Print failure/retry without stock changes.

## System tests

- Offline startup and restart.
- Microphone permission/device changes.
- ASR latency/RAM/CPU on target PC.
- Shop noise and multiple speakers.
- TVS RP3160 GOLD(U) driver and receipt formatting.
- Clean Windows installer, upgrade, backup/restore, uninstall.

## Critical scenarios

1. Single, multiple, and repeated products.
2. kg/g and litre/ml conversions.
3. Fractions and quantities as spoken words.
4. Similar product names, brands and pack sizes.
5. Unknown product or missing quantity.
6. Insufficient stock.
7. Price change after preview, before confirm.
8. Duplicate confirmation.
9. Database failure during stock update.
10. Printer disconnect after committed sale.
11. Reprint existing invoice.
12. Duplicate SKU import.
13. Replace stock vs add stock.
14. Offline mode.

## Pilot metrics

Targets to validate, not current claims:
- DB price retrieval: 100%.
- Arithmetic: 100% on reference cases.
- Stock consistency: 100%.
- Quantity extraction target >=99%.
- Product identification target >=98%.
- No silent selection for ambiguous products.

Report ASR WER separately from product identification and quantity extraction, with sample size and language/speaker/noise breakdown.
