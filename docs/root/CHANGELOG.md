# Changelog

All notable dotagent source-pack changes are tracked here.

## Unreleased

### Changed

- Kept the repository root intentionally small with only `AGENTS.md` and `README.md`.
- Moved source-pack operational docs into `docs/root/`.
- Updated hooks, health checks, runtime discovery, and documentation links for the `docs/root/` source layout.
- Clarified that Obsidian is optional and is not automatically installed by dotagent.
- Removed obsolete transition reports, duplicate Obsidian starter vault files, generated local state, and legacy standalone runtime helpers.
- Updated README with the current source-pack layout, installer copy map, Python runtime status, and Obsidian policy.

### Fixed

- Added runtime validation support for either installed-project `PLAN.md` or source-pack `docs/root/PLAN.md`.
- Updated the weekly PLAN reminder workflow to link to `docs/root/PLAN.md` for this source repository.
- Removed duplicate reviewer-agent and unused root hook config from the tracked source pack.

## 1.0.0 - 2026-04-12

### Added

- Project-local `AGENTS.md`, `CONTEXT.md`, and `PLAN.md` templates.
- Specialist agent profiles, reusable skills, engineering rules, hooks, schemas, prompts, and installer scripts.
- Documentation guides for quick start, migration, troubleshooting, customization, rule hierarchy, skills, GitHub Actions, Obsidian, case study, and starter templates.
- Python runtime modules for planning, execution, validation, telemetry, evidence, memory, and local state storage.

### Changed

- Established `docs/design/` as the required design-document location for Requirement, Architecture, HLD, DD, and milestone docs.
- Standardized the local workflow around `PLAN -> EXECUTE -> VALIDATE -> REPLAN`.

### Compatibility

- Installed consumer projects still receive root-level `AGENTS.md`, `CONTEXT.md`, and `PLAN.md`.
- PowerShell remains the Windows compatibility entrypoint over the Python runtime.
