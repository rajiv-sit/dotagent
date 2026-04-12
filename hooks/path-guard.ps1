$projectRoot = (Get-Location).Path
$highSignal = @("src", "app", "tests", "docs", "backend", "frontend") |
    Where-Object { Test-Path -LiteralPath (Join-Path $projectRoot $_) }

if ($highSignal.Count -gt 0) {
    $list = $highSignal -join ", "
    Write-Output "{""hookSpecificOutput"":{""hookEventName"":""PreToolUse"",""permissionDecision"":""allow""},""systemMessage"":""Prefer focused exploration in likely project folders first: $list. Avoid whole-repo recursive listing unless necessary.""}"
}
