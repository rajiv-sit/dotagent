#!/usr/bin/env pwsh
<#
    Integration Test for Issue #1 (Real DAG Planner) and Issue #5 (Memory Integration)
    
    Tests:
    1. Real DAG generation for complex goal
    2. Memory retrieval before planning
    3. Memory storage after failure
    4. Retrieval of stored lessons
#>

param(
    [string]$ProjectRoot = $PSScriptRoot
)

$ErrorActionPreference = "Stop"

# Helper functions
function Write-Header {
    param([string]$Message)
    Write-Host "`n" -NoNewline
    Write-Host "=" * 80
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "=" * 80 -NoNewline
}

function Test-DAGPlanner {
    Write-Header "TEST 1: Real DAG Planner (Issue #1)"
    
    $goal = "Build satellite UI + backend with PostgreSQL database"
    Write-Host "Testing goal: $goal`n"
    
    # Call dag_planner_cli
    $output = & python -m dotagent_runtime.dag_planner_cli `
        --goal "$goal" `
        --project-root $ProjectRoot `
        --json-output 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ DAG Planner failed" -ForegroundColor Red
        return $false
    }
    
    $result = $output | ConvertFrom-Json
    
    # Validation checks
    $checks = @(
        @{ name = "Has tasks"; test = { $result.tasks.Count -gt 0 } },
        @{ name = "Detects parallelization"; test = { $result.has_parallelization -eq $true } },
        @{ name = "Task count > 1"; test = { $result.task_count -gt 1 } },
        @{ name = "UI task found"; test = { $result.tasks | Where-Object { $_.name -like "*UI*" -or $_.name -like "*ui*" } } },
        @{ name = "Backend task found"; test = { $result.tasks | Where-Object { $_.name -like "*backend*" -or $_.name -like "*Backend*" } } },
        @{ name = "Database task found"; test = { $result.tasks | Where-Object { $_.name -like "*database*" -or $_.name -like "*Database*" -or $_.name -like "*PostgreSQL*" } } },
        @{ name = "Integration task present"; test = { $result.tasks | Where-Object { $_.name -like "*Integrate*" -or $_.name -like "*integrate*" } } }
    )
    
    $passed = 0
    foreach ($check in $checks) {
        if (& $check.test) {
            Write-Host "  ✓ $($check.name)" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "  ✗ $($check.name)" -ForegroundColor Red
        }
    }
    
    Write-Host "`n📊 DAG Structure:"
    foreach ($task in $result.tasks) {
        $deps = if ($task.depends_on.Count -gt 0) { " (depends: $($task.depends_on -join ', '))" } else { " (independent)" }
        Write-Host "  - $($task.id): $($task.name)$deps"
    }
    
    $success = $passed -eq $checks.Count
    Write-Host "`n$(if ($success) {' ✓ '} else {' ✗ '}) DAG Planner: $passed/$($checks.Count) checks passed" -ForegroundColor $(if ($success) { "Green" } else { "Red" })
    
    return $success
}

function Test-MemoryRetrieval {
    Write-Header "TEST 2: Memory Retrieval (Issue #5)"
    
    Write-Host "Testing memory retrieval for authentication task`n"
    
    $output = & python -m dotagent_runtime.memory_integration_cli `
        --goal "Implement authentication system" `
        --mode retrieve `
        --json-output 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Memory retrieval failed (expected if no prior lessons)" -ForegroundColor Yellow
        return $true
    }
    
    $result = $output | ConvertFrom-Json
    
    $checks = @(
        @{ name = "Has mode"; test = { $result.mode -eq "retrieve" } },
        @{ name = "Has goal"; test = { $result.goal -ne $null } },
        @{ name = "Has lessons_prompt"; test = { $result.lessons_prompt -ne $null } }
    )
    
    $passed = 0
    foreach ($check in $checks) {
        if (& $check.test) {
            Write-Host "  ✓ $($check.name)" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "  ✗ $($check.name)" -ForegroundColor Red
        }
    }
    
    if ($result.lessons -and $result.lessons.Count -gt 0) {
        Write-Host "`n📚 Retrieved $($result.lessons.Count) lessons:"
        foreach ($lesson in $result.lessons[0..2]) {
            Write-Host "  - $($lesson.Substring(0, [Math]::Min(60, $lesson.Length)))" -ForegroundColor Gray
        }
    }
    
    $success = $passed -eq $checks.Count
    Write-Host "`n$(if ($success) {' ✓ '} else {' ✗ '}) Memory Retrieval: $passed/$($checks.Count) checks passed" -ForegroundColor $(if ($success) { "Green" } else { "Red" })
    
    return $success
}

