# PLAN

## Current Objective

Consolidate `dotagent` onto the Python runtime as the single orchestration engine and reduce PowerShell to a compatibility wrapper.

## Completed

- Audited the existing repo layout, docs, and runtime scripts.
- Identified the gap between strong packaging and weak runtime intelligence.
- Confirmed the Python runtime has the right module boundaries for planner, executor, validator, memory, and orchestrator work.
- Updated the design documents to target an explicit `PLAN -> EXECUTE -> VALIDATE -> REPLAN` control loop.
- Fixed the Python runtime registry break and link-validation drift.

## In Progress

- Replacing the duplicated PowerShell orchestration path with a thin wrapper over `python -m dotagent_runtime.cli`.
- Updating the installer so consumer repos receive the Python runtime under `.agent/runtime/`.
- Aligning docs and templates to the Python-canonical architecture.

## Next

- Verify the PowerShell wrapper and installed runtime work end-to-end through smoke commands.
- Update core documentation to describe PowerShell as a compatibility layer rather than a second runtime.
- Decide whether to remove or archive the remaining legacy orchestration helper scripts after wrapper migration.
- Continue closing runtime gaps around semantic memory, distributed execution targets, and policy enforcement.

## Blockers

- Consumer-repo smoke validation still depends on verifying the installed `.agent/runtime/` layout after the installer changes.

## Verification

- tests run:
  - `git rev-parse --abbrev-ref HEAD`
  - `python -m unittest discover -s runtime/tests -v`
  - `$env:PYTHONPATH='runtime'; python -m unittest discover -s runtime/tests -v`
  - `powershell -ExecutionPolicy Bypass -File .\.agent\scripts\validate-links.ps1 -Path .`
  - `powershell -ExecutionPolicy Bypass -File .\.agent\scripts\health-check.ps1`
- manual checks:
  - inspected the PowerShell shim, Python runtime modules, installer, schemas, docs, templates, and validation scripts
- known gaps:
  - there are still legacy docs that describe `scripts/run-agent.ps1` as the orchestration engine instead of the Python CLI
  - compatibility flags accepted by the PowerShell wrapper are not yet meaningful runtime controls
