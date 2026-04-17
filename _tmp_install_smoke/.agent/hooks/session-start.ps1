$projectRoot = (Get-Location).Path
$branch = ""

try {
    $branch = (git rev-parse --abbrev-ref HEAD 2>$null)
} catch {
    $branch = ""
}

$docs = @("CONTEXT.md", "PLAN.md", "Requirement.md", "Architecture.md", "HLD.md", "DD.md", "milestone.md") |
    Where-Object { Test-Path -LiteralPath (Join-Path $projectRoot $_) }

$graphReport = Test-Path -LiteralPath (Join-Path $projectRoot "graphify-out\GRAPH_REPORT.md")
$obsidian = Test-Path -LiteralPath (Join-Path $projectRoot ".obsidian")

$parts = @()
if ($branch) { $parts += "branch=$branch" }
$parts += "docs=$($docs.Count)"
$parts += "graphify=" + $(if ($graphReport) { "present" } else { "missing" })
$parts += "obsidian=" + $(if ($obsidian) { "present" } else { "missing" })

Write-Output ("dotagent session: " + ($parts -join " | "))

