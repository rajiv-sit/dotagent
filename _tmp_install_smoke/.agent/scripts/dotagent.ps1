param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$runAgent = Join-Path $PSScriptRoot "run-agent.ps1"
if (-not (Test-Path -LiteralPath $runAgent)) {
    throw "run-agent.ps1 not found next to dotagent.ps1"
}

& $runAgent @RemainingArgs
