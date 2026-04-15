# PLAN

## Current Objective

Upgrade `dotagent` from a framework shell into a materially agentic local orchestration runtime.

## Completed

- Audited the existing repo layout, docs, and runtime scripts.
- Identified the gap between strong packaging and weak runtime intelligence.
- Confirmed the Python runtime has the right module boundaries for planner, executor, validator, memory, and orchestrator work.
- Updated the design documents to target an explicit `PLAN -> EXECUTE -> VALIDATE -> REPLAN` control loop.

## In Progress

- Reworking the Python runtime around explicit planner, executor, validator, memory, and orchestrator boundaries.
- Adding persisted step state, bounded retries, and corrective replanning metadata.
- Expanding the runtime with adaptive planning, semantic memory, bounded parallel execution, external adapters, and richer policy checks.

## Next

- Persist richer plan state including attempts, acceptance criteria, and corrective metadata.
- Add step executor and validator behavior that can drive retries and replans.
- Improve local memory capture and retrieval for run history.
- Repair validation drift in repo checks after runtime changes land.
- Close the remaining runtime gaps around semantic memory, distributed execution targets, and policy enforcement.

## Blockers

- `health-check.ps1` currently fails because it uses `$error` as a foreach variable, which collides with PowerShell's read-only automatic variable.
- `validate-links.ps1` currently reports a broken relative link in `templates/runtime/hooks/README.md`.
- Python runtime tests require workspace-local temp directories in this environment.

## Verification

- tests run:
  - `git rev-parse --abbrev-ref HEAD`
  - `python -m unittest discover -s runtime/tests -v`
  - `$env:PYTHONPATH='runtime'; python -m unittest discover -s runtime/tests -v`
  - `powershell -ExecutionPolicy Bypass -File .\.agent\scripts\validate-links.ps1 -Path .`
  - `powershell -ExecutionPolicy Bypass -File .\.agent\scripts\health-check.ps1`
- manual checks:
  - inspected the PowerShell shim, Python runtime modules, schemas, docs, templates, and validation scripts
- known gaps:
  - the repo is still stronger on packaging than on autonomous execution intelligence
  - validation and health-check scripts lag behind the current repo state
