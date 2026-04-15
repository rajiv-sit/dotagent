# Scripts

This folder contains the install and runtime scripts for `dotagent`.

## Included

- `install-dotagent.ps1`
  - installs the source pack into a real project root
  - writes `AGENTS.md`, `CONTEXT.md`, `PLAN.md`, and the project-local `.agent/` contents
- `init-project-docs.ps1`
  - creates the required root design documents for a new project
  - writes `Requirement.md`, `Architecture.md`, `HLD.md`, `DD.md`, and `milestone.md`
- `dotagent.ps1`
  - local runtime for prompt packaging, job tracking, workflow orchestration, and artifact indexing

## Typical Usage

From a real project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\dotagent\scripts\install-dotagent.ps1 -ProjectRoot .
powershell -ExecutionPolicy Bypass -File .\.agent\scripts\init-project-docs.ps1 -ProjectRoot .
powershell -ExecutionPolicy Bypass -File .\.agent\scripts\dotagent.ps1 setup
```

`dotagent.ps1` does not depend on provider-specific plugin APIs. Instead it:

- renders prompt templates from `prompts/`
- stores local job records under `.dotagent-state/`
- stores workflow graphs under `.dotagent-state/graphs/`
- lets a team track `task`, `review`, `run`, `status`, `result`, and `cancel`
- can optionally execute prepared prompts through the local agent CLI when `agent.cmd exec` is available

Lifecycle states:

- `PENDING`
- `RUNNING`
- `SUCCESS`
- `FAILED`
- `REVIEWED`
- `CANCELLED`

Workflow orchestration:

- `run` creates a local DAG for `HLD -> DD -> CODE -> TEST -> REVIEW`
- dependency metadata is persisted on each job
- artifact evidence bundles include SHA256 digests for prompt, output, stderr, and event files

This gives `dotagent` the same separation-of-concerns pattern as a plugin-backed system without requiring a plugin runtime.


