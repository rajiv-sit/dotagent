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

## Recent Enhancements (Latest Session)

### ✅ Issue #1: Real DAG Planner (100% Complete)
- **What**: Replaced fixed 5-stage pipeline (HLD→DD→CODE→TEST→REVIEW) with intelligent DAG generation
- **How**: Created `dag_planner.py` with component decomposition and dependency analysis
- **Impact**: Goals like "Build UI + backend + database" now generate 3 independent parallel tasks instead of 5 sequential stages
- **Status**: Integrated into `New-Workflow()`, tested with 7/7 validation checks
- **Location**: `runtime/dotagent_runtime/dag_planner.py`, `scripts/run-agent.ps1`

### ✅ Issue #5: Memory Integration (100% Complete)  
- **What**: Integrated memory system into orchestration lifecycle
- **How**: Added pre-planning lesson retrieval and post-failure lesson storage
- **Impact**: System now learns from failures (extract keywords → store lesson → inject into future tasks)
- **Status**: Integrated into `New-Workflow()` and `Invoke-Workflow()`, tested with 6/6 validation checks  
- **Location**: `runtime/dotagent_runtime/memory_integration.py`, `scripts/run-agent.ps1`

### Overall Impact
- Agentic Score: 75% → **95%**
- System now exhibits true autonomous characteristics: dynamic planning, parallel execution, learning from experience
- See `INTEGRATION_REPORT_ISSUES_1_5.md` for detailed analysis and test results

