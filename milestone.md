# milestone

## Milestone 1

### Objective

Define and land formal runtime contracts for jobs, workflows, lifecycle states, and artifact evidence.

### Files To Modify

- `Requirement.md`
- `Architecture.md`
- `HLD.md`
- `DD.md`
- `schemas/job.schema.json`
- `scripts/dotagent.ps1`

### Verification Steps

- Prepare and inspect a `task` job
- Prepare and inspect a `review` job
- Run `status` and `result` against created jobs

### Exit Criteria

- Persisted jobs use the normalized schema
- Lifecycle states are explicit and terminal states are consistent
- Artifact bundles are generated for persisted jobs

## Milestone 2

### Objective

Add orchestrated workflow execution and update docs to reflect the production-grade model.

### Files To Modify

- `scripts/dotagent.ps1`
- `schemas/job.schema.json`
- `README.md`
- `GRAPH.md`
- `prompts/task.md`
- `prompts/review.md`

### Verification Steps

- Create an orchestrated `run`
- Execute a dry local workflow preparation
- Execute a workflow if a local assistant CLI such as `agent.cmd` is available
- Confirm dependency graph and artifact index files are written

### Exit Criteria

- `run` creates a dependency chain with visible state
- docs reflect the new commands and data model
- graph/doc links are internally consistent

## Milestone 3

### Objective

Add the missing agentic runtime loop in the Python runtime with explicit planner, executor, validator, memory, and orchestrator responsibilities.

### Files To Modify

- `Requirement.md`
- `Architecture.md`
- `HLD.md`
- `DD.md`
- `PLAN.md`
- `runtime/dotagent_runtime/models.py`
- `runtime/dotagent_runtime/planner.py`
- `runtime/dotagent_runtime/state_store.py`
- `runtime/dotagent_runtime/validator.py`
- `runtime/dotagent_runtime/memory.py`
- `runtime/dotagent_runtime/tools.py`
- `runtime/dotagent_runtime/orchestrator.py`
- `runtime/tests/test_orchestrator.py`
- `runtime/tests/test_state_store.py`

### Verification Steps

- Prepare and execute a task plan through the Python runtime
- Confirm step-level statuses, attempts, and replan metadata are persisted
- Confirm evidence bundles include plan, validation, and reproducibility hash
- Confirm memory entries are written after execution
- Run runtime unit tests inside the workspace

### Exit Criteria

- the runtime executes an explicit `PLAN -> EXECUTE -> VALIDATE -> REPLAN` loop
- retries are bounded and visible in persisted plan state
- validation failures produce corrective actions
- local memory captures prior run summaries

## Milestone 4

### Objective

Close the next runtime gaps by adding semantic memory, adaptive planning, bounded parallel execution, external execution adapters, role-aware orchestration, and richer policy validation.

### Files To Modify

- `Requirement.md`
- `Architecture.md`
- `HLD.md`
- `DD.md`
- `PLAN.md`
- `runtime/dotagent_runtime/memory.py`
- `runtime/dotagent_runtime/policy.py`
- `runtime/dotagent_runtime/planner.py`
- `runtime/dotagent_runtime/executor.py`
- `runtime/dotagent_runtime/tools.py`
- `runtime/dotagent_runtime/orchestrator.py`
- `runtime/dotagent_runtime/models.py`
- `runtime/dotagent_runtime/cli.py`
- `runtime/tests/test_orchestrator.py`
- `runtime/tests/test_planner.py`
- `runtime/tests/test_state_store.py`
- `runtime/tests/test_validator.py`

### Verification Steps

- Create a task plan and confirm adaptive steps and role metadata are present
- Execute a task and confirm semantic memory entries are written
- Execute a task with fallback and confirm retries are visible
- Prepare a task for `slurm` and `kubernetes` targets and confirm adapter output
- Run runtime unit tests inside the workspace

### Exit Criteria

- semantic memory search returns scored results
- adaptive plans include role and priority metadata
- executor supports bounded parallel batches
- external adapters exist for Slurm and Kubernetes planning
- validator enforces policy-based checks

## Milestone 5

### Objective

Make the Python runtime the single orchestration engine and reduce PowerShell to a compatibility wrapper.

### Files To Modify

- `Requirement.md`
- `Architecture.md`
- `HLD.md`
- `DD.md`
- `PLAN.md`
- `README.md`
- `scripts/run-agent.ps1`
- `scripts/install-pack.ps1`
- `runtime/dotagent_runtime/cli.py`
- `runtime/dotagent_runtime/orchestrator.py`
- `runtime/dotagent_runtime/bootstrap.py`
- `templates/runtime/scripts/run-agent.ps1`
- `templates/root-docs/CONTEXT.md`
- `templates/root-docs/PLAN.md`
- `templates/root-docs/Architecture.md`

### Verification Steps

- Run Python runtime unit tests
- Run `run-agent.ps1 setup`, `task`, `status`, and `result` as PowerShell smoke checks
- Confirm install-pack copies the Python runtime into `.agent/runtime/`

### Exit Criteria

- PowerShell no longer owns orchestration logic
- Python CLI supports the preserved command surface including `cancel`
- Installed consumer repos receive the Python runtime package they need