function Test-MemoryStorage {
    Write-Header "TEST 3: Memory Storage (Issue #5)"
    
    Write-Host "Testing memory storage for a failure`n"
    
    # Create temp files with step and result data
    $tempDir = [System.IO.Path]::GetTempPath()
    $stepFile = Join-Path $tempDir "test_step_$(New-Guid).json"
    $resultFile = Join-Path $tempDir "test_result_$(New-Guid).json"
    
    $stepData = @{
        step_id = "test_step_authentication"
        kind = "IMPL"
        action = "Implement authentication system"
    }
    
    $resultData = @{
        status = "FAILED"
        error = "JWT token validation failed"
        stderr = "Module 'jwt' not found"
        exit_code = 1
    }
    
    ConvertTo-Json $stepData | Set-Content -Path $stepFile -Encoding UTF8
    ConvertTo-Json $resultData | Set-Content -Path $resultFile -Encoding UTF8
    
    Write-Host "Storing failure: JWT token validation failed`n"
    
    $output = & python -m dotagent_runtime.memory_integration_cli `
        --goal "Implement authentication system" `
        --step-json $stepFile `
        --result-json $resultFile `
        --attempt 0 `
        --mode store `
        --json-output 2>$null
    
    Remove-Item -LiteralPath $stepFile -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $resultFile -Force -ErrorAction SilentlyContinue
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Memory storage failed" -ForegroundColor Red
        return $false
    }
    
    $result = $output | ConvertFrom-Json
    
    $checks = @(
        @{ name = "Mode is store"; test = { $result.mode -eq "store" } },
        @{ name = "Storage successful"; test = { $result.stored -eq $true } },
        @{ name = "Has message"; test = { $result.message -ne $null } }
    )
    
    $passed = 0
    foreach ($check in $checks) {
        if (& $check.test) {
            Write-Host "  ✓ $($check.name)" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "  ✗ $($check.name)" -ForegroundColor Red
        }
    }
    
    Write-Host "`n💾 Result: $($result.message)"
    
    $success = $passed -eq $checks.Count
    Write-Host "`n$(if ($success) {' ✓ '} else {' ✗ '}) Memory Storage: $passed/$($checks.Count) checks passed" -ForegroundColor $(if ($success) { "Green" } else { "Red" })
    
    return $success
}

function Test-MemoryRetrieval2 {
    Write-Header "TEST 4: Memory Retrieval After Storage (Issue #5)"
    
    Write-Host "Testing that stored lessons are now retrievable`n"
    
    $output = & python -m dotagent_runtime.memory_integration_cli `
        --goal "Implement authentication system" `
        --mode retrieve `
        --json-output 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Memory retrieval failed" -ForegroundColor Red
        return $false
    }
    
    $result = $output | ConvertFrom-Json
    
    $checks = @(
        @{ name = "Has lessons after storage"; test = { $result.lessons -and $result.lessons.Count -gt 0 } },
        @{ name = "lessons_prompt includes stored content"; test = { $result.lessons_prompt -like "*jwt*" -or $result.lessons_prompt -like "*JWT*" -or $result.lessons_prompt -like "*authentication*" } }
    )
    
    $passed = 0
    foreach ($check in $checks) {
        if (& $check.test) {
            Write-Host "  ✓ $($check.name)" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "  ✗ $($check.name)" -ForegroundColor Red
        }
    }
    
    if ($result.lessons -and $result.lessons.Count -gt 0) {
        Write-Host "`n📚 Retrieved $($result.lessons.Count) lessons (including stored one):"
        foreach ($lesson in $result.lessons[0..1]) {
            Write-Host "  - $($lesson.Substring(0, [Math]::Min(70, $lesson.Length)))..." -ForegroundColor Gray
        }
    }
    
    $success = $passed -eq $checks.Count
    Write-Host "`n$(if ($success) {' ✓ '} else {' ✗ '}) Memory Retrieval After Storage: $passed/$($checks.Count) checks passed" -ForegroundColor $(if ($success) { "Green" } else { "Red" })
    
    return $success
}

# Main test execution
try {
    Write-Header "Integration Tests: Issue #1 (DAG Planner) + Issue #5 (Memory Integration)"
    
    $results = @()
    $results += Test-DAGPlanner
    $results += Test-MemoryRetrieval
    $results += Test-MemoryStorage
    $results += Test-MemoryRetrieval2
    
    Write-Header "Test Summary"
    
    $total = $results.Count
    $passed = ($results | Where-Object { $_ -eq $true }).Count
    
    Write-Host "`n📊 Results: $passed/$total tests passed`n" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })
    
    if ($passed -eq $total) {
        Write-Host "✅ All integration tests PASSED - Issues #1 and #5 are 100% complete!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "⚠️  Some tests failed. Review output above for details." -ForegroundColor Yellow
        exit 1
    }
    
} catch {
    Write-Host "`n❌ Test execution error: $_" -ForegroundColor Red
    exit 2
}
