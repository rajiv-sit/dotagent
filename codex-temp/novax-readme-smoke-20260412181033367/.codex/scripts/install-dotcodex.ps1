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
$projectRootPath = (Resolve-Path -LiteralPath $ProjectRoot).Path
$codexRoot = Join-Path $projectRootPath ".codex"

Ensure-Dir $codexRoot

Copy-ManagedFile -Source (Join-Path $sourceRoot "AGENTS.md") -Destination (Join-Path $projectRootPath "AGENTS.md") -Force:$Force
Copy-ManagedFile -Source (Join-Path $sourceRoot "CONTEXT.md") -Destination (Join-Path $projectRootPath "CONTEXT.md") -Force:$Force
Copy-ManagedFile -Source (Join-Path $sourceRoot "PLAN.md") -Destination (Join-Path $projectRootPath "PLAN.md") -Force:$Force
Copy-ManagedFile -Source (Join-Path $sourceRoot "hooks.json") -Destination (Join-Path $codexRoot "hooks.json") -Force:$Force

foreach ($name in @("agents", "hooks", "prompts", "rules", "schemas", "scripts", "skills")) {
    Copy-ManagedDirectory -Source (Join-Path $sourceRoot $name) -Destination (Join-Path $codexRoot $name) -Force:$Force
}

Write-Output ""
Write-Output "dotcodex install complete."
Write-Output "Project root: $projectRootPath"
Write-Output "Next steps:"
Write-Output "1. Create Requirement.md, Architecture.md, HLD.md, DD.md, and milestone.md in the project root."
Write-Output "2. Run: powershell -ExecutionPolicy Bypass -File .\.codex\scripts\dotcodex.ps1 setup"
Write-Output "3. Start work with: powershell -ExecutionPolicy Bypass -File .\.codex\scripts\dotcodex.ps1 task ""Describe the first milestone"""
