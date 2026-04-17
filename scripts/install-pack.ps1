param(
    [string]$ProjectRoot = ".",
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-Dir {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Copy-ManagedFile {
    param(
        [string]$Source,
        [string]$Destination,
        [switch]$Force
    )

    $parent = Split-Path -Parent $Destination
    Ensure-Dir $parent

    if ((Test-Path -LiteralPath $Destination) -and -not $Force) {
        Write-Output "Skipped existing file: $Destination"
        return
    }

    Copy-Item -LiteralPath $Source -Destination $Destination -Force
    Write-Output "Installed file: $Destination"
}

function Copy-ManagedDirectory {
    param(
        [string]$Source,
        [string]$Destination,
        [switch]$Force
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Required source directory not found: $Source"
    }

    Ensure-Dir $Destination

    Get-ChildItem -LiteralPath $Source -Recurse -File | ForEach-Object {
        $relative = $_.FullName.Substring($Source.Length).TrimStart('\', '/')
        $target = Join-Path $Destination $relative
        $targetParent = Split-Path -Parent $target
        Ensure-Dir $targetParent

        if ((Test-Path -LiteralPath $target) -and -not $Force) {
            Write-Output "Skipped existing file: $target"
        } else {
            Copy-Item -LiteralPath $_.FullName -Destination $target -Force
            Write-Output "Installed file: $target"
        }
    }
}

$sourceRoot = Split-Path -Parent $PSScriptRoot
$templatesRoot = Join-Path $sourceRoot "templates"
$rootDocsSource = Join-Path $templatesRoot "root-docs"
$runtimeSource = Join-Path $templatesRoot "runtime"
$workflowSource = Join-Path $templatesRoot "workflows"
$pythonRuntimeSource = Join-Path $sourceRoot "runtime\dotagent_runtime"

foreach ($requiredPath in @($rootDocsSource, $runtimeSource, $workflowSource, $pythonRuntimeSource)) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Required template path not found: $requiredPath"
    }
}

$projectRootPath = (Resolve-Path -LiteralPath $ProjectRoot).Path
$agentRoot = Join-Path $projectRootPath ".agent"

Ensure-Dir $agentRoot

foreach ($name in @("AGENTS.md", "CONTEXT.md", "PLAN.md")) {
    Copy-ManagedFile -Source (Join-Path $rootDocsSource $name) -Destination (Join-Path $projectRootPath $name) -Force:$Force
}

Copy-ManagedFile -Source (Join-Path $runtimeSource "hooks.json") -Destination (Join-Path $agentRoot "hooks.json") -Force:$Force

foreach ($name in @("agents", "hooks", "rules", "schemas", "skills", "scripts")) {
    Copy-ManagedDirectory -Source (Join-Path $runtimeSource $name) -Destination (Join-Path $agentRoot $name) -Force:$Force
}

Copy-ManagedDirectory -Source $pythonRuntimeSource -Destination (Join-Path $agentRoot "runtime\dotagent_runtime") -Force:$Force

Copy-ManagedDirectory -Source $rootDocsSource -Destination (Join-Path $agentRoot "templates\root-docs") -Force:$Force
Copy-ManagedDirectory -Source $workflowSource -Destination (Join-Path $agentRoot "workflows") -Force:$Force

Write-Output ""
Write-Output "dotagent pack install complete."
Write-Output "Project root: $projectRootPath"
Write-Output "Next steps:"
Write-Output "1. Run: powershell -ExecutionPolicy Bypass -File .\.agent\scripts\init-project-docs.ps1 -ProjectRoot ."
Write-Output "2. Run: powershell -ExecutionPolicy Bypass -File .\.agent\scripts\run-agent.ps1 setup"
Write-Output "3. Start work with: powershell -ExecutionPolicy Bypass -File .\.agent\scripts\run-agent.ps1 task ""Describe the first milestone"""
