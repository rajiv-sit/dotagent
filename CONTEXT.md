# CONTEXT

## Project

`dotagent` is a reusable source pack for agent-driven development. It installs project-local agents, hooks, prompts, rules, schemas, scripts, and root working-memory docs into a target repository.

## Architecture Snapshot

The current system is a local, file-backed PowerShell runtime. `scripts/install-dotagent.ps1` installs the source pack into a consumer repo, `scripts/init-project-docs.ps1` bootstraps required design docs, and `scripts/dotagent.ps1` prepares or executes task/review workflows while persisting state in `.dotagent-state/`.

The active enhancement is to raise the runtime from a simple prompt wrapper into a production-grade local orchestrator with formal job records, explicit lifecycle states, workflow dependencies, and artifact indexing.

## Key Decisions

- Keep orchestration local and file-backed.
  - Reason: the current repo already uses local PowerShell scripts and JSON records.
  - Impact: easier debugging and adoption, but no distributed scheduler.

- Add a normalized job contract rather than ad hoc record shapes.
  - Reason: current state files are useful but not rigorous enough for traceability.
  - Impact: status/result/reporting become more deterministic.

- Model orchestration as a lightweight DAG.
  - Reason: the missing workflow chain is the main production gap in the current runtime.
  - Impact: `HLD -> DD -> Code -> Test -> Review` can be tracked explicitly without adding a service.

## Constraints

- Technical:
  - Windows-first PowerShell runtime
  - no external database or scheduler
  - must remain workspace-local

- Operational:
  - preserve simple CLI ergonomics
  - keep generated state human-readable

## Known Risks

- Validator scripts under `.agent/scripts/` are stronger as utilities than as rigorously tested production code.
  - Mitigation: keep changes targeted and validate behavior with actual command runs.

- Existing job records may not match the new schema exactly.
  - Mitigation: make read paths tolerant of missing fields where practical.

## Important Paths

- `scripts/dotagent.ps1`: main runtime and orchestration entry point
- `scripts/install-dotagent.ps1`: source-pack installer
- `scripts/init-project-docs.ps1`: root doc bootstrapper
- `schemas/*.json`: output and document contracts
- `prompts/task.md`, `prompts/review.md`: prompt templates
- `.dotagent-state/`: runtime persistence

## Linked Docs

- `Requirement.md`
- `Architecture.md`
- `HLD.md`
- `DD.md`
- `milestone.md`
- `PLAN.md`

## Architecture Decision (April 16, 2026)

**Split responsibility clearly:**

- **dotagent does**: Execution, validation, feedback, state management
- **External LLM does**: Reasoning, planning, deciding, learning

**Why**: Each layer does one thing well instead of pretending to do everything

See `docs/ARCHITECTURE_HONEST_DESIGN.md` for detailed rationale and design.

### Production-Ready Components

- ✅ **Execution Engine**: Deterministic tool execution with timeouts and retries
- ✅ **Output Validator**: Rigorous property checking (syntax, tests, requirements, artifacts)
- ✅ **State Manager**: Reliable job tracking and artifact persistence
- ✅ **Feedback Collector**: Comprehensive error reporting to external LLM
- ✅ **Orchestrator**: Reliable coordination of jobs and workflows

All components tested and integrated into `scripts/run-agent.ps1`

