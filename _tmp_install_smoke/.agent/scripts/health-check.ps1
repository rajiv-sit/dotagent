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
$null = Test-FileExists "$projectRoot\.agent\agents\default-agent.md" "Default agent profile exists"
$null = Test-DirectoryExists "$projectRoot\.agent\rules" "Rules directory exists"
$null = Test-FileExists "$projectRoot\hooks.json" "hooks.json exists" $false

Write-Host "`n3. Rules and Standards" -ForegroundColor Yellow
$rulesDir = "$projectRoot\.agent\rules"
if (Test-Path $rulesDir) {
    $ruleCount = @(Get-ChildItem -Path $rulesDir -Filter "*.md" | Measure-Object).Count
    if ($ruleCount -gt 0) {
        $script:checks += @{ Status = "OK"; Check = "Rules found"; Path = ".agent/rules ($ruleCount files)" }
    } else {
        $script:warnings += @{ Check = "Rules found"; Path = ".agent/rules"; Status = "No rule files (.md)"; Optional = $true }
    }
}

Write-Host "`n4. Agents" -ForegroundColor Yellow
$agentsDir = "$projectRoot\.agent\agents"
if (Test-Path $agentsDir) {
    $agentCount = @(Get-ChildItem -Path $agentsDir -Filter "*.md" | Measure-Object).Count
    if ($agentCount -gt 0) {
        $script:checks += @{ Status = "OK"; Check = "Agents found"; Path = ".agent/agents ($agentCount files)" }
    } else {
        $script:errors += @{ Check = "Agents found"; Path = ".agent/agents"; Status = "No agent files (.md)"; Fix = "Add default-agent.md and other agents" }
    }
}

Write-Host "`n5. Skills" -ForegroundColor Yellow
$skillsDir = "$projectRoot\.agent\skills"
if (Test-Path $skillsDir) {
    $skillCount = @(Get-ChildItem -Path $skillsDir -Directory | Measure-Object).Count
    if ($skillCount -gt 0) {
        $script:checks += @{ Status = "OK"; Check = "Skills found"; Path = ".agent/skills ($skillCount directories)" }
    } else {
        $script:warnings += @{ Check = "Skills found"; Path = ".agent/skills"; Status = "No skill directories"; Optional = $true }
    }
}

Write-Host "`n6. Hooks" -ForegroundColor Yellow
$hooksDir = "$projectRoot\.agent\hooks"
if (Test-Path $hooksDir) {
    $hookCount = @(Get-ChildItem -Path $hooksDir -Filter "*.ps1" | Measure-Object).Count
    if ($hookCount -gt 0) {
        $script:checks += @{ Status = "OK"; Check = "Hooks found"; Path = ".agent/hooks ($hookCount scripts)" }
    } else {
        $script:warnings += @{ Check = "Hooks found"; Path = ".agent/hooks"; Status = "No PowerShell hooks (.ps1)"; Optional = $true }
    }
}

Write-Host "`n7. Scripts" -ForegroundColor Yellow
$scriptsDir = "$projectRoot\.agent\scripts"
if (Test-Path $scriptsDir) {
    $scriptCount = @(Get-ChildItem -Path $scriptsDir -Filter "*.ps1" | Measure-Object).Count
    if ($scriptCount -gt 0) {
        $script:checks += @{ Status = "OK"; Check = "Scripts found"; Path = ".agent/scripts ($scriptCount files)" }
    } else {
        $script:warnings += @{ Check = "Scripts found"; Path = ".agent/scripts"; Status = "No PowerShell scripts (.ps1)"; Optional = $true }
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
    foreach ($error in $script:errors) {
        Write-Host "  FAIL: $($error.Check)" -ForegroundColor Red
        Write-Host "        Path: $($error.Path)" -ForegroundColor DarkRed
        Write-Host "        Status: $($error.Status)" -ForegroundColor DarkRed
        if ($error.Fix) {
            Write-Host "        Fix: $($error.Fix)" -ForegroundColor Yellow
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
