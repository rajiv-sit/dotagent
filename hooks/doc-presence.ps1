$projectRoot = (Get-Location).Path
$docs = @("CONTEXT.md", "PLAN.md", "docs\\design\\Requirement.md", "docs\\design\\Architecture.md", "docs\\design\\HLD.md", "docs\\design\\DD.md", "docs\\design\\milestone.md") |
    Where-Object { Test-Path -LiteralPath (Join-Path $projectRoot $_) }

if ($docs.Count -gt 0) {
    $docList = $docs -join ", "
    Write-Output "{""hookSpecificOutput"":{""hookEventName"":""PreToolUse"",""permissionDecision"":""allow""},""systemMessage"":""Project context docs detected: $docList. Read them directly before broad implementation or exploration.""}"
}
