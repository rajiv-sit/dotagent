# Requirement

## Overview

### Purpose

Make `dotagent` materially more agentic as a local orchestration layer for AI-assisted engineering work. The runtime must move beyond prepared prompts and single-pass execution into an explicit `PLAN -> EXECUTE -> VALIDATE -> REPLAN` loop with persisted state, evidence capture, and bounded recovery.

### Scope

This enhancement targets the in-repo runtime implementation, with priority on the Python runtime modules under `runtime/dotagent_runtime/` and supporting documentation. The design remains vendor-neutral, workspace-local, and file-backed. It does not add remote schedulers, hosted memory services, or distributed agents.

## Functional Requirements

- FR-1: The runtime must persist normalized job records with explicit lifecycle state and structured input, output, and metadata fields.
- FR-2: The runtime must persist plan records with step-level state, dependencies, retry metadata, and orchestration metadata.
- FR-3: The runtime must expose a concrete `PLAN -> EXECUTE -> VALIDATE -> REPLAN` loop for executable jobs.
- FR-4: The planner must generate a deterministic DAG of steps for `task` and `review` jobs.
- FR-5: The executor must dispatch steps through a tool registry rather than embedding tool-specific logic into the orchestrator.
- FR-6: The executor must support bounded retry and step-level recovery driven by planner-provided replan logic.
- FR-7: The validator must evaluate step outputs against explicit acceptance criteria and produce corrective actions on failure.
- FR-8: The runtime must persist evidence bundles containing the job, plan, outputs, validation results, and a reproducibility hash.
- FR-9: The runtime must store run history in local memory and expose enough context for later runs to retrieve relevant prior outcomes.
- FR-10: The CLI must preserve existing `setup`, `task`, `review`, `run`, `status`, and `result` flows.
- FR-11: The runtime must persist per-run telemetry including step traces, durations, retries, and aggregate metrics.
- FR-12: `status` and `result` must surface telemetry summaries without requiring users to inspect raw event logs manually.
- FR-13: The memory subsystem must support semantic-style retrieval, not only exact token matching.
- FR-14: The planner must adapt plan shape based on goal intent, prior context, and requested execution target.
- FR-15: The executor must support bounded parallel execution for independent ready steps.
- FR-16: The runtime must model explicit agent roles for planner, executor, validator, memory, and review responsibilities.
- FR-17: The runtime must support external execution targets such as Slurm and Kubernetes through local adapter tools.
- FR-18: The validator must support richer policy-based SLO checks including latency and metric policies.

## Non-Functional Requirements

- Determinism: step ordering, dependency resolution, retries, and terminal states must be derived from persisted records.
- Reliability: failed executions must retain intermediate outputs, validation context, and corrective actions.
- Observability: each run must emit reproducible trace and metrics data that can be inspected after execution.
- Safety: all operations must remain inside the workspace and default to non-destructive local execution.
- Debuggability: plans, evidence bundles, and memory entries must remain human-readable JSON.
- Extensibility: planner, executor, validator, and memory concerns must be separable modules so future tools or models can be added without rewriting orchestration logic.
- Bounded autonomy: recovery behavior must be limited by explicit retry counts and must fail closed when validation still does not pass.
- Portability: external execution adapters must degrade cleanly to local dry-run planning when real schedulers are not available.

## Data Definition

- Input:
  - CLI command arguments (`setup`, `task`, `review`, `run`, `status`, `result`)
  - job objective or review target
  - optional step payloads such as shell commands, fallback commands, and acceptance criteria
- Output:
  - persisted job JSON records under `.dotagent-state/jobs/`
  - persisted plan JSON records under `.dotagent-state/plans/`
  - event logs under `.dotagent-state/events/`
  - evidence bundles under `.dotagent-state/evidence/`
  - memory entries under `.dotagent-state/memory/`
  - telemetry summaries under `.dotagent-state/telemetry/`
- Data flow:
  - user input -> plan creation -> step scheduling -> tool execution -> validation -> optional replan/retry -> evidence write -> memory update -> status/result query

## Edge Cases

- Missing or empty project documents during discovery
- Step dependencies that can never become ready because an upstream step failed
- Shell execution failures that should switch to a fallback command on replan
- Validation failures caused by unmet acceptance thresholds even when the command exits successfully
- Existing jobs or plans that predate the new step metadata fields
- Dry-run style execution where a shell step has no command and should remain safe
- Telemetry files missing for legacy jobs should not break `status` or `result`
