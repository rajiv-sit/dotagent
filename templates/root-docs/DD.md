# DD

## Class Design

This PowerShell runtime is function-oriented rather than class-based. The design still enforces object boundaries through structured records.

- Job record
  - fields: `id`, `type`, `status`, `created_at`, `input`, `output`, `metadata`
- Artifact record
  - fields: `path`, `kind`, `exists`, `size`, `sha256`, `updated_at`
- Workflow record
  - fields: `id`, `type`, `created_at`, `objective`, `jobs`, `edges`, `status`

## Algorithms

### Job lifecycle

1. Build normalized job object with `PENDING` status.
2. Persist JSON and prompt.
3. On execution start, transition to `RUNNING`.
4. Invoke the configured assistant process.
5. If exit code is zero, transition to `SUCCESS`; else `FAILED`.
6. For review jobs that succeed, transition to `REVIEWED`.
7. Re-index artifacts after every terminal transition.

### Workflow scheduling

1. Create fixed nodes for `HLD`, `DD`, `Code`, `Test`, `Review`.
2. Persist edges as predecessor lists.
3. For execution, repeatedly scan for `PENDING` jobs whose dependencies are terminal and successful.
4. Execute one ready node at a time.
5. Stop if any required predecessor fails.
6. Mark workflow status from aggregated node states.

## Data Structures

- Hashtable-backed PowerShell objects for job and workflow records
- Arrays for artifact lists and dependency edges
- File-per-record JSON storage for simple inspectability and low operational overhead

## Complexity

- Job read/write: `O(1)` per record
- Status listing: `O(n)` for `n` jobs
- Workflow readiness scan: `O(v + e)` per scheduler pass for vertices/jobs `v` and edges `e`
- Artifact indexing: `O(a)` for `a` tracked files per job

## Error Handling

- Throw immediately on invalid command input or missing required arguments
- Persist stderr and exit code for failed executions
- Record blocked dependency context in job metadata when orchestration cannot proceed
- Treat missing files as non-fatal during artifact indexing; record `exists = false`
- Keep state transitions explicit and persisted even on failure

