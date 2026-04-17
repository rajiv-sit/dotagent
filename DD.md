# DD

## Class Design

The Python runtime is class-oriented with explicit module boundaries.

- `Job`
  - fields: `id`, `type`, `status`, `created_at`, `updated_at`, `input`, `output`, `metadata`
- `Step`
  - fields: `id`, `name`, `kind`, `status`, `depends_on`, `tool`, `payload`, `max_attempts`, `attempts`, `acceptance`, `last_error`, `priority`, `agent_role`, `execution_target`, `parallel_group`
- `Plan`
  - fields: `id`, `goal`, `steps`, `created_at`, `updated_at`, `metadata`
- `ExecutionResult`
  - fields: `step_id`, `tool`, `ok`, `output`, `started_at`, `ended_at`, `attempt`, `metadata`
- `ValidationResult`
  - fields: `status`, `summary`, `checks`, `corrective_actions`, `retryable`
- `StepExecutor`
  - responsibility: tool dispatch and per-step attempt execution
- `Planner`
  - responsibility: deterministic plan creation and corrective step mutation on failure
- `Validator`
  - responsibility: acceptance checks and retryability judgment
- `MemoryManager`
  - responsibility: append/search lightweight local memory with semantic-style scoring
- `Orchestrator`
  - responsibility: scheduling loop, job transitions, evidence generation, and finalization
- `PolicyEngine`
  - responsibility: enforce richer SLO and policy checks across validator steps
- PowerShell wrapper script
  - responsibility: resolve the installed runtime package location, preserve legacy flags, and invoke `python -m dotagent_runtime.cli`

## Algorithms

### Orchestration loop

1. Load job and plan.
2. Set job status to `RUNNING`.
3. Query memory for relevant prior context.
4. Find ready steps whose dependencies are all `SUCCESS`.
5. Execute one ready step or a bounded parallel batch of ready steps.
6. Validate the result.
7. If validation passes, mark the step `SUCCESS`.
8. If validation fails and retry is allowed, ask the planner for a corrective update, persist the plan, and retry.
9. If validation fails without recovery, mark the step `FAILED` and end the job as `FAILED`.
10. When all required steps succeed, mark the job `SUCCESS`.
11. Persist evidence and write a memory summary.

### Cancellation

1. Load the target job.
2. If the job is already terminal, return current state.
3. Mark the job `CANCELLED`.
4. Load the linked plan from job metadata.
5. Mark any `PENDING` or `RUNNING` steps as `CANCELLED`.
6. Persist cancellation metadata on the plan and emit a cancellation event.

### Step replanning

1. Inspect the failed step and validation result.
2. If the step contains fallback commands, promote the next fallback command to primary command.
3. Record replan metadata and corrective notes in the step payload.
4. Increment plan-level replan count.
5. Return the updated step for another bounded attempt.

### Validation

1. Check base execution success.
2. Evaluate acceptance criteria such as required return code, expected text in stdout, forbidden text in stderr, and metric thresholds.
3. Emit corrective actions for unmet checks.
4. Mark retryable only when the step still has attempts remaining and the failure mode is recoverable.

## Data Structures

- dataclass-backed runtime records for job, plan, step, execution result, and validation result
- JSON files for persisted state, evidence, and memory
- adjacency-by-dependency lists for plan DAG evaluation
- installer-copied Python package under `.agent/runtime/dotagent_runtime` in consumer repos

## Complexity

- Job and plan read/write: `O(1)` per record
- Ready-step scan: `O(v + e)` per pass for plan vertices `v` and dependencies `e`
- Validation: `O(c)` for `c` acceptance checks on a step
- Memory search: `O(m)` for `m` stored entries in the queried namespace
- Parallel execution batch: bounded by `p` workers where `p = max_parallelism`

## Error Handling

- Fail fast on missing job or plan identifiers
- Treat missing optional memory or evidence files as non-fatal
- Persist step-level failure summaries and corrective actions
- Stop orchestration when a dependency chain can no longer reach success
- Keep retries bounded by `max_attempts`
- Treat compatibility-only PowerShell flags such as `-Model` and `-Sandbox` as accepted but non-authoritative when they no longer affect Python runtime behavior
