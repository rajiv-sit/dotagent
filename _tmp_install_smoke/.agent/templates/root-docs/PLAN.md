# PLAN

## Current Objective

Upgrade `dotagent` into a Python-led local orchestration runtime with PowerShell wrappers kept only for compatibility.

## Completed

- Audited the existing repo layout, docs, and runtime scripts.
- Identified missing production primitives: formal job schema, orchestration layer, lifecycle states, dependency chaining, and artifact indexing.
- Created `Requirement.md`, `Architecture.md`, `HLD.md`, `DD.md`, and `milestone.md` for the enhancement.

## In Progress

- Reworking the Python runtime around a normalized job and plan model.
- Reducing `scripts/dotagent.ps1` and `run-agent.ps1` to thin wrappers over the Python CLI.

## Next

- Add formal job and plan persistence contracts.
- Implement local DAG execution for adaptive task and review plans.
- Add evidence bundle hashing and telemetry files.
- Update README and graph/docs to reflect the Python-canonical model.
- Re-run validation scripts and runtime smoke tests.

## Blockers

- `validate-links.ps1` currently fails on stale links in `GRAPH.md` and on at least one zero-byte markdown file.

## Verification

- tests run:
  - `git rev-parse --abbrev-ref HEAD`
  - `powershell -ExecutionPolicy Bypass -File .\.agent\scripts\validate-links.ps1 -Path .`
  - `powershell -ExecutionPolicy Bypass -File .\.agent\scripts\health-check.ps1`
- manual checks:
  - inspected runtime, hooks, prompts, schemas, docs, and graph references
- known gaps:
  - wrapper/docs drift can reappear if PowerShell logic grows again
  - health-check output can still be more optimistic than deeper runtime validation

