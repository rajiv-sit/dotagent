# dotcodex Health Check Script
# Validates that your dotcodex Codex project setup is correct
# Usage: .\health-check.ps1
# Output: All checks passed or Issues found (with descriptions)

param(
    [switch]$Verbose = $false,
    [switch]$Fix = $false
)

# Script state
$checks = @()
$warnings = @()
$errors = @()
$projectRoot = (Get-Item -Path $PSScriptRoot).Parent.Parent.FullName

Write-Host "dotcodex Health Check" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host "Project: $projectRoot`n"

# === Helper Functions ===

function Test-FileExists {
    param(
        [string]$Path,
        [string]$Description,
        [bool]$Critical = $true
    )
    
    $relativePath = $Path -replace [regex]::Escape($projectRoot), "."
    
    if (Test-Path $Path) {
        $checks += @{ Status = "OK"; Check = $Description; Path = $relativePath }
        return $true
    } else {
        if ($Critical) {
            $errors += @{ Check = $Description; Path = $relativePath; Status = "File not found"; Fix = "Create $relativePath" }
        } else {
            $warnings += @{ Check = $Description; Path = $relativePath; Status = "File not found"; Optional = $true }
        }
        return $false
    }
}

function Test-DirectoryExists {
    param(
        [string]$Path,
        [string]$Description,
        [bool]$Critical = $true
    )
    
    $relativePath = $Path -replace [regex]::Escape($projectRoot), "."
    
    if (Test-Path $Path -PathType Container) {
        $checks += @{ Status = "OK"; Check = $Description; Path = $relativePath }
        return $true
    } else {
        if ($Critical) {
            $errors += @{ Check = $Description; Path = $relativePath; Status = "Directory not found"; Fix = "Create $relativePath" }
        } else {
            $warnings += @{ Check = $Description; Path = $relativePath; Status = "Directory not found"; Optional = $true }
        }
        return $false
    }
}

function Test-FileNotEmpty {
    param(
        [string]$Path,
        [string]$Description
    )
    
    $relativePath = $Path -replace [regex]::Escape($projectRoot), "."
    
    if ((Test-Path $Path) -and (Get-Item $Path).Length -gt 0) {
        $checks += @{ Status = "OK"; Check = $Description; Path = $relativePath }
        return $true
    } else {
        $errors += @{ Check = $Description; Path = $relativePath; Status = "File is empty"; Fix = "Populate $relativePath with content" }
        return $false
    }
}

function Test-ValidJson {
    param(
        [string]$Path,
        [string]$Description
    )
    
    $relativePath = $Path -replace [regex]::Escape($projectRoot), "."
    
    if (!(Test-Path $Path)) {
        return $false
    }
    
    try {
        $content = Get-Content -Path $Path -Raw
        $null = $content | ConvertFrom-Json
        $checks += @{ Status = "OK"; Check = $Description; Path = $relativePath }
        return $true
    } catch {
        $errors += @{ Check = $Description; Path = $relativePath; Status = "Invalid JSON"; Fix = "Fix JSON syntax in $relativePath"; Detail = $_.Exception.Message }
        return $false
    }
}

function Test-FileContains {
    param(
        [string]$Path,
        [string]$Pattern,
        [string]$Description
    )
    
    $relativePath = $Path -replace [regex]::Escape($projectRoot), "."
    
    if (!(Test-Path $Path)) {
        return $false
    }
    
    $content = Get-Content -Path $Path -Raw
    if ($content -match $Pattern) {
        $checks += @{ Status = "OK"; Check = $Description; Path = $relativePath }
        return $true
    } else {
        $warnings += @{ Check = $Description; Path = $relativePath; Status = "Pattern not found: $Pattern"; Optional = $true }
        return $false
    }
}

# === Health Checks ===

Write-Host "1. Core Documentation Files" -ForegroundColor Yellow
$t1 = Test-FileNotEmpty "$projectRoot\AGENTS.md" "AGENTS.md exists and has content"
$t2 = Test-FileNotEmpty "$projectRoot\CONTEXT.md" "CONTEXT.md exists and has content"
$t3 = Test-FileNotEmpty "$projectRoot\PLAN.md" "PLAN.md exists and has content"

Write-Host "`n2. Codex Configuration" -ForegroundColor Yellow
$t4 = Test-DirectoryExists "$projectRoot\.codex" ".codex directory exists"
$t5 = Test-FileExists "$projectRoot\.codex\agents\default-agent.md" "Default agent profile exists"
$t6 = Test-DirectoryExists "$projectRoot\.codex\rules" "Rules directory exists"
$t7 = Test-FileExists "$projectRoot\hooks.json" "hooks.json exists" $false

Write-Host "`n3. Rules and Standards" -ForegroundColor Yellow
$rulesDir = "$projectRoot\.codex\rules"
if (Test-Path $rulesDir) {
    $ruleCount = @(Get-ChildItem -Path $rulesDir -Filter "*.md" | Measure-Object).Count
    if ($ruleCount -gt 0) {
        $checks += @{ Status = "OK"; Check = "Rules found"; Path = ".codex/rules ($ruleCount files)" }
        $t8 = $true
    } else {
        $warnings += @{ Check = "Rules found"; Path = ".codex/rules"; Status = "No rule files (.md)"; Optional = $true }
        $t8 = $false
    }
} else {
    $t8 = $false
}

