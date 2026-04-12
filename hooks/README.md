# Hooks

This folder contains helper scripts used by `.codex/hooks.json`.

## Included Hooks

- `pre-bash-context.ps1`
  - emits a Codex system message reminding the agent to use graphify context when available
- `session-start.ps1`
  - emits a compact startup summary so the agent doesn't need to rediscover basic repo state
- `doc-presence.ps1`
  - reminds the agent to read root design docs directly when they exist
- `path-guard.ps1`
  - nudges the agent away from broad whole-repo shell exploration
- `graph-staleness.ps1`
  - warns when graphify output may be older than the source tree

## Token Reduction Purpose

These hooks are optimized to reduce unnecessary exploration tokens by:

- surfacing root design docs early
- preferring `graphify-out/GRAPH_REPORT.md` over broad grep/listing
- warning when the agent is about to search the whole repo
- exposing repo state once at session start

## Notes

- keep hooks deterministic
- avoid destructive side effects
- prefer context injection and guardrails over silent automation
