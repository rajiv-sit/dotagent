# Error Handling

- Fail loudly on invalid state at boundaries.
- Return actionable error messages with enough context for debugging.
- Avoid swallowing exceptions without logging or translation.
- Define recovery behavior for transient failures.
- Keep error-handling paths covered by tests where practical.
