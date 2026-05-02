# Contributing

Use the project-local workflow before changing behavior.

1. Read [AGENTS.md](../../AGENTS.md), [CONTEXT.md](CONTEXT.md), and [PLAN.md](PLAN.md).
2. Read the design docs under [docs/design](../design/README.md).
3. Make changes one milestone at a time.
4. Keep PowerShell as a compatibility layer and Python as the canonical runtime.
5. Run validation before handing off:

```powershell
$env:PYTHONPATH='runtime'; python -m unittest discover -s runtime/tests -v
powershell -ExecutionPolicy Bypass -File .\.agent\scripts\validate-links.ps1 -Path .
powershell -ExecutionPolicy Bypass -File .\.agent\scripts\health-check.ps1
```

For installer changes, also run an installed-consumer smoke check with `scripts/install-pack.ps1`.
