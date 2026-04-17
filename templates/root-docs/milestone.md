# milestone

## Milestone 1

### Objective

Define and land formal runtime contracts for jobs, workflows, lifecycle states, and artifact evidence.

### Files To Modify

- `docs/design/Requirement.md`
- `docs/design/Architecture.md`
- `docs/design/HLD.md`
- `docs/design/DD.md`
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

