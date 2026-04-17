# Default Agent

This is the default Agent agent profile for everyday development.

## Primary Context

Read these operational root docs directly before substantial work:

- `CONTEXT.md`
- `PLAN.md`

Then read these design docs under `docs/design/`:

- `docs/design/Requirement.md`
- `docs/design/Architecture.md`
- `docs/design/HLD.md`
- `docs/design/DD.md`
- `docs/design/milestone.md`

If they are incomplete, treat completion of those documents as the first task before major implementation.

## Execution Model

- use the root markdown docs as the source of truth for scope, architecture, and sequencing
- use `CONTEXT.md` for durable decisions and constraints
- use `PLAN.md` for current execution state and recent history
- implement one milestone at a time
- validate after each milestone before proceeding
- prefer root-cause fixes and minimal diffs

## graphify

- if `graphify-out/GRAPH_REPORT.md` exists, read it before broad architecture or codebase analysis
- if `graphify-out/wiki/index.md` exists, prefer it over broad raw-file exploration
- use graph context to avoid re-deriving architecture each session

## Delegation

Delegate only when the task clearly matches a specialist:

- `code-reviewer.md`
- `backend-engineer.md`
- `security-reviewer.md`
- `performance-reviewer.md`
- `doc-reviewer.md`
- `frontend-designer.md`

