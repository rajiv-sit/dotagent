$projectRoot = (Get-Location).Path
$docs = @("CONTEXT.md", "PLAN.md", "Requirement.md", "Architecture.md", "HLD.md", "DD.md", "milestone.md") |
    Where-Object { Test-Path -LiteralPath (Join-Path $projectRoot $_) }

if ($docs.Count -gt 0) {
    $docList = $docs -join ", "
    Write-Output "{""hookSpecificOutput"":{""hookEventName"":""PreToolUse"",""permissionDecision"":""allow""},""systemMessage"":""Root design docs detected: $docList. Read them directly before broad implementation or exploration.""}"
}
