# API Specification

Initial contract; implementation starts in M1/M2. Base path: /api/v1. Bind only to 127.0.0.1.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /health | Backend/database/model readiness |
| POST | /api/v1/voice/transcribe | Audio to transcript |
| POST | /api/v1/voice/parse | Transcript to structured intents |
| POST | /api/v1/voice/process | Full voice pipeline |
| GET/POST | /api/v1/products | List/create products |
| GET/PATCH | /api/v1/products/{id} | Read/update product |
| GET | /api/v1/products/search | Product search |
| POST | /api/v1/products/{id}/aliases | Add spoken alias |
| GET | /api/v1/inventory | Inventory listing |
| POST | /api/v1/inventory/import/preview | Validate and preview workbook |
| POST | /api/v1/inventory/import/commit | Commit reviewed import |
| POST | /api/v1/inventory/adjustments | Manual adjustment |
| POST | /api/v1/cart/resolve | Resolve parsed items |
| POST | /api/v1/sales/preview | Calculate proposed bill |
| POST | /api/v1/sales/confirm | Atomic sale commit |
| GET | /api/v1/sales | Sales history |
| GET | /api/v1/sales/{id} | Invoice detail |
| POST | /api/v1/printing/jobs | Queue/retry committed receipt |
| GET | /api/v1/printing/jobs/{id} | Print status |
| GET | /api/v1/reports/daily | Daily report |
| GET/PATCH | /api/v1/settings | Local settings |

## Contracts

- Prices always come from DB, never from transcript or client request.
- Preview does not reserve/deduct stock.
- Confirmation reloads price and stock and recalculates server-side.
- Sale confirmation requires an idempotency key.
- Sale, lines, payment, stock movement and stock balance update are atomic.
- Printing is post-commit and retryable.

## Example voice response

```json
{
  "transcript": "do kilo chini aur ek litre doodh",
  "detected_language": "mixed",
  "items": [
    {
      "product_query": "chini",
      "quantity": "2",
      "unit": "kg",
      "candidates": [
        {
          "product_id": 102,
          "display_name": "Sugar",
          "match_method": "alias",
          "match_score": 1.0
        }
      ],
      "resolution": "needs_operator_review"
    }
  ],
  "requires_confirmation": true
}
```

Match score is not ASR confidence and must be calibrated.

## Error codes

PRODUCT_NOT_FOUND, PRODUCT_AMBIGUOUS, PRODUCT_INACTIVE, UNIT_INCOMPATIBLE, INSUFFICIENT_STOCK, INVALID_QUANTITY, IMPORT_VALIDATION_FAILED, IDEMPOTENCY_CONFLICT, PRINTER_UNAVAILABLE, ASR_NOT_READY, AUDIO_INVALID.


## Implemented catalogue and inventory endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/products?q=&include_inactive=false` | Search/list products by name, SKU, brand, or barcode |
| POST | `/api/v1/products` | Create product and record opening stock movement |
| GET | `/api/v1/products/{id}` | Read product |
| PATCH | `/api/v1/products/{id}` | Update product fields |
| DELETE | `/api/v1/products/{id}` | Soft-deactivate product |
| GET/POST | `/api/v1/categories` | List/create categories |
| GET/POST | `/api/v1/products/{id}/aliases` | List/add spoken aliases |
| POST | `/api/v1/inventory/products/{id}/adjustments` | Apply signed stock adjustment with ledger record |
| GET | `/api/v1/inventory/movements` | List stock movement history |

Stock adjustments reject a resulting negative balance. Product creation records non-zero opening stock in the stock movement ledger. Product deletion is a soft deactivation; historical records are not removed.


## Inventory spreadsheet import

- `POST /api/v1/inventory/import/preview` — multipart upload of CSV, XLSX, or XLSM (10 MB maximum). Required columns: SKU, product name, selling price. Optional columns include stock quantity, brand, barcode, cost price, stock/sale units, tax rate, and reorder level. Header aliases are accepted.
- Preview persists normalized rows locally and returns row-level validation errors plus create/update classification. Preview does not modify products or stock.
- `POST /api/v1/inventory/import/{import_id}/commit?stock_mode=replace|add` — commits only a preview with zero row errors. The operation is transactional. `replace` sets the supplied stock quantity; `add` adds it to current stock. Omitted stock quantities leave stock unchanged.
- Each non-zero stock change writes a stock-ledger movement. Rows missing from the spreadsheet are never deleted or deactivated. An import preview can be committed once.


## Sales and payments

- `POST /api/v1/sales/checkout` — accepts an idempotency key, payment method, optional discount and product/quantity lines. The server reloads current product prices and stock, calculates tax, creates the sale and payment records, deducts stock, and writes stock movements in one database transaction. Repeating the same idempotency key returns the existing sale instead of charging/deducting twice.
- `GET /api/v1/sales` — recent completed/refunded sale records.
- `GET /api/v1/sales/{sale_id}` — receipt snapshot and line details.
- `POST /api/v1/sales/{sale_id}/refund` — full-sale refund record only. Restores stock and marks the sale refunded in one transaction. This endpoint records the refund; it does not send money through a bank, UPI provider or card terminal. The cashier must return funds through the original payment channel manually.
- `GET /api/v1/inventory/summary` — active catalogue and low-stock summary.
- `GET /api/v1/reports/summary` — daily/all-time sales totals and stock indicators.
- `POST /api/v1/voice/transcribe` — optional local ASR. Requires the separately installed faster-whisper package and model.
- `POST /api/v1/voice/interpret` — matches a transcript against names, SKUs, brands and aliases. Suggestions always require cashier confirmation.
