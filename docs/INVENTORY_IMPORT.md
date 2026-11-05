# Inventory Import

## Inputs

XLSX primary; CSV secondary. Treat workbook content as untrusted. Never execute macros.

## Logical columns

| Column | Required | Notes |
|---|---|---|
| SKU / Product ID | Preferred unique key | Required for safe repeat updates |
| Product Name | Yes | Display label |
| Brand | No | Helps distinguish variants |
| Category | No | Category assignment |
| Selling Price | Yes | INR, non-negative |
| Stock Quantity | Yes for initial import | Non-negative |
| Stock Unit | Yes | kg, g, litre, ml, piece, packet |
| Sale Unit | Yes | Unit sold at counter |
| Conversion Factor | When units differ | Explicit conversion |
| Cost Price | No | Future margin reports |
| Tax Rate | No | Only after owner verifies setup |
| Barcode | No | Future feature |
| Aliases | No | Can be added in dashboard |

## Wizard

1. Upload and choose worksheet.
2. Map columns.
3. Preview parsed values.
4. Validate required fields, price, stock, units and conversions.
5. Detect duplicate/blank SKUs and alias collisions.
6. Match existing records by SKU; never auto-update by fuzzy name.
7. Show insert/update/unchanged/conflict/error summary.
8. Select stock mode.
9. Confirm and commit atomically.
10. Save import batch and row outcomes.

## Stock modes

- Replace count: spreadsheet quantity becomes counted stock; log delta from old balance.
- Add stock: spreadsheet quantity is incoming stock; log positive movement.
- Operator must explicitly choose a mode.
- Missing rows never delete catalog products.
- Price changes create price history.
- Stock changes create stock movements.
- Duplicate SKU blocks commit until resolved.
- Product with history is deactivated, not hard-deleted.
- Backup before bulk import; rollback entire commit on failure.
