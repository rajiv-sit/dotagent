param(
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet("setup", "task", "review", "run", "status", "result", "cancel")]
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

function Resolve-RuntimeRoot {
    $scriptParent = Split-Path -Parent $PSScriptRoot
    $candidates = @(
        (Join-Path $scriptParent "runtime"),
        (Join-Path $scriptParent "..\runtime")
    )

    foreach ($candidate in $candidates) {
        $resolved = Resolve-Path -LiteralPath $candidate -ErrorAction SilentlyContinue
        if ($resolved -and (Test-Path -LiteralPath (Join-Path $resolved.Path "dotagent_runtime\__init__.py"))) {
            return $resolved.Path
        }
    }

    throw "dotagent Python runtime not found next to scripts. Expected runtime/dotagent_runtime."
}

function Invoke-DotagentPythonCli {
    param(
        [string[]]$CliArgs
    )

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        throw "python is required to run dotagent."
    }

    $runtimeRoot = Resolve-RuntimeRoot
    $previousPyPath = $env:PYTHONPATH
    try {
        if ($previousPyPath) {
            $env:PYTHONPATH = "$runtimeRoot;$previousPyPath"
        } else {
            $env:PYTHONPATH = $runtimeRoot
        }

        & python -m dotagent_runtime.cli @CliArgs
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    } finally {
        $env:PYTHONPATH = $previousPyPath
    }
}

$projectRoot = Get-ProjectRoot
$cliArgs = @("--project-root", $projectRoot, $Command)

switch ($Command) {
    "task" {
        if (-not $Text) {
            throw "Provide task text."
        }
        $cliArgs += $Text
        if ($Execute) {
            $cliArgs += "--execute"
        }
    }
    "review" {
        $reviewTarget = if ($Target) { $Target } elseif ($Text) { $Text } else { "" }
        if (-not $reviewTarget) {
            throw "Provide review text or -Target."
        }
        $cliArgs += "--target"
        $cliArgs += $reviewTarget
        if ($Execute) {
            $cliArgs += "--execute"
        }
    }
    "run" {
        if (-not $Text) {
            throw "Provide orchestration text."
        }
        $cliArgs += $Text
        if ($Execute) {
            $cliArgs += "--execute"
        }
    }
    "result" {
        if (-not $Id) {
            throw "Provide -Id for result."
        }
        $cliArgs += "--id"
        $cliArgs += $Id
    }
    "cancel" {
        if (-not $Id) {
            throw "Provide -Id for cancel."
        }
        $cliArgs += "--id"
        $cliArgs += $Id
    }
}

if ($Model) {
    Write-Warning "-Model is accepted for compatibility but is not used by the Python runtime."
}
if ($PSBoundParameters.ContainsKey("Sandbox")) {
    Write-Warning "-Sandbox is accepted for compatibility but is not used by the Python runtime."
}

Invoke-DotagentPythonCli -CliArgs $cliArgs
