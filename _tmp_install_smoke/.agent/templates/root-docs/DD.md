# DD

## Class Design

The canonical runtime is Python class-oriented. PowerShell remains a compatibility wrapper and should not own orchestration behavior.

- Job
  - fields: `id`, `type`, `status`, `created_at`, `input`, `output`, `metadata`
- Step
  - fields: `id`, `name`, `kind`, `status`, `depends_on`, `tool`, `payload`, `max_attempts`, `attempts`, `acceptance`
- Plan
  - fields: `id`, `goal`, `steps`, `created_at`, `updated_at`, `metadata`
- ExecutionResult
  - fields: `step_id`, `tool`, `ok`, `output`, `started_at`, `ended_at`, `attempt`, `metadata`
- ValidationResult
  - fields: `status`, `summary`, `checks`, `corrective_actions`, `retryable`

## Algorithms

### Orchestration loop

1. Build normalized job object with `PENDING` status.
2. Build and persist a plan with step dependencies.
3. On execution start, transition the job to `RUNNING`.
4. Execute ready steps in dependency order.
5. Validate each step result immediately.
6. Retry or replan within explicit bounds.
7. Persist evidence, telemetry, and memory summaries on terminal transition.

### Cancellation

1. Load the target job and linked plan.
2. If the job is non-terminal, mark it `CANCELLED`.
3. Mark `PENDING` and `RUNNING` plan steps as `CANCELLED`.
4. Persist cancellation metadata and emit an event.

## Data Structures

- Dataclass-backed Python objects for job, plan, step, execution result, and validation result
- File-per-record JSON storage for simple inspectability and low operational overhead

## Complexity

- Job read/write: `O(1)` per record
- Status listing: `O(n)` for `n` jobs
- Plan readiness scan: `O(v + e)` per scheduler pass for vertices/steps `v` and edges `e`
- Validation: `O(c)` for `c` checks on a step

## Error Handling

- Throw immediately on invalid command input or missing required arguments
- Persist stderr and validation details for failed executions
- Record blocked dependency context in job metadata when orchestration cannot proceed
- Treat missing optional evidence or telemetry files as non-fatal
- Keep state transitions explicit and persisted even on failure

