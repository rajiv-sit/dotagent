# PowerShell runtime orchestration layer for dotagent
# Wraps Python runtime and provides CLI interface for Issues 1-6

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Get Python runtime path
function Get-RuntimePythonPath {
    $repoRoot = Split-Path $PSScriptRoot -Parent
    $runtimeDir = Join-Path $repoRoot "runtime"
    return $runtimeDir
}

# Planner: Call Python planner_cli to generate dynamic DAG
function Invoke-DynamicPlanner {
    param(
        [string]$Goal,
        [string]$ProjectRoot = ".",
        [string]$JobType = "task",
        [switch]$AsJson = $true
    )

    $pythonPath = Get-RuntimePythonPath
    $pythonExe = "python"
    
    $dagOutput = & $pythonExe -m dotagent_runtime.planner_cli `
        --goal $Goal `
        --project-root $ProjectRoot `
        --job-type $JobType `
        --json-output

    if ($LASTEXITCODE -ne 0) {
        throw "Planner failed: $dagOutput"
    }

    if ($AsJson) {
        return $dagOutput | ConvertFrom-Json
    }
    return $dagOutput
}

# Validator: Call Python validator_cli to validate step results
function Invoke-ValidationEngine {
    param(
        [string]$StepJson,
        [string]$ResultJson,
        [string]$ProjectRoot = "."
    )

    $pythonPath = Get-RuntimePythonPath
    $pythonExe = "python"

    $validationOutput = & $pythonExe -m dotagent_runtime.validator_cli `
        --step-json $StepJson `
        --result-json $ResultJson `
        --project-root $ProjectRoot

    if ($LASTEXITCODE -ne 0) {
        return @{
            status = "FAIL"
            summary = "Validation engine error"
            error = $validationOutput
        }
    }

    return $validationOutput | ConvertFrom-Json
}

# Retry Loop: Execute step with auto-retry and failure context
function Invoke-StepWithRetry {
    param(
        [hashtable]$Step,
        [hashtable]$Context = @{},
        [int]$MaxRetries = 3,
        [hashtable]$Tools = @{}
    )

    $result = $null
    $lastError = $null
    
    for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
        Write-Host "Attempt $attempt/$MaxRetries for step $($Step.id)"
        
        try {
            # Check if tool is available internally
            $toolName = $Step.tool
            if ($Tools.ContainsKey($toolName)) {
                $result = & $Tools[$toolName] $Step
            } else {
                # Fallback to LLM execution if tool not found
                $result = Invoke-ExternalTool $Step $Context
            }

            if ($result.ok) {
                Write-Host "Step $($Step.id) succeeded on attempt $attempt"
                return $result
            }

            $lastError = $result.output.stderr
            Write-Host "Step $($Step.id) failed: $lastError"
            
            # Generate fix prompt for next attempt
            if ($attempt -lt $MaxRetries) {
                $fixPrompt = @"
The previous attempt failed with error:
$lastError

Please fix the issue and retry.
Context: $($Step.name)
"@
                Write-Host "Retrying with fix context..."
            }
        } catch {
            $lastError = $_.Exception.Message
            if ($attempt -eq $MaxRetries) {
                throw $_
            }
            Write-Host "Exception on attempt $attempt: $lastError"
        }
    }

    throw "Step $($Step.id) failed after $MaxRetries attempts. Last error: $lastError"
}

# Tool Registry: Maps tool names to PowerShell scriptblocks
function New-ToolRegistry {
    return @{
        "write_file" = {
            param($task)
            $path = $task.path
            $content = $task.content
            $parent = Split-Path $path -Parent
            if (-not (Test-Path $parent)) {
                New-Item -ItemType Directory -Path $parent -Force | Out-Null
            }
            Set-Content -Path $path -Value $content
            return @{ ok = $true; output = @{ message = "File written to $path" } }
        }
        
        "run_tests" = {
            param($task)
            $command = $task.command
            if (-not $command) {
                $command = "python -m pytest"
            }
            $output = & $command 2>&1
            $exitCode = $LASTEXITCODE
            return @{
                ok = ($exitCode -eq 0)
                output = @{
                    stdout = $output
                    stderr = if ($exitCode -ne 0) { "Tests failed with exit code $exitCode" } else { "" }
                    returncode = $exitCode
                }
            }
        }
        
        "run_linter" = {
            param($task)
            $command = $task.command
            if (-not $command) {
                $command = "python -m pylint . --disable=all"
            }
            $output = & $command 2>&1
            $exitCode = $LASTEXITCODE
            return @{
                ok = ($exitCode -eq 0)
                output = @{
                    stdout = $output
                    returncode = $exitCode
                }
            }
        }

        "build" = {
            param($task)
            $command = $task.command
            if (-not $command) {
                $command = "cmake --build . --config Release"
            }
            $output = & $command 2>&1
            $exitCode = $LASTEXITCODE
            return @{
                ok = ($exitCode -eq 0)
                output = @{
                    stdout = $output
                    returncode = $exitCode
                }
            }
        }
    }
}

# Memory Layer: Load and save persistent memory
function New-MemoryStore {
    param([string]$StorePath = ".dotagent-state/memory")
    
    if (-not (Test-Path $StorePath)) {
        New-Item -ItemType Directory -Path $StorePath -Force | Out-Null
    }

    return @{
        failures = @()
        solutions = @()
        patterns = @()
        path = $StorePath
    }
}

function Save-MemoryStore {
    param(
        [hashtable]$Store,
        [string]$FilePath = ".dotagent-state/memory/store.json"
    )

    $dir = Split-Path $FilePath -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    $data = @{
        failures = $Store.failures
        solutions = $Store.solutions
        patterns = $Store.patterns
        timestamp = Get-Date -AsUTC -Format o
    }

    $data | ConvertTo-Json -Depth 10 | Set-Content -Path $FilePath
}

function Load-MemoryStore {
    param([string]$FilePath = ".dotagent-state/memory/store.json")

    if (-not (Test-Path $FilePath)) {
        return @{
            failures = @()
            solutions = @()
            patterns = @()
        }
    }

    $data = Get-Content -Path $FilePath -Raw | ConvertFrom-Json
    return @{
        failures = $data.failures
        solutions = $data.solutions
        patterns = $data.patterns
    }
}

# Observability: Logging and metrics
function Write-JobLog {
    param(
        [string]$JobId,
        [string]$Status,
        [int]$DurationMs = 0,
        [string]$LogPath = ".dotagent-state/logs/run.log"
    )

    $logDir = Split-Path $LogPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    $logEntry = "$JobId,$Status,$DurationMs,$(Get-Date -AsUTC -Format o)"
    Add-Content -Path $LogPath -Value $logEntry
}

function Get-JobMetrics {
    param([string]$LogPath = ".dotagent-state/logs/run.log")

    if (-not (Test-Path $LogPath)) {
        return @{
            total_jobs = 0
            success_count = 0
            failed_count = 0
            avg_duration_ms = 0
        }
    }

    $lines = @(Get-Content -Path $LogPath)
    $totalJobs = $lines.Length
    $successCount = ($lines | Where-Object { $_ -match ',SUCCESS,' }).Length
    $failedCount = ($lines | Where-Object { $_ -match ',FAILED,' }).Length
    
    $durations = @()
    foreach ($line in $lines) {
        if ($line -match ',(\d+),') {
            $durations += [int]$matches[1]
        }
    }
    
    $avgDuration = if ($durations) { ($durations | Measure-Object -Average).Average } else { 0 }

    return @{
        total_jobs = $totalJobs
        success_count = $successCount
        failed_count = $failedCount
        avg_duration_ms = [math]::Round($avgDuration)
    }
}

# Export functions
Export-ModuleMember -Function @(
    "Invoke-DynamicPlanner",
    "Invoke-ValidationEngine",
    "Invoke-StepWithRetry",
    "New-ToolRegistry",
    "New-MemoryStore",
    "Save-MemoryStore",
    "Load-MemoryStore",
    "Write-JobLog",
    "Get-JobMetrics"
)
