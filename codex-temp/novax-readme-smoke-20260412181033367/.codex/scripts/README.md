# Scripts

This folder contains the install and runtime scripts for `dotcodex`.

## Included

- `install-dotcodex.ps1`
  - installs the source pack into a real project root
  - writes `AGENTS.md`, `CONTEXT.md`, `PLAN.md`, and the project-local `.codex/` contents
- `dotcodex.ps1`
  - local runtime for prompt packaging and job tracking

## Typical Usage

From a real project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\dotcodex\scripts\install-dotcodex.ps1 -ProjectRoot .
powershell -ExecutionPolicy Bypass -File .\.codex\scripts\dotcodex.ps1 setup
```

`dotcodex.ps1` does not depend on Claude plugin APIs. Instead it:

- renders prompt templates from `prompts/`
- stores local job records under `.dotcodex-state/`
- lets a team track `task`, `review`, `status`, `result`, and `cancel`
- can optionally execute prepared prompts through the local Codex CLI when `codex.cmd exec` is available

This gives `dotcodex` the same separation-of-concerns pattern as a plugin-backed system without requiring a plugin runtime.
