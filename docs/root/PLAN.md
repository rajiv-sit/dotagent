# PLAN

## Current Objective

Consolidate `dotagent` onto the Python runtime as the single orchestration engine and reduce PowerShell to a compatibility wrapper.

## Completed

- Audited the existing repo layout, docs, and runtime scripts.
- Identified the gap between strong packaging and weak runtime intelligence.
- Confirmed the Python runtime has the right module boundaries for planner, executor, validator, memory, and orchestrator work.
- Updated the design documents to target an explicit `PLAN -> EXECUTE -> VALIDATE -> REPLAN` control loop.
- Fixed the Python runtime registry break and link-validation drift.
- Added Milestone 6 robustness scope for wrapper parity, clean installs, and structured tool failure persistence.
- Hardened tool dispatch so missing or failing tools become persisted failed steps with evidence and telemetry.
- Updated PowerShell wrappers to forward runtime command, execution target, and serial execution controls for `task` and `run`.
- Updated the installer to skip generated Python cache files when copying the runtime into consumer repos.
- Updated PowerShell wrappers to suppress Python bytecode generation during runtime invocation.
- Marked legacy PowerShell-era integration reports as historical and pointed readers to the Python-canonical runtime.
- Updated `GRAPH.md` and `CONTEXT.md` to describe PowerShell as a compatibility layer over the Python CLI.
- Verified the installed consumer runtime works end-to-end after installer changes.
- Pruned obsolete transition reports, legacy standalone runtime helpers, duplicate Obsidian starter vault files, and generated local state.
- Expanded `.gitignore` for runtime state, temp workspaces, Python caches, coverage output, and local Obsidian workspace artifacts.
- Moved source-pack operational markdown from the repository root into `docs/root/`, leaving only `AGENTS.md` and `README.md` at root.
- Updated hooks, health checks, runtime discovery, and documentation links for the new `docs/root/` source layout.
- Updated `README.md` with the current source-pack layout, installer copy map, runtime status, and optional Obsidian policy.

## In Progress

- No active blockers.

## Next

- Optional: decide whether to add more consumer smoke coverage for non-Windows shells if cross-platform wrappers are introduced.

## Blockers

- None.

## Verification

- tests run:
  - `git rev-parse --abbrev-ref HEAD`
  - `python -m unittest discover -s runtime/tests -v`
  - `$env:PYTHONPATH='runtime'; python -m unittest discover -s runtime/tests -v`
  - `powershell -ExecutionPolicy Bypass -File .\.agent\scripts\validate-links.ps1 -Path .`
  - `powershell -ExecutionPolicy Bypass -File .\.agent\scripts\health-check.ps1`
  - `powershell -ExecutionPolicy Bypass -File .\scripts\run-agent.ps1 task "wrapper command smoke" -RuntimeCommand 'python --version' -ExecutionTarget slurm -Serial`
  - `powershell -ExecutionPolicy Bypass -File .\scripts\install-pack.ps1 -ProjectRoot <workspace-temp>`
- latest results:
  - runtime unit tests: 18 passed
  - markdown link validation: 564 valid links, 0 broken links
  - health check: passed with 15 checks and 0 warnings
  - wrapper smoke: command forwarding, Slurm target selection, and serial mode reached the Python plan
  - installer smoke: installed runtime contained `cli.py` and excluded `__pycache__` plus `.pyc` files
  - installed consumer smoke: install, init docs, setup, task execute, review prepare, run prepare, status, and result succeeded
  - runtime cache smoke: installed runtime remained free of `__pycache__` and `.pyc` after wrapper execution
  - stale PowerShell orchestration reference search: no current-doc matches
  - cleanup reference search: no references to pruned legacy files remain
  - cleanup install smoke: setup and task execution succeeded with 0 runtime `.pyc` files
  - source root markdown check: only `AGENTS.md` and `README.md` remain at repository root
  - graph reachability check: 91 markdown files reachable from `AGENTS.md`, 0 unreachable, 0 orphan files
  - README refresh validation: links, health check, runtime tests, and `AGENTS.md` reachability all passed after the update
- manual checks:
  - inspected the PowerShell shim, Python runtime modules, installer, schemas, docs, templates, and validation scripts
- known gaps:
  - none currently tracked
