# dotagent Health Check Script
# Validates that your dotagent Agent project setup is correct
# Usage: .\health-check.ps1
# Output: All checks passed or Issues found (with descriptions)

param(
    [switch]$Verbose = $false,
    [switch]$Fix = $false
)

$script:checks = @()
$script:warnings = @()
$script:errors = @()
$projectRoot = (Get-Item -Path $PSScriptRoot).Parent.Parent.FullName
$script:isInstalledLayout = Test-Path "$projectRoot\.agent\agents\default-agent.md"
$script:isSourcePackLayout = Test-Path "$projectRoot\agents\default-agent.md"

Write-Host "dotagent Health Check" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host "Project: $projectRoot`n"

function Test-FileExists {
    param(
        [string]$Path,
        [string]$Description,
        [bool]$Critical = $true
    )

    $relativePath = $Path -replace [regex]::Escape($projectRoot), "."

    if (Test-Path $Path) {
        $script:checks += @{ Status = "OK"; Check = $Description; Path = $relativePath }
        return $true
    }

    if ($Critical) {
        $script:errors += @{ Check = $Description; Path = $relativePath; Status = "File not found"; Fix = "Create $relativePath" }
    } else {
        $script:warnings += @{ Check = $Description; Path = $relativePath; Status = "File not found"; Optional = $true }
    }
    return $false
}

function Test-DirectoryExists {
    param(
        [string]$Path,
        [string]$Description,
        [bool]$Critical = $true
    )

    $relativePath = $Path -replace [regex]::Escape($projectRoot), "."

    if (Test-Path $Path -PathType Container) {
        $script:checks += @{ Status = "OK"; Check = $Description; Path = $relativePath }
        return $true
    }

    if ($Critical) {
        $script:errors += @{ Check = $Description; Path = $relativePath; Status = "Directory not found"; Fix = "Create $relativePath" }
    } else {
        $script:warnings += @{ Check = $Description; Path = $relativePath; Status = "Directory not found"; Optional = $true }
    }
    return $false
}

function Resolve-LayoutPath {
    param(
        [string]$InstalledRelative,
        [string]$SourcePackRelative
    )

    $installedPath = Join-Path $projectRoot $InstalledRelative
    $sourcePackPath = Join-Path $projectRoot $SourcePackRelative

    if (Test-Path $installedPath) {
        return $installedPath
    }

    if (Test-Path $sourcePackPath) {
        return $sourcePackPath
    }

    if ($script:isInstalledLayout -or -not $script:isSourcePackLayout) {
        return $installedPath
    }

    return $sourcePackPath
}

function Test-FileNotEmpty {
    param(
        [string]$Path,
        [string]$Description
    )

    $relativePath = $Path -replace [regex]::Escape($projectRoot), "."

    if ((Test-Path $Path) -and (Get-Item $Path).Length -gt 0) {
        $script:checks += @{ Status = "OK"; Check = $Description; Path = $relativePath }
        return $true
    }

    $script:errors += @{ Check = $Description; Path = $relativePath; Status = "File is empty"; Fix = "Populate $relativePath with content" }
    return $false
}

Write-Host "1. Core Documentation Files" -ForegroundColor Yellow
$null = Test-FileNotEmpty "$projectRoot\AGENTS.md" "AGENTS.md exists and has content"
$null = Test-FileNotEmpty "$projectRoot\CONTEXT.md" "CONTEXT.md exists and has content"
$null = Test-FileNotEmpty "$projectRoot\PLAN.md" "PLAN.md exists and has content"

Write-Host "`n2. Agent Configuration" -ForegroundColor Yellow
$null = Test-DirectoryExists "$projectRoot\.agent" ".agent directory exists"
$defaultAgentPath = Resolve-LayoutPath -InstalledRelative ".agent\agents\default-agent.md" -SourcePackRelative "agents\default-agent.md"
$rulesPath = Resolve-LayoutPath -InstalledRelative ".agent\rules" -SourcePackRelative "rules"
$null = Test-FileExists $defaultAgentPath "Default agent profile exists"
$null = Test-DirectoryExists $rulesPath "Rules directory exists"
$null = Test-FileExists "$projectRoot\hooks.json" "hooks.json exists" $false

Write-Host "`n3. Rules and Standards" -ForegroundColor Yellow
$rulesDir = $rulesPath
if (Test-Path $rulesDir) {
    $ruleCount = @(Get-ChildItem -Path $rulesDir -Filter "*.md" | Measure-Object).Count
    if ($ruleCount -gt 0) {
        $relativeRules = $rulesDir -replace [regex]::Escape($projectRoot), "."
        $script:checks += @{ Status = "OK"; Check = "Rules found"; Path = "$relativeRules ($ruleCount files)" }
    } else {
        $relativeRules = $rulesDir -replace [regex]::Escape($projectRoot), "."
        $script:warnings += @{ Check = "Rules found"; Path = $relativeRules; Status = "No rule files (.md)"; Optional = $true }
    }
}

Write-Host "`n4. Agents" -ForegroundColor Yellow
$agentsDir = Resolve-LayoutPath -InstalledRelative ".agent\agents" -SourcePackRelative "agents"
if (Test-Path $agentsDir) {
    $agentCount = @(Get-ChildItem -Path $agentsDir -Filter "*.md" | Measure-Object).Count
    $relativeAgents = $agentsDir -replace [regex]::Escape($projectRoot), "."
    if ($agentCount -gt 0) {
        $script:checks += @{ Status = "OK"; Check = "Agents found"; Path = "$relativeAgents ($agentCount files)" }
    } else {
        $script:errors += @{ Check = "Agents found"; Path = $relativeAgents; Status = "No agent files (.md)"; Fix = "Add default-agent.md and other agents" }
    }
}

