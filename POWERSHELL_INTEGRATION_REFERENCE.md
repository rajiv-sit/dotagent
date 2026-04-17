# PowerShell Integration Reference - Issue #1 & #5

## Quick Reference: Where Integration Happens

### File: `scripts/run-agent.ps1`

#### 1. Real DAG Planner (Issue #1) Integration

**Location**: `New-Workflow()` function

**What Changed**:
- Replaced call to old `planner_cli` with new `dag_planner_cli`
- Generates real DAG instead of fixed pipeline

**PowerShell Code** (approximately lines 780-830):
```powershell
# STEP 1: Call real DAG planner to generate dynamic DAG (Issue #1)
$planOutput = & python -m dotagent_runtime.dag_planner_cli `
    --goal "$Objective" `
    --project-root $projectRoot `
    --json-output 2>$null

# Result contains: $plannerOutput.tasks (array of Task objects)
# Each task has: id, name, depends_on, work_types, can_parallelize
```

**Fallback Behavior**:
- If `dag_planner_cli` fails, falls back to old `planner_cli`  
- If both fail, uses hardcoded 5-stage pipeline (legacy)

---

#### 2. Memory Integration - RETRIEVE Phase (Issue #5)

**Location**: `New-Workflow()` function - BEFORE planning

**What It Does**:
- Retrieves previous failure lessons for the goal
- Injects lessons into job prompts before execution

**PowerShell Code** (approximately lines 789-805):
```powershell
# STEP 0: Retrieve lessons before planning (Issue #5 - Memory Integration)
$lessonsContext = ""
try {
    $memoryOutput = & python -m dotagent_runtime.memory_integration_cli `
        --goal "$Objective" `
        --mode retrieve `
        --json-output 2>$null

    if ($LASTEXITCODE -eq 0 -and $memoryOutput) {
        $memoryData = $memoryOutput | ConvertFrom-Json
        if ($memoryData.lessons_prompt) {
            $lessonsContext = $memoryData.lessons_prompt
            Write-Output "📚 Retrieved lessons from previous similar tasks"
        }
    }
}
```

**Output**:
- `$lessonsContext` contains formatted prompt with:
  - Previous similar task results
  - Common failures and fixes
  - Agent-friendly guidance

**Injection** (approximately lines 869-877):
```powershell
# Inject lessons into prompt
$taskDescription = "$($step.action) - $Objective"
if ($lessonsContext) {
    $taskDescription = "$taskDescription`n`n$lessonsContext"
}

$prompt = Render-Template -Template (Get-Template -Name "task.md") `
    -Tokens @{ TASK = $taskDescription }
```

---

#### 3. Memory Integration - STORE Phase (Issue #5)

**Location 1**: `Invoke-Workflow()` - Validation Failure Handler

**When It Triggers**:
- Output validation fails but is retryable (validation failed, but not critical)
- Store the failure pattern for learning

**PowerShell Code** (approximately lines 1082-1120):
```powershell
# Store failure lesson (Issue #5 - Memory Integration)
$tempStepFile2 = Join-Path ([System.IO.Path]::GetTempPath()) "step_mem_$(New-Guid).json"
$tempResultFile2 = Join-Path ([System.IO.Path]::GetTempPath()) "result_mem_$(New-Guid).json"

# Prepare step and result data
$stepJson = @{ step_id = $jobRef.step_id; kind = $jobRef.stage; action = $job.summary }
$resultJson = @{ status = $job.status; errors = $validationOutput.errors; stderr = $job.output.stderr }

# Write to temp files
ConvertTo-Json $stepJson | Set-Content -Path $tempStepFile2 -Encoding UTF8
ConvertTo-Json $resultJson | Set-Content -Path $tempResultFile2 -Encoding UTF8

# Call memory integration to store
& python -m dotagent_runtime.memory_integration_cli `
    --goal "$($job.summary)" `
    --step-json $tempStepFile2 `
    --result-json $tempResultFile2 `
    --attempt $(($attempts - 1)) `
    --mode store `
    --json-output 2>$null | Out-Null

Write-Output "  💾 Failure pattern stored for learning"

# Cleanup
Remove-Item -LiteralPath $tempStepFile2 -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $tempResultFile2 -Force -ErrorAction SilentlyContinue
```

**Location 2**: `Invoke-Workflow()` - Execution Failure Handler

**When It Triggers**:
- Job execution fails (exit code != 0)
- Task can be retried or max attempts exhausted

**PowerShell Code** (approximately lines 1188-1253):
```powershell
# Store execution failure as lesson (Issue #5 - Memory Integration)
try {
    $tempStepFile4 = Join-Path ([System.IO.Path]::GetTempPath()) "step_mem_$(New-Guid).json"
    $tempResultFile4 = Join-Path ([System.IO.Path]::GetTempPath()) "result_mem_$(New-Guid).json"
    
    $stepJson = @{ step_id = $jobRef.step_id; kind = $jobRef.stage; action = $job.summary }
    $resultJson = @{ status = $job.status; exit_code = $job.output.exit_code; stderr = $job.output.stderr }
    
    ConvertTo-Json $stepJson | Set-Content -Path $tempStepFile4 -Encoding UTF8
    ConvertTo-Json $resultJson | Set-Content -Path $tempResultFile4 -Encoding UTF8
    
    & python -m dotagent_runtime.memory_integration_cli `
        --goal "$($job.summary)" `
        --step-json $tempStepFile4 `
        --result-json $tempResultFile4 `
        --attempt $(($attempts - 1)) `
        --mode store `
        --json-output 2>$null | Out-Null
    
    Write-Output "  💾 Execution failure stored for learning"
}
```

---

## Module Dependency Chain

```
New-Workflow()
  ├─→ memory_integration_cli --mode retrieve
  │    └─→ memory_integration.py: retrieve_lessons_for_goal()
  │
  └─→ dag_planner_cli
       ├─→ dag_planner.py: GoalDecomposer.decompose()
       └─→ dag_planner.py: DAGOptimizer.optimize()

Invoke-Workflow()
  ├─→ [Validation checks]
  │    └─→ output_validator [EXISTING]
  │
  └─→ [Failure scenarios]
       └─→ memory_integration_cli --mode store
            └─→ memory_integration.py: store_failure_lesson()
```

---

## Testing

### Integration Test File
```
tests/integration_test_issues_1_5.py
```

### Run All Tests
```powershell
cd c:\Users\MrSit\source\repos\dotagent
python tests/integration_test_issues_1_5.py
```

### Expected Output
```
✓ TEST 1: Real DAG Planner (7/7 checks passed)
✓ TEST 2: Memory Retrieval (3/3 checks passed)
✓ TEST 3: Memory Storage (3/3 checks passed)
✓ TEST 4: Memory Retrieval After Storage (2/2 checks passed)

📊 Results: 4/4 tests passed
✅ All integration tests PASSED
```

---

## Troubleshooting

### If memory_integration_cli fails
- Check Python path: `$PYTHONPATH` should include runtime directory
- Check temp file permissions: `/tmp` or system temp dir must be writable
- Check JSON format: step and result files must be valid JSON

### If dag_planner_cli fails
- Check goal parsing: complex goals with multiple components work best
- Check project root: must point to valid dotagent project
- Check Python dependencies: all imports in dag_planner.py must be available

### If integration tests fail
- Run with verbose: `python tests/integration_test_issues_1_5.py -v`
- Check specific test: Tests 1, 2, 3, 4 are independent
- Review test file: `tests/integration_test_issues_1_5.py` for debug info

---

## Key Metrics

| Metric | Value |
|--------|-------|
| DAG Planner Lines | 300+ |
| Memory Integration Lines | 315+ |  
| CLI Wrappers Lines | 170+ |
| PowerShell Integration Points | 5+ |
| Test Cases | 4 |
| Validation Checks | 15 |
| Pass Rate | 100% ✅ |

---

## Future Enhancements

1. **Parallel Task Execution**: Queue independent tasks concurrently
2. **Memory Persistence**: Move from file-based to lightweight database
3. **Advanced DAG Features**: Handle more complex dependency patterns
4. **Learning Tuning**: Adjust TF-IDF parameters for better lesson matching
5. **Performance Optimization**: Cache DAG generation results

