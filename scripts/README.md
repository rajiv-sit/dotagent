# Scripts

This folder contains the install and runtime scripts for `dotagent`.

## Included

- `install-pack.ps1`
  - installs the source pack into a real project root from `templates/`
  - writes `AGENTS.md`, `CONTEXT.md`, `PLAN.md`, and the project-local `.agent/` contents
- `install-dotagent.ps1`
  - compatibility wrapper for `install-pack.ps1`
- `init-project-docs.ps1`
  - creates the required design documents under `docs/design/` for a new project from `templates/root-docs/`
- `run-agent.ps1`
  - thin PowerShell wrapper over the Python runtime for setup, preparation, execution, and status queries
- `dotagent.ps1`
  - compatibility wrapper for `run-agent.ps1`
- `adapters/`
  - assistant CLI resolution helpers

## Typical Usage

From a real project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\dotagent\scripts\install-pack.ps1 -ProjectRoot .
powershell -ExecutionPolicy Bypass -File .\.agent\scripts\init-project-docs.ps1 -ProjectRoot .
powershell -ExecutionPolicy Bypass -File .\.agent\scripts\run-agent.ps1 setup
```

`run-agent.ps1` forwards to `python -m dotagent_runtime.cli`. The Python runtime:

- stores local job records under `.dotagent-state/`
- stores plan records under `.dotagent-state/plans/`
- lets a team track `task`, `review`, `run`, `status`, `result`, and `cancel`
- can execute steps through its tool registry and local shell adapters

Lifecycle states:

- `PENDING`
- `RUNNING`
- `SUCCESS`
- `FAILED`
- `REVIEWED`
- `CANCELLED`

The installed Python package is copied into `.agent/runtime/dotagent_runtime/` by `install-pack.ps1`, which keeps consumer repos self-contained.


