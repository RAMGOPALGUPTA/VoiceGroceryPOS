# Development Guidelines

## Before coding

Read README.md and the relevant design documents. The repository currently contains architecture/planning documents only.

## Code principles

- Keep API routers thin; business rules belong in services.
- Keep ASR engines behind a common adapter.
- Keep parser, matching, inventory, billing, and printing independent.
- Use type hints and Pydantic.
- Use Decimal/integer paise for money; never float.
- Use explicit unit conversions.
- Test business rules and failure paths.
- Never silently resolve ambiguous product.
- Never commit customer data, audio, model weights, credentials, or live databases.

## Branches

- main: reviewed stable work.
- docs/*: documentation.
- feat/*: feature work.
- fix/*: bug fixes.

## Commit examples

- docs: define offline POS architecture
- feat(inventory): add validated Excel import
- test(billing): cover stock rollback and idempotency

## Pull request checklist

- Scope explained.
- Tests added/updated.
- No secrets/customer data.
- Migration included for schema changes.
- Offline behavior considered.
- Error and rollback behavior documented.
- User-facing docs updated.
