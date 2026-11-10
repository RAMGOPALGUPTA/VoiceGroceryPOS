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
