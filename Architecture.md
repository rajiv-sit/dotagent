# Architecture

## System Overview

`dotagent` remains a local, file-backed orchestration runtime, but the control loop is now defined explicitly instead of being implied by prepared prompts. The runtime decomposes execution into planner, executor, validator, memory, and orchestrator modules. The orchestrator owns lifecycle control and drives a bounded `PLAN -> EXECUTE -> VALIDATE -> REPLAN` loop until the plan succeeds or reaches a terminal failure.

The architecture remains vendor-neutral. The stable interface is still the local repo contract: docs, rules, prompts, schemas, plans, jobs, evidence bundles, and telemetry records. Tool execution can stay local and can later be pointed at an assistant CLI, shell command, or API-backed adapter.

Core flow:

1. Parse CLI command.
2. Create a normalized job record.
3. Build a deterministic step graph and persist a plan record.
4. Retrieve relevant local memory for the objective.
5. Schedule ready steps in dependency order.
6. Execute each step via the executor's tool registry.
7. Validate step output against acceptance criteria.
8. Replan and retry when bounded recovery is available.
9. Persist telemetry traces and metrics for the run.
10. Persist final evidence and write run memory.
11. Expose status and result queries.
12. Reuse semantic memory and role summaries for future runs.

## Architecture Style

- Monolithic local CLI runtime
- File-backed DAG orchestration
- Modular agentic control loop inside one process

This is intentionally simpler than a distributed scheduler but strong enough to model goal-driven local automation with traceability, bounded recovery, and testable module boundaries.

## Technology Selection

- Python runtime modules:
  - clearer module boundaries for planner, executor, validator, memory, and orchestrator
  - easier unit testing for step scheduling and validation logic
  - portable implementation path while remaining local-first
- PowerShell wrappers:
  - preserve Windows-first ergonomics and installation flow
  - maintain compatibility with the existing source-pack usage model
- JSON persistence:
  - keeps jobs, plans, evidence, and memory inspectable
  - avoids requiring a service process or external database

## Interfaces

- CLI interface:
  - `setup`
  - `task`
  - `review`
  - `run`
  - `status`
  - `result`
- Runtime interfaces:
  - planner interface creates plans and corrective updates
  - executor interface dispatches tools and captures execution results
  - validator interface evaluates acceptance criteria and emits corrective actions
  - memory interface stores and retrieves local run summaries
  - telemetry interface records step spans, retry counts, and run metrics
  - external adapter interface exposes local contracts for Slurm and Kubernetes style execution targets
- Persisted contracts:
  - `.dotagent-state/jobs/<job-id>.json`
  - `.dotagent-state/plans/<plan-id>.json`
  - `.dotagent-state/events/events.jsonl`
  - `.dotagent-state/evidence/<job-id>.json`
  - `.dotagent-state/memory/<namespace>.jsonl`
  - `.dotagent-state/telemetry/<job-id>.json`

## Visualization And Debugging

- `status` provides an at-a-glance view of persisted job state.
- plan JSON provides the debugging view for step dependencies, retries, and terminal outcomes.
- evidence bundles provide reproducibility data, including validation output and SHA256 digest.
- event logs provide the time-ordered orchestration trace.
- telemetry summaries provide aggregate metrics such as total duration, step counts, retry counts, and failure points.
- agent-role summaries show which planner/executor/validator/memory responsibilities were active in the run.
