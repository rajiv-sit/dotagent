# HLD

## Modules

- CLI command parser
  - Python CLI parses command, options, and execution intent
- PowerShell compatibility wrapper
  - forwards the Windows command surface into the Python CLI
- State store
  - creates, reads, updates, and lists persisted job and plan records
- Executor
  - invokes local tools, captures stdout/stderr, and stores outputs
- Validator
  - evaluates step results against explicit acceptance criteria and policies
- Workflow orchestrator
  - creates persisted plans and executes ready steps in dependency order

## System Decomposition

- Single-job flow:
  - `task` and `review` create one job and one plan each and optionally execute them
- Multi-step flow:
  - `run` uses the same plan-based runtime path as `task`
  - dependencies are encoded in persisted plan records
  - scheduler logic selects the next ready step locally
- Cancellation flow:
  - `cancel` marks non-terminal jobs and linked plan steps consistently

## Data Flow

1. User issues CLI command.
2. PowerShell wrapper forwards to the Python CLI when applicable.
3. Runtime creates normalized job and plan record(s).
4. Execution updates status to `RUNNING`.
5. Outputs are captured, validated, and persisted.
6. Evidence and telemetry files are written.
7. Status/result reads combine job state with plan metadata.

## External Dependencies

- Python interpreter on PATH
- optional local assistant CLI shim on PATH for future adapter-driven execution
- local filesystem under project root
- no database, no queue, no remote scheduler

## Integration Points

- prompt templates in `prompts/`
- output schemas in `schemas/`
- project docs that inform generated prompts
- downstream CI can read job and workflow JSON directly