Write-Host "`n4. Agents" -ForegroundColor Yellow
$agentsDir = "$projectRoot\.codex\agents"
if (Test-Path $agentsDir) {
    $agentCount = @(Get-ChildItem -Path $agentsDir -Filter "*.md" | Measure-Object).Count
    if ($agentCount -gt 0) {
        $checks += @{ Status = "OK"; Check = "Agents found"; Path = ".codex/agents ($agentCount files)" }
        $t9 = $true
    } else {
        $errors += @{ Check = "Agents found"; Path = ".codex/agents"; Status = "No agent files (.md)"; Fix = "Add default-agent.md and other agents" }
        $t9 = $false
    }
} else {
    $t9 = $false
}

Write-Host "`n5. Skills" -ForegroundColor Yellow
$skillsDir = "$projectRoot\.codex\skills"
if (Test-Path $skillsDir) {
    $skillCount = @(Get-ChildItem -Path $skillsDir -Directory | Measure-Object).Count
    if ($skillCount -gt 0) {
        $checks += @{ Status = "OK"; Check = "Skills found"; Path = ".codex/skills ($skillCount directories)" }
        $t10 = $true
    } else {
        $warnings += @{ Check = "Skills found"; Path = ".codex/skills"; Status = "No skill directories"; Optional = $true }
        $t10 = $false
    }
} else {
    $t10 = $false
}

Write-Host "`n6. Hooks" -ForegroundColor Yellow
$hooksDir = "$projectRoot\.codex\hooks"
if (Test-Path $hooksDir) {
    $hookCount = @(Get-ChildItem -Path $hooksDir -Filter "*.ps1" | Measure-Object).Count
    if ($hookCount -gt 0) {
        $checks += @{ Status = "OK"; Check = "Hooks found"; Path = ".codex/hooks ($hookCount scripts)" }
        $t11 = $true
    } else {
        $warnings += @{ Check = "Hooks found"; Path = ".codex/hooks"; Status = "No PowerShell hooks (.ps1)"; Optional = $true }
        $t11 = $false
    }
} else {
    $t11 = $false
}

Write-Host "`n7. Scripts" -ForegroundColor Yellow
$scriptsDir = "$projectRoot\.codex\scripts"
if (Test-Path $scriptsDir) {
    $scriptCount = @(Get-ChildItem -Path $scriptsDir -Filter "*.ps1" | Measure-Object).Count
    if ($scriptCount -gt 0) {
        $checks += @{ Status = "OK"; Check = "Scripts found"; Path = ".codex/scripts ($scriptCount files)" }
        $t12 = $true
    } else {
        $warnings += @{ Check = "Scripts found"; Path = ".codex/scripts"; Status = "No PowerShell scripts (.ps1)"; Optional = $true }
        $t12 = $false
    }
} else {
    $t12 = $false
}

Write-Host "`n8. Documentation" -ForegroundColor Yellow
$t13 = Test-DirectoryExists "$projectRoot\docs" "Documentation directory exists" $false
$t14 = Test-FileExists "$projectRoot\README.md" "README.md exists"
$t15 = Test-FileExists "$projectRoot\CONTRIBUTING.md" "CONTRIBUTING.md exists" $false

# === Summary ===

Write-Host "`n" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "=======" -ForegroundColor Cyan

# Show all checks
if ($checks.Count -gt 0) {
    Write-Host "`nPassed Checks ($($checks.Count)):" -ForegroundColor Green
    foreach ($check in $checks) {
        Write-Host "  OK: $($check.Check)" -ForegroundColor Green
        if ($Verbose) {
            Write-Host "      Path: $($check.Path)" -ForegroundColor DarkGreen
        }
    }
}

# Show warnings
if ($warnings.Count -gt 0) {
    Write-Host "`nWarnings ($($warnings.Count)):" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
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

# Show errors
if ($errors.Count -gt 0) {
    Write-Host "`nFailed Checks ($($errors.Count)):" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  FAIL: $($error.Check)" -ForegroundColor Red
        Write-Host "        Path: $($error.Path)" -ForegroundColor DarkRed
        Write-Host "        Status: $($error.Status)" -ForegroundColor DarkRed
        if ($error.Fix) {
            Write-Host "        Fix: $($error.Fix)" -ForegroundColor Yellow
        }
        if ($error.Detail) {
            Write-Host "        Detail: $($error.Detail)" -ForegroundColor DarkRed
        }
    }
}

# Final status
Write-Host "`n" -ForegroundColor Cyan
if ($errors.Count -eq 0) {
    Write-Host "Health Check PASSED" -ForegroundColor Green
    Write-Host "Your dotcodex setup is working correctly!" -ForegroundColor Green
    if ($warnings.Count -gt 0) {
        Write-Host "($($warnings.Count) optional items not configured)" -ForegroundColor DarkGray
    }
    exit 0
} else {
    Write-Host "Health Check FAILED" -ForegroundColor Red
    Write-Host "$($errors.Count) critical issue(s) found. See fixes above." -ForegroundColor Red
    exit 1
}
