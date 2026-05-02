# Integration Complete

This is a historical report from the earlier orchestration phase.

Current status:

- `scripts/run-agent.ps1` is a compatibility wrapper.
- `scripts/dotagent.ps1` delegates to `run-agent.ps1`.
- The canonical runtime entrypoint is `python -m dotagent_runtime.cli`.
- Current orchestration lives in `runtime/dotagent_runtime/orchestrator.py`.

Use these current references instead:

- [PLAN.md](../PLAN.md)
- [CONTEXT.md](../CONTEXT.md)
- [Architecture](design/Architecture.md)
- [HLD](design/HLD.md)
- [DD](design/DD.md)
- [Milestones](design/milestone.md)
