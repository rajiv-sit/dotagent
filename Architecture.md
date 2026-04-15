# Architecture

## System Overview

`dotagent` remains a file-backed local runtime. The CLI prepares or executes prompt-driven jobs, persists state under `.dotagent-state/`, and now adds a lightweight orchestration layer for multi-step development workflows.

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

This fits the current repo because the runtime already stores local job state and shells out to `agent.cmd`. A local DAG is enough for milestone-oriented Agent workflows and keeps operational complexity low.

## Technology Selection

- PowerShell:
  - native fit with the current Windows-first scripts
  - easy file/process orchestration
  - consistent with existing installer and hook stack
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
  - `jobs/<job-id>.json`
  - `jobs/<job-id>.prompt.md`
  - `jobs/<job-id>.output.md`
  - `jobs/<job-id>.stderr.log`
  - `jobs/<job-id>.events.jsonl`
  - `jobs/<job-id>.artifacts.json`
  - `graphs/<workflow-id>.json`

## Visualization And Debugging

- `status` serves as the real-time textual view of job and workflow state.
- Artifact index files serve as evidence bundles for traceability.
- SHA256 digests support reproducibility checks and external evidence capture.
- Workflow graph JSON is the debugging view for dependency chains.

