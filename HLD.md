# HLD

## Modules

- CLI command parser
  - parses command, options, and execution intent
- State store
  - persists jobs, plans, events, evidence, and memory files
- Planner
  - creates adaptive step DAGs, assigns roles and priority, and emits corrective updates for failed steps
- Executor
  - dispatches steps to registered tools, supports bounded parallelism, and returns structured execution records
- Validator
  - evaluates execution records against acceptance criteria and policy-based SLO checks
- Memory manager
  - records prior run summaries, semantic summaries, and retrieves relevant local context for new jobs
- Orchestrator
  - coordinates scheduling, execution, validation, replanning, and finalization

## System Decomposition

- Preparation flow:
  - `task`, `review`, and `run` create a job and a persisted plan
  - the plan carries step dependencies, retry limits, and acceptance criteria
- Execution flow:
  - orchestrator loads job and plan
  - memory is queried for relevant historical context
  - ready steps are executed in dependency order, optionally in bounded parallel batches
  - each step is validated immediately
  - failed steps may be replanned and retried within explicit bounds
- Finalization flow:
  - job status is derived from plan outcome
  - evidence bundle is written
  - a memory entry is appended for future retrieval

## Data Flow

1. User issues CLI command.
2. Planner creates a normalized plan.
3. State store persists job and plan.
4. Orchestrator retrieves relevant local memory.
5. Executor runs each ready step through the tool registry.
6. Validator checks step outputs against acceptance criteria.
7. Planner emits corrective updates when retryable failures occur.
8. State store writes final evidence and events.
9. Status/result reads surface persisted job and plan records.

## External Dependencies

- local filesystem under project root
- optional local assistant CLI or shell-accessible tools
- no database, vector service, queue, or remote scheduler

## Integration Points

- prompt templates and rules can still inform higher-level task generation
- schemas formalize persisted runtime artifacts
- downstream CI can inspect `.dotagent-state` outputs directly
