# Upgrade Summary

This package preserves the original source-pack installation contract and extends it into a runnable local agentic framework.

## Added
- `.agent/runtime/dotagent_runtime/` Python runtime package
- planner
- tool registry and executor tools
- validator
- state store
- memory manager
- orchestrator
- CLI
- evidence bundle generation
- tests
- GitHub Actions workflow for Python tests

## Preserved design
- source pack at repo root
- active installed runtime under `.agent/`
- local state under `.dotagent-state/`
- PowerShell install/bootstrap commands
