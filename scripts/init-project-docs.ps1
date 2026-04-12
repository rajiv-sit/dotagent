param(
    [string]$ProjectRoot = ".",
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-ManagedFile {
    param(
        [string]$Path,
        [string]$Content,
        [switch]$Force
    )

    if ((Test-Path -LiteralPath $Path) -and -not $Force) {
        Write-Output "Skipped existing file: $Path"
        return
    }

    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }

    $Content | Set-Content -LiteralPath $Path -Encoding UTF8
    Write-Output "Wrote file: $Path"
}

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path

$requirement = @'
# Requirement

## Functional Requirements

- Describe the core capabilities the system must provide.
- Describe the main user and system interactions.
- Describe expected input and output behavior.

## Non-Functional Requirements

- Performance targets: latency, throughput, startup time.
- Scalability targets: expected growth and concurrency.
- Reliability targets: availability, retries, recovery expectations.
- Determinism and safety constraints.
- Resource constraints: CPU, memory, storage, network.

## Data Definition

- Input data formats.
- Output data formats.
- Data flow through the system.

## Edge Cases

- Failure modes.
- Boundary conditions.
- Invalid input handling.
'@

$architecture = @'
# Architecture

## System Overview

- Describe the end-to-end workflow.
- List the major components and their roles.

## Architecture Style

- Monolithic, distributed, hybrid, pipeline, or event-driven.
- Explain why this style fits the problem.

## Technology Selection

- Primary languages and frameworks.
- Why each technology was selected.

## Interfaces

- Module interfaces.
- Data contracts.
- Internal and external communication protocols.

## Visualization And Debugging

- Real-time views or dashboards if needed.
- Metrics and observability approach.
- Debugging tools and trace points.
'@

$hld = @'
# HLD

## Modules

- List the major modules.
- State each module's responsibility.

## System Decomposition

- Explain how the system is partitioned.
- Show which modules own which behaviors.

## Data Flow

- Describe how data moves between modules.
- Call out critical paths.

## External Dependencies

- Third-party services.
- Databases, queues, APIs, SDKs, or platform dependencies.

## Integration Points

- Internal boundaries.
- External integration boundaries.
- Deployment-time or runtime integration concerns.
'@

$dd = @'
# DD

## Class Design

- Key classes, interfaces, and responsibilities.
- Encapsulation boundaries.
- Inheritance or composition strategy where relevant.

## Algorithms

- Step-by-step logic for critical workflows.
- Pseudocode where useful.

## Data Structures

- Chosen data structures.
- Why they are appropriate.

## Complexity

- Time complexity for critical paths.
- Space complexity for critical paths.

## Error Handling

- Exception and error propagation strategy.
- Recovery mechanisms.
- Logging and observability approach.
'@

$milestone = @'
# milestone

## Milestone 1

### Objective

- Describe the milestone outcome.

### Files To Modify

- List expected files or directories.

### Verification Steps

- Unit tests.
- Integration tests.
- Manual checks.

### Exit Criteria

- Define what must be true before the milestone is complete.

## Milestone 2

### Objective

- Describe the milestone outcome.

### Files To Modify

- List expected files or directories.

### Verification Steps

- Unit tests.
- Integration tests.
- Manual checks.

### Exit Criteria

- Define what must be true before the milestone is complete.
'@

Write-ManagedFile -Path (Join-Path $root "Requirement.md") -Content $requirement -Force:$Force
Write-ManagedFile -Path (Join-Path $root "Architecture.md") -Content $architecture -Force:$Force
Write-ManagedFile -Path (Join-Path $root "HLD.md") -Content $hld -Force:$Force
Write-ManagedFile -Path (Join-Path $root "DD.md") -Content $dd -Force:$Force
Write-ManagedFile -Path (Join-Path $root "milestone.md") -Content $milestone -Force:$Force

Write-Output ""
Write-Output "Project document bootstrap complete."
Write-Output "Project root: $root"
