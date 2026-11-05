# Receipt Printing

## Initial approach

Use Windows printer spooler with installed driver first. Add direct ESC/POS only after verifying exact printer model and connection.

Initial target: TVS RP 3160 GOLD(U), pending driver and command validation on deployment PC.

## Receipt fields

Store details, invoice number/time, item names, quantities/units, unit price, line totals, discount, configured tax, grand total, payment method, footer.

## Print lifecycle

- Receipt builder renders committed invoice snapshot.
- Print queue tracks pending, printing, printed, failed, attempts and error.
- Reprint references the same sale; it never creates another invoice or stock movement.
- A print failure does not cancel the sale.

## Validation

Paper width (printer-dependent), margins, wrapping, column alignment, paper feed, cutter, disconnected printer, driver errors, retry, reprint, and Unicode.

Some low-cost thermal devices may not render Gurmukhi/Devanagari correctly. Start with English/transliterated receipt labels if needed; verify native scripts before promising them.
