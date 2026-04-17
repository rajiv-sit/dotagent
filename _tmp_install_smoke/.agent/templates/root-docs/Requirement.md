# Requirement

## Overview

### Purpose

Make `dotagent` production-grade as a local orchestration layer for AI-assisted engineering work. The runtime must model jobs explicitly, support deterministic lifecycle transitions, handle simple dependency chains, and index execution artifacts for traceability.

### Scope

This change applies to the `dotagent` source pack itself, primarily the local PowerShell runtime, schemas, prompts, and documentation. The pack must remain vendor-neutral so teams can use Codex, Claude, Copilot, or another assistant that can follow local repo instructions. It does not introduce external services or distributed scheduling.

## Functional Requirements

- FR-1: The runtime must persist jobs using a formal job record shape with `id`, `type`, `status`, `created_at`, `input`, `output`, and `metadata`.
- FR-2: The runtime must support explicit lifecycle states: `PENDING`, `RUNNING`, `SUCCESS`, `FAILED`, `REVIEWED`, and `CANCELLED`.
- FR-3: The runtime must expose an orchestration command capable of creating and tracking a dependency chain for `HLD -> DD -> Code -> Test -> Review`.
- FR-4: The runtime must store dependency metadata so downstream steps can reference upstream artifacts.
- FR-5: The runtime must persist an artifact index for each job, including SHA256 digests for generated evidence files.
- FR-6: The runtime must preserve existing single-job flows for `task` and `review`.
- FR-7: The runtime must surface job graph status in a way that is readable from the CLI.

## Non-Functional Requirements

- Determinism: lifecycle transitions must be explicit and derived from persisted state, not inferred from console output.
- Reliability: failed executions must retain stderr, output, event logs, and metadata for postmortem inspection.
- Safety: all operations must remain local to the workspace and avoid destructive behavior.
- Compatibility: existing prepared jobs and the current `.dotagent-state/` layout should remain readable where practical.
- Simplicity: orchestration should remain local, file-backed, and easy to debug without a background service.

## Data Definition

- Input:
  - CLI command arguments (`task`, `review`, `run`, `status`, `result`, `cancel`)
  - prompt text or orchestration objective
  - optional model and sandbox parameters
- Output:
  - persisted job JSON records
  - prompt files
  - output files
  - stderr and event logs
  - artifact index JSON files with SHA256 digests
  - optional workflow graph JSON files
- Data flow:
  - user input -> prompt rendering -> job record creation -> optional execution -> artifact hashing/indexing -> state query commands

## Edge Cases

- Missing assistant CLI shim such as `agent.cmd` on PATH
- Failed upstream dependency should block downstream execution
- Cancelled jobs should not be executed by orchestrated runs
- Existing jobs created with the old schema may be missing new fields
- Empty or missing output files should not break artifact indexing

