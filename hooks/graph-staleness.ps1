$projectRoot = (Get-Location).Path
$graphPath = Join-Path $projectRoot "graphify-out\GRAPH_REPORT.md"

if (-not (Test-Path -LiteralPath $graphPath)) {
    return
}

$graphTime = (Get-Item -LiteralPath $graphPath).LastWriteTimeUtc
$candidates = Get-ChildItem -LiteralPath $projectRoot -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notlike "*\graphify-out\*" -and
        $_.Extension -in @(".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".md")
    } |
    Sort-Object LastWriteTimeUtc -Descending

if ($candidates.Count -gt 0 -and $candidates[0].LastWriteTimeUtc -gt $graphTime) {
    Write-Output "{""hookSpecificOutput"":{""hookEventName"":""PreToolUse"",""permissionDecision"":""allow""},""systemMessage"":""graphify output may be stale relative to recent source changes. Use graph context carefully or refresh the graph if needed.""}"
}
