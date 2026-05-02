param(
    [string]$ProjectRoot = ".",
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-TemplateRoot {
    $projectAgentTemplates = Join-Path (Split-Path -Parent $PSScriptRoot) "templates\root-docs"
    if (Test-Path -LiteralPath $projectAgentTemplates) {
        return $projectAgentTemplates
    }

    $repoTemplateRoot = Join-Path (Split-Path -Parent $PSScriptRoot) "templates\root-docs"
    if (Test-Path -LiteralPath $repoTemplateRoot) {
        return $repoTemplateRoot
    }

    throw "root-docs templates not found next to init-project-docs.ps1"
}

function Get-DocsTemplateRoot {
    $projectAgentTemplates = Join-Path (Split-Path -Parent $PSScriptRoot) "templates\docs"
    if (Test-Path -LiteralPath $projectAgentTemplates) {
        return $projectAgentTemplates
    }

    $repoTemplateRoot = Join-Path (Split-Path -Parent $PSScriptRoot) "templates\docs"
    if (Test-Path -LiteralPath $repoTemplateRoot) {
        return $repoTemplateRoot
    }

    throw "docs templates not found next to init-project-docs.ps1"
}

function Write-ManagedFile {
    param(
        [string]$Source,
        [string]$Destination,
        [switch]$Force
    )

    if ((Test-Path -LiteralPath $Destination) -and -not $Force) {
        Write-Output "Skipped existing file: $Destination"
        return
    }

    $parent = Split-Path -Parent $Destination
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }

    Copy-Item -LiteralPath $Source -Destination $Destination -Force
    Write-Output "Wrote file: $Destination"
}

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$templateRoot = Get-TemplateRoot
$docsTemplateRoot = Get-DocsTemplateRoot
$designRoot = Join-Path $root "docs\design"
$docsRoot = Join-Path $root "docs"

foreach ($name in @("Requirement.md", "Architecture.md", "HLD.md", "DD.md", "milestone.md")) {
    Write-ManagedFile -Source (Join-Path $templateRoot $name) -Destination (Join-Path $designRoot $name) -Force:$Force
}

Write-ManagedFile -Source (Join-Path $docsTemplateRoot "dotagent-user-guide.html") -Destination (Join-Path $docsRoot "dotagent-user-guide.html") -Force:$Force

Write-Output ""
Write-Output "Project document bootstrap complete."
Write-Output "Project root: $root"
Write-Output "Design docs path: $designRoot"
Write-Output "User guide: $(Join-Path $docsRoot "dotagent-user-guide.html")"
