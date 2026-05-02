# PowerShell Integration Reference

PowerShell is now a compatibility layer, not the orchestration engine.

Current behavior:

- `scripts/install-dotagent.ps1` delegates to `scripts/install-pack.ps1`.
- `scripts/dotagent.ps1` delegates to `scripts/run-agent.ps1`.
- `scripts/run-agent.ps1` resolves `.agent/runtime` or source `runtime`, sets `PYTHONPATH`, suppresses bytecode cache writes, and invokes `python -m dotagent_runtime.cli`.

Use these references for current behavior:

- [Scripts README](../scripts/README.md)
- [Runtime Architecture](design/Architecture.md)
- [`runtime/dotagent_runtime/cli.py`](../runtime/dotagent_runtime/cli.py)
- [`runtime/dotagent_runtime/orchestrator.py`](../runtime/dotagent_runtime/orchestrator.py)
