param(
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet("setup", "task", "review", "status", "result", "cancel")]
    [string]$Command,

    [Parameter(Position = 1)]
    [string]$Text,

    [string]$Target,
    [string]$Id,
    [switch]$Execute,
    [string]$Model,
    [ValidateSet("read-only", "workspace-write", "danger-full-access")]
    [string]$Sandbox = "workspace-write"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-ProjectRoot {
    return (Get-Location).Path
}

function Get-StateRoot {
    $root = Get-ProjectRoot
    return Join-Path $root ".dotcodex-state"
}

function Ensure-Dir {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Get-Template {
    param([string]$Name)
    $scriptRoot = $PSScriptRoot
    $repoRoot = Split-Path -Parent $scriptRoot
    return Get-Content -LiteralPath (Join-Path $repoRoot "prompts\$Name") -Raw
}

function Get-RepoRoot {
    $scriptRoot = $PSScriptRoot
    return Split-Path -Parent $scriptRoot
}

function Get-SchemaPath {
    param([string]$Name)
    return Join-Path (Get-RepoRoot) "schemas\$Name"
}

function Render-Template {
    param(
        [string]$Template,
        [hashtable]$Tokens
    )
    $out = $Template
    foreach ($key in $Tokens.Keys) {
        $out = $out.Replace("{{${key}}}", [string]$Tokens[$key])
    }
    return $out
}

function New-JobId {
    param([string]$Prefix)
    return "$Prefix-" + [DateTime]::UtcNow.ToString("yyyyMMddHHmmssfff")
}

function Convert-ToProcessArguments {
    param([string[]]$Arguments)

    $quoted = foreach ($arg in $Arguments) {
        if ($null -eq $arg) {
            '""'
        } else {
            '"' + ($arg -replace '"', '\"') + '"'
        }
    }
    return [string]::Join(' ', $quoted)
}

function Write-JobRecord {
    param(
        [string]$JobId,
        [hashtable]$Record,
        [string]$PromptText
    )
    $stateRoot = Get-StateRoot
    $jobsRoot = Join-Path $stateRoot "jobs"
    Ensure-Dir $stateRoot
    Ensure-Dir $jobsRoot
    $jsonPath = Join-Path $jobsRoot "$JobId.json"
    $promptPath = Join-Path $jobsRoot "$JobId.prompt.md"
    $Record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $jsonPath -Encoding UTF8
    $PromptText | Set-Content -LiteralPath $promptPath -Encoding UTF8
    return @{
        json = $jsonPath
        prompt = $promptPath
    }
}

function Read-JobRecord {
    param([string]$JobId)
    $jsonPath = Join-Path (Join-Path (Get-StateRoot) "jobs") "$JobId.json"
    if (-not (Test-Path -LiteralPath $jsonPath)) {
        throw "Job not found: $JobId"
    }
    return Get-Content -LiteralPath $jsonPath -Raw | ConvertFrom-Json
}

function Save-JobRecord {
    param(
        [string]$JobId,
        [object]$Record
    )
    $jsonPath = Join-Path (Join-Path (Get-StateRoot) "jobs") "$JobId.json"
    $Record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $jsonPath -Encoding UTF8
}

function Set-RecordField {
    param(
        [object]$Record,
        [string]$Name,
        [object]$Value
    )
    if ($Record.PSObject.Properties.Name -contains $Name) {
        $Record.$Name = $Value
    } else {
        $Record | Add-Member -NotePropertyName $Name -NotePropertyValue $Value
    }
}

function Get-CodexCommand {
    $cmd = Get-Command codex.cmd -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $shim = Get-Command codex -ErrorAction SilentlyContinue
    if ($shim -and $shim.Source -like "*.cmd") { return $shim.Source }
    return $null
}

function Invoke-CodexPreparedJob {
    param(
        [string]$JobId,
        [string]$Kind,
        [string]$Model,
        [string]$Sandbox
    )

    $codex = Get-CodexCommand
    if (-not $codex) {
        throw "codex.cmd was not found on PATH."
    }

    $stateRoot = Get-StateRoot
    $jobsRoot = Join-Path $stateRoot "jobs"
    $promptPath = Join-Path $jobsRoot "$JobId.prompt.md"
    $record = Read-JobRecord -JobId $JobId
    $outputPath = Join-Path $jobsRoot "$JobId.output.md"
    $jsonlPath = Join-Path $jobsRoot "$JobId.events.jsonl"
    $stderrPath = Join-Path $jobsRoot "$JobId.stderr.log"
    $schemaFile = if ($Kind -eq "review") { "review-output.schema.json" } else { "task-output.schema.json" }
    $schemaPath = Get-SchemaPath $schemaFile

    $argList = New-Object System.Collections.Generic.List[string]
    $argList.Add("exec") | Out-Null
    $argList.Add("-C") | Out-Null
    $argList.Add((Get-ProjectRoot)) | Out-Null
    $argList.Add("-s") | Out-Null
    $argList.Add($Sandbox) | Out-Null
    $argList.Add("--json") | Out-Null
    $argList.Add("--output-schema") | Out-Null
    $argList.Add($schemaPath) | Out-Null
    $argList.Add("-o") | Out-Null
    $argList.Add($outputPath) | Out-Null
    if ($Model) {
        $argList.Add("-m") | Out-Null
        $argList.Add($Model) | Out-Null
    }
    $argList.Add("-") | Out-Null

    Set-RecordField -Record $record -Name "status" -Value "running"
    Set-RecordField -Record $record -Name "started_at" -Value ([DateTime]::UtcNow.ToString("o"))
    Save-JobRecord -JobId $JobId -Record $record

    $promptText = Get-Content -LiteralPath $promptPath -Raw
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $codex
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.Arguments = Convert-ToProcessArguments -Arguments $argList

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi
    $process.Start() | Out-Null
    $process.StandardInput.Write($promptText)
    $process.StandardInput.Close()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    $stdout | Set-Content -LiteralPath $jsonlPath -Encoding UTF8
    $stderr | Set-Content -LiteralPath $stderrPath -Encoding UTF8

    Set-RecordField -Record $record -Name "status" -Value $(if ($process.ExitCode -eq 0) { "completed" } else { "failed" })
    Set-RecordField -Record $record -Name "completed_at" -Value ([DateTime]::UtcNow.ToString("o"))
    Set-RecordField -Record $record -Name "exit_code" -Value $process.ExitCode
    Set-RecordField -Record $record -Name "output_file" -Value $outputPath
    Set-RecordField -Record $record -Name "events_file" -Value $jsonlPath
    Set-RecordField -Record $record -Name "stderr_file" -Value $stderrPath
    Set-RecordField -Record $record -Name "prompt_preview" -Value ($promptText.Substring(0, [Math]::Min(140, $promptText.Length)))
    Save-JobRecord -JobId $JobId -Record $record

    return $record
}

switch ($Command) {
    "setup" {
        $stateRoot = Get-StateRoot
        Ensure-Dir $stateRoot
        Ensure-Dir (Join-Path $stateRoot "jobs")
        Write-Output "dotcodex runtime ready: $stateRoot"
    }
    "task" {
        if (-not $Text) { throw "Provide task text." }
        $jobId = New-JobId "task"
        $template = Get-Template "task.md"
        $prompt = Render-Template $template @{ TASK = $Text }
        $record = @{
            id = $jobId
            kind = "task"
            status = "prepared"
            summary = $Text
            created_at = [DateTime]::UtcNow.ToString("o")
        }
        $paths = Write-JobRecord -JobId $jobId -Record $record -PromptText $prompt
        Write-Output "Prepared task: $jobId"
        Write-Output "Prompt: $($paths.prompt)"
        Write-Output "Record: $($paths.json)"
        if ($Execute) {
            $result = Invoke-CodexPreparedJob -JobId $jobId -Kind "task" -Model $Model -Sandbox $Sandbox
            Write-Output "Executed task: $($result.id) [$($result.status)]"
            Write-Output "Output: $($result.output_file)"
        }
    }
    "review" {
        $reviewTarget = if ($Target) { $Target } elseif ($Text) { $Text } else { "current change set" }
        $jobId = New-JobId "review"
        $template = Get-Template "review.md"
        $prompt = Render-Template $template @{ TARGET = $reviewTarget }
        $record = @{
            id = $jobId
            kind = "review"
            status = "prepared"
            summary = $reviewTarget
            created_at = [DateTime]::UtcNow.ToString("o")
        }
        $paths = Write-JobRecord -JobId $jobId -Record $record -PromptText $prompt
        Write-Output "Prepared review: $jobId"
        Write-Output "Prompt: $($paths.prompt)"
        Write-Output "Record: $($paths.json)"
        if ($Execute) {
            $result = Invoke-CodexPreparedJob -JobId $jobId -Kind "review" -Model $Model -Sandbox $Sandbox
            Write-Output "Executed review: $($result.id) [$($result.status)]"
            Write-Output "Output: $($result.output_file)"
        }
    }
    "status" {
        $jobsRoot = Join-Path (Get-StateRoot) "jobs"
        if (-not (Test-Path -LiteralPath $jobsRoot)) {
            Write-Output "No dotcodex state found."
            break
        }
        Get-ChildItem -LiteralPath $jobsRoot -Filter *.json |
            Sort-Object LastWriteTime -Descending |
            ForEach-Object {
                $record = Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json
                Write-Output "$($record.id) [$($record.kind)] $($record.status) - $($record.summary)"
            }
    }
    "result" {
        if (-not $Id) { throw "Provide -Id for result." }
        $record = Read-JobRecord -JobId $Id
        Write-Output ($record | ConvertTo-Json -Depth 6)
        if ($record.PSObject.Properties.Name -contains "output_file" -and (Test-Path -LiteralPath $record.output_file)) {
            Write-Output ""
            Write-Output "--- output ---"
            Get-Content -LiteralPath $record.output_file
        }
    }
    "cancel" {
        if (-not $Id) { throw "Provide -Id for cancel." }
        $record = Read-JobRecord -JobId $Id
        Set-RecordField -Record $record -Name "status" -Value "cancelled"
        Set-RecordField -Record $record -Name "cancelled_at" -Value ([DateTime]::UtcNow.ToString("o"))
        Save-JobRecord -JobId $Id -Record $record
        Write-Output "Cancelled: $Id"
    }
}
