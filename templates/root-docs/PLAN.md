# PLAN

## Current Objective

Upgrade `dotagent` from a prompt wrapper into a production-grade local orchestration runtime.

## Completed

- Audited the existing repo layout, docs, and runtime scripts.
- Identified missing production primitives: formal job schema, orchestration layer, lifecycle states, dependency chaining, and artifact indexing.
- Created `Requirement.md`, `Architecture.md`, `HLD.md`, `DD.md`, and `milestone.md` for the enhancement.

## In Progress

- Reworking `scripts/dotagent.ps1` around a normalized job model and a new `run` workflow command.

## Next

- Add formal job and workflow persistence contracts.
- Implement local DAG execution for `HLD -> DD -> Code -> Test -> Review`.
- Add evidence bundle hashing and artifact index files.
- Update README and graph/docs to reflect the new model.
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
  - orchestration and artifact indexing not implemented yet
  - health-check output is overly optimistic relative to actual repo state

