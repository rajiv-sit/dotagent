# Architecture

## System Overview

`dotagent` remains a file-backed local runtime. The canonical CLI is implemented in Python and persists state under `.dotagent-state/`. PowerShell wrappers preserve the Windows-first command surface but forward orchestration into the Python runtime.

The architecture is intentionally vendor-neutral. The local docs, rules, prompts, and state model are the stable interface; the execution shim can target Codex, Claude, Copilot, or another assistant CLI as long as it can consume prepared prompts and return outputs locally.

Core flow:

1. Parse CLI command.
2. Create a normalized job record.
3. Render prompt input when relevant.
4. Persist job state as `PENDING`.
5. Execute locally when requested.
6. Transition lifecycle state based on result.
7. Hash and index produced artifacts.
8. Expose status and result queries.

## Architecture Style

- Monolithic local CLI runtime
- File-backed workflow orchestration
- DAG-style dependency metadata without a daemon or external queue

This fits the current repo because the runtime already stores local job state and can orchestrate local tools without requiring a daemon or service runtime. A local DAG is enough for milestone-oriented workflows and keeps operational complexity low.

## Technology Selection

- Python:
  - explicit planner, executor, validator, memory, and orchestrator modules
  - easier unit testing than large shell scripts
  - portable while remaining local-first
- PowerShell:
  - native fit with the current Windows-first scripts
  - retained as a thin compatibility layer for installed repos
- JSON schemas:
  - formalize persisted records and output contracts
  - support future validation without requiring a service runtime

## Interfaces

- CLI interface:
  - `setup`
  - `task`
  - `review`
  - `run`
  - `status`
  - `result`
  - `cancel`
- Persisted contracts:
  - `.dotagent-state/jobs/<job-id>.json`
  - `.dotagent-state/plans/<plan-id>.json`
  - `.dotagent-state/events/events.jsonl`
  - `.dotagent-state/evidence/<job-id>.json`
  - `.dotagent-state/telemetry/<job-id>.json`

## Visualization And Debugging

- `status` serves as the real-time textual view of job and workflow state.
- Artifact index files serve as evidence bundles for traceability.
- SHA256 digests support reproducibility checks and external evidence capture.
- Workflow graph JSON is the debugging view for dependency chains.

