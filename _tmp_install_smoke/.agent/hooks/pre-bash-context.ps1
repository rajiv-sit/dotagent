$projectRoot = (Get-Location).Path
$reportPath = Join-Path $projectRoot "graphify-out\\GRAPH_REPORT.md"

if (Test-Path -LiteralPath $reportPath) {
    Write-Output '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"},"systemMessage":"graphify knowledge graph available. Read graphify-out/GRAPH_REPORT.md before broad codebase exploration."}'
}
