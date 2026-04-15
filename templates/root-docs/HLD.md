# HLD

## Modules

- CLI command parser
  - parses command, options, and execution intent
- Job store
  - creates, reads, updates, and lists persisted job records
- Prompt renderer
  - resolves prompt templates and fills tokens
- Executor
  - invokes a local assistant CLI such as `agent.cmd exec`, captures stdout/stderr, and stores outputs
- Artifact indexer
  - computes file metadata and SHA256 digests for evidence bundles
- Workflow orchestrator
  - creates workflow DAG metadata and executes ready nodes in dependency order

## System Decomposition

- Single-job flow:
  - `task` and `review` create one job each and optionally execute it
- Multi-job flow:
  - `run` creates a fixed workflow chain of stage jobs
  - dependencies are encoded in job metadata and workflow graph JSON
  - scheduler logic selects the next ready node locally

## Data Flow

1. User issues CLI command.
2. Runtime creates normalized job record(s).
3. Prompt(s) are written to disk.
4. Execution updates status to `RUNNING`.
5. Outputs are captured and persisted.
6. Artifact indexer hashes evidence files.
7. Status/result reads combine job state with workflow metadata.

## External Dependencies

- local assistant CLI shim on PATH, for example `agent.cmd` or `agent`
- local filesystem under project root
- no database, no queue, no remote scheduler

## Integration Points

- prompt templates in `prompts/`
- output schemas in `schemas/`
- project docs that inform generated prompts
- downstream CI can read job and workflow JSON directly

