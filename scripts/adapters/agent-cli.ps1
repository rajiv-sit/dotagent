Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AssistantCommand {
    $cmd = Get-Command agent.cmd -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $shim = Get-Command agent -ErrorAction SilentlyContinue
    if ($shim) {
        return $shim.Source
    }

    return $null
}