Write-Host "`n5. Skills" -ForegroundColor Yellow
$skillsDir = Resolve-LayoutPath -InstalledRelative ".agent\skills" -SourcePackRelative "skills"
if (Test-Path $skillsDir) {
    $skillCount = @(Get-ChildItem -Path $skillsDir -Directory | Measure-Object).Count
    $relativeSkills = $skillsDir -replace [regex]::Escape($projectRoot), "."
    if ($skillCount -gt 0) {
        $script:checks += @{ Status = "OK"; Check = "Skills found"; Path = "$relativeSkills ($skillCount directories)" }
    } else {
        $script:warnings += @{ Check = "Skills found"; Path = $relativeSkills; Status = "No skill directories"; Optional = $true }
    }
}

Write-Host "`n6. Hooks" -ForegroundColor Yellow
$hooksDir = Resolve-LayoutPath -InstalledRelative ".agent\hooks" -SourcePackRelative "hooks"
if (Test-Path $hooksDir) {
    $hookCount = @(Get-ChildItem -Path $hooksDir -Filter "*.ps1" | Measure-Object).Count
    $relativeHooks = $hooksDir -replace [regex]::Escape($projectRoot), "."
    if ($hookCount -gt 0) {
        $script:checks += @{ Status = "OK"; Check = "Hooks found"; Path = "$relativeHooks ($hookCount scripts)" }
    } else {
        $script:warnings += @{ Check = "Hooks found"; Path = $relativeHooks; Status = "No PowerShell hooks (.ps1)"; Optional = $true }
    }
}

Write-Host "`n7. Scripts" -ForegroundColor Yellow
$scriptsDir = Resolve-LayoutPath -InstalledRelative ".agent\scripts" -SourcePackRelative "scripts"
if (Test-Path $scriptsDir) {
    $scriptCount = @(Get-ChildItem -Path $scriptsDir -Filter "*.ps1" | Measure-Object).Count
    $relativeScripts = $scriptsDir -replace [regex]::Escape($projectRoot), "."
    if ($scriptCount -gt 0) {
        $script:checks += @{ Status = "OK"; Check = "Scripts found"; Path = "$relativeScripts ($scriptCount files)" }
    } else {
        $script:warnings += @{ Check = "Scripts found"; Path = $relativeScripts; Status = "No PowerShell scripts (.ps1)"; Optional = $true }
    }
}

Write-Host "`n8. Documentation" -ForegroundColor Yellow
$null = Test-DirectoryExists "$projectRoot\docs" "Documentation directory exists" $false
$null = Test-FileExists "$projectRoot\README.md" "README.md exists"
$null = Test-FileExists "$projectRoot\CONTRIBUTING.md" "CONTRIBUTING.md exists" $false

Write-Host "`n"
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "=======" -ForegroundColor Cyan

if ($script:checks.Count -gt 0) {
    Write-Host "`nPassed Checks ($($script:checks.Count)):" -ForegroundColor Green
    foreach ($check in $script:checks) {
        Write-Host "  OK: $($check.Check)" -ForegroundColor Green
        if ($Verbose) {
            Write-Host "      Path: $($check.Path)" -ForegroundColor DarkGreen
        }
    }
}

if ($script:warnings.Count -gt 0) {
    Write-Host "`nWarnings ($($script:warnings.Count)):" -ForegroundColor Yellow
    foreach ($warning in $script:warnings) {
        Write-Host "  WARN: $($warning.Check)" -ForegroundColor Yellow
        Write-Host "        Status: $($warning.Status)" -ForegroundColor DarkYellow
        if ($warning.Optional) {
            Write-Host "        Note: Optional" -ForegroundColor DarkGray
        }
        if ($Verbose) {
            Write-Host "        Path: $($warning.Path)" -ForegroundColor DarkYellow
        }
    }
}

if ($script:errors.Count -gt 0) {
    Write-Host "`nFailed Checks ($($script:errors.Count)):" -ForegroundColor Red
    foreach ($failedCheck in $script:errors) {
        Write-Host "  FAIL: $($failedCheck.Check)" -ForegroundColor Red
        Write-Host "        Path: $($failedCheck.Path)" -ForegroundColor DarkRed
        Write-Host "        Status: $($failedCheck.Status)" -ForegroundColor DarkRed
        if ($failedCheck.Fix) {
            Write-Host "        Fix: $($failedCheck.Fix)" -ForegroundColor Yellow
        }
    }
}

Write-Host "`n"
if ($script:errors.Count -eq 0) {
    Write-Host "Health Check PASSED" -ForegroundColor Green
    Write-Host "Your dotagent setup is working correctly!" -ForegroundColor Green
    if ($script:warnings.Count -gt 0) {
        Write-Host "($($script:warnings.Count) optional items not configured)" -ForegroundColor DarkGray
    }
    exit 0
}

Write-Host "Health Check FAILED" -ForegroundColor Red
Write-Host "$($script:errors.Count) critical issue(s) found. See fixes above." -ForegroundColor Red
exit 1
