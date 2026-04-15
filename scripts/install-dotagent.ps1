param(
    [string]$ProjectRoot = ".",
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$installPack = Join-Path $PSScriptRoot "install-pack.ps1"
if (-not (Test-Path -LiteralPath $installPack)) {
    throw "install-pack.ps1 not found next to install-dotagent.ps1"
}

& $installPack -ProjectRoot $ProjectRoot -Force:$Force
