# CONTEXT

## Project

`dotagent` is a reusable source pack for agent-driven development. It installs project-local agents, hooks, prompts, rules, schemas, scripts, and root working-memory docs into a target repository.

## Architecture Snapshot

The current system is a local, file-backed Python runtime with Windows-first PowerShell compatibility wrappers. `scripts/install-dotagent.ps1` installs the source pack into a consumer repo, `scripts/init-project-docs.ps1` bootstraps required design docs, and `scripts/dotagent.ps1` forwards task/review/run/status/result/cancel commands into `python -m dotagent_runtime.cli` while runtime state is persisted in `.dotagent-state/`.

The active enhancement is to raise the runtime from a simple prompt wrapper into a production-grade local orchestrator with formal job records, explicit lifecycle states, workflow dependencies, and artifact indexing.

## Key Decisions

- Use a simple three-command bootstrap for new consumer projects.
  - Run from the project root after the `dotagent/` folder is present:
    - `powershell -ExecutionPolicy Bypass -File .\dotagent\scripts\install-dotagent.ps1 -ProjectRoot .`
    - `powershell -ExecutionPolicy Bypass -File .\.agent\scripts\init-project-docs.ps1 -ProjectRoot .`
    - `powershell -ExecutionPolicy Bypass -File .\.agent\scripts\dotagent.ps1 setup`
  - Impact: a new project gets `AGENTS.md`, `CONTEXT.md`, `PLAN.md`, `.agent/`, `docs/design/`, and `docs/dotagent-user-guide.html` before feature work starts.

- Setup must bridge into an operational lifecycle guide.
  - Reason: environment initialization alone does not explain how to run epics, Jira intake, codebase digestion, planning, implementation, review, validation, and evidence workflows.
  - Impact: `init-project-docs.ps1` writes `docs/dotagent-user-guide.html` so users have a single manual after setup.

- Treat task or Jira intake as a plan-first workflow.
  - Recommended request pattern: read `AGENTS.md`, `CONTEXT.md`, `PLAN.md`, and `docs/design/`; then generate `docs/plans/<feature-name>-plan.md` from the task or Jira ticket.
  - The generated plan should capture requirements, architecture impact, implementation steps, likely files, tests, risks, and verification commands.
  - Impact: implementation starts from a traceable feature plan instead of an unstructured prompt.

- Use branch-per-feature execution after the plan exists.
  - Recommended request pattern: create `feature/<feature-name>`, implement the generated plan one milestone at a time, validate after each milestone, and update `PLAN.md` plus `CONTEXT.md` when project state changes.
  - Impact: work stays reviewable and aligned with the current execution tracker.

- Treat peer review as a targeted fix workflow.
  - Recommended request pattern: paste review comments, address only actionable feedback, keep diffs minimal, and rerun relevant validation.
  - Impact: review response stays focused instead of turning into unrelated refactoring.

- Require pre-PR validation.
  - Recommended request pattern: run lint, tests, coverage, pre-commit checks, and markdown link checks where available; fix failures and summarize commands plus results.
  - Impact: PRs carry concrete evidence for correctness and remaining risk.

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

- `runtime/dotagent_runtime/cli.py`: canonical runtime and orchestration entry point
- `scripts/dotagent.ps1`: PowerShell compatibility wrapper over the Python runtime
- `scripts/install-dotagent.ps1`: source-pack installer
- `scripts/init-project-docs.ps1`: project-doc bootstrapper
- `docs/dotagent-user-guide.html`: user-facing operational manual generated into consumer projects
- `schemas/*.json`: output and document contracts
- `prompts/task.md`, `prompts/review.md`: prompt templates
- `.dotagent-state/`: runtime persistence

## Linked Docs

- [docs/design/README.md](../design/README.md)
- [docs/design/Requirement.md](../design/Requirement.md)
- [docs/design/Architecture.md](../design/Architecture.md)
- [docs/design/HLD.md](../design/HLD.md)
- [docs/design/DD.md](../design/DD.md)
- [docs/design/milestone.md](../design/milestone.md)
- [PLAN.md](PLAN.md)

## Architecture Decision (April 16, 2026)

**Split responsibility clearly:**

- **dotagent does**: Execution, validation, feedback, state management
- **External LLM does**: Reasoning, planning, deciding, learning

**Why**: Each layer does one thing well instead of pretending to do everything

See [docs/design/Architecture.md](../design/Architecture.md), [docs/design/HLD.md](../design/HLD.md), and [docs/design/DD.md](../design/DD.md) for the current architecture and implementation design.

### Production-Ready Components

- ✅ **Execution Engine**: Deterministic tool execution with timeouts and retries
- ✅ **Output Validator**: Rigorous property checking (syntax, tests, requirements, artifacts)
- ✅ **State Manager**: Reliable job tracking and artifact persistence
- ✅ **Feedback Collector**: Comprehensive error reporting to external LLM
- ✅ **Orchestrator**: Reliable coordination of jobs and workflows

All components are tested through the Python runtime, with `scripts/run-agent.ps1` acting as the compatibility entrypoint.
