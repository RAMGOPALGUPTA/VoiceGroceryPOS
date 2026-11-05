# Database Schema

Logical contract; SQLAlchemy models and Alembic migrations are implemented in M1.

## Tables

| Table | Important fields | Purpose |
|---|---|---|
| categories | id PK, name, parent_id FK | Categories |
| products | id, sku unique, name, brand, category_id, selling_price, cost_price, stock_quantity, stock_unit, sale_unit, conversion_factor, barcode, tax_rate, reorder_level, is_active | Catalog and current balance |
| product_aliases | id, product_id FK, alias, normalized_alias, language | Multilingual spoken names |
| sales | id, invoice_number unique, idempotency_key unique, status, totals, timestamps | Committed/voided sales |
| sale_items | id, sale_id FK, product_id FK, name/sku/unit/price/tax snapshots, quantity, line_total | Immutable invoice lines |
| payments | id, sale_id FK, method, amount, reference, status | Payment record |
| stock_movements | id, product_id FK, quantity_delta, stock_unit, movement_type, reference, note, timestamp | Auditable stock ledger |
| price_history | id, product_id FK, old_price, new_price, source, timestamp | Price audit |
| inventory_imports | id, filename, file_hash, worksheet, stock_mode, status, counts | Batch summary |
| inventory_import_rows | id, import_id FK, row_number, sku, status, message | Row-level import results |
| print_jobs | id, sale_id FK, printer_name, status, attempts, last_error | Print/retry history |
| audit_logs | id, actor, action, entity_type, entity_id, details, timestamp | Audit trail |
| app_settings | key PK, value, updated_at | Store/printer/receipt settings |

## Invariants

1. Python calculations use Decimal; persisted currency totals should use integer paise where practical.
2. Quantity uses decimal-compatible precision, never float.
3. Unit conversions must be explicit and configured per product.
4. Every stock balance change has a stock movement in the same transaction.
5. Invoice snapshots never change after product edits.
6. Imports never delete products just because a row is absent.
7. Import must specify replace-count or add-stock mode.
8. Sale confirmation is idempotent.
9. Print retry never modifies sale or stock.
10. Foreign keys enabled and transaction boundaries explicit.

## Unit model

Every product has a canonical stock unit and a sale unit. A 5 kg bag can be configured as a bag with conversion factor 5 kg. Loose 500 g sale is allowed only if that product supports fractional weight sale. Packet is not converted to grams unless pack size is configured.

## SQLite

Enable foreign keys on each connection, busy timeout, evaluate WAL for local use, keep transactions short, and use a consistent backup method. Do not keep live DB in a synced cloud directory.
