# Validate All Markdown Links
# Checks that all internal references in markdown files resolve to existing files
# Usage: .\validate-links.ps1
# Output: [OK] All links valid or [BROKEN] Broken links found

param(
    [string]$Path = ".",
    [switch]$Verbose = $false,
    [switch]$Fix = $false
)

$validLinks = @()
$brokenLinks = @()
$externalLinks = @()
$projectRoot = (Get-Item -Path $Path).FullName

Write-Host "Markdown Link Validator" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host "Scanning: $projectRoot`n" -ForegroundColor Gray

function Resolve-LinkPath {
    param(
        [string]$LinkPath,
        [string]$FromFile
    )

    $pathOnly = $LinkPath -split '#' | Select-Object -First 1

    if ($pathOnly -match '^https?://' -or $pathOnly -match '^mailto:') {
        return @{ Type = "External"; Path = $pathOnly }
    }

    $fromDir = Split-Path -Parent $FromFile
    $resolvedPath = Join-Path -Path $fromDir -ChildPath $pathOnly | Resolve-Path -ErrorAction SilentlyContinue

    if ($resolvedPath) {
        return @{ Type = "Valid"; Path = $resolvedPath; Original = $LinkPath }
    }

    return @{ Type = "Broken"; Path = $pathOnly; Original = $LinkPath }
}

function Extract-MarkdownLinks {
    param([string]$FilePath)

    $content = Get-Content -Path $FilePath -Raw
    if ($null -eq $content) {
        $content = ""
    }

    $pattern = '!?\[([^\]]*)\]\(([^)]+)\)'
    $matches = [regex]::Matches([string]$content, $pattern)

    $links = @()
    foreach ($match in $matches) {
        $links += @{
            Text = $match.Groups[1].Value
            Url = $match.Groups[2].Value
            FullMatch = $match.Value
        }
    }

    return $links
}

Write-Host "1. Scanning markdown files..." -ForegroundColor Yellow
$markdownFiles = Get-ChildItem -Path $projectRoot -Filter "*.md" -Recurse -ErrorAction SilentlyContinue
Write-Host "Found $($markdownFiles.Count) markdown files`n" -ForegroundColor Gray

Write-Host "2. Validating links..." -ForegroundColor Yellow
foreach ($file in $markdownFiles) {
    $relativePath = $file.FullName -replace [regex]::Escape($projectRoot), "."

    if ($Verbose) {
        Write-Host "  Checking: $relativePath" -ForegroundColor Gray
    }

    $links = Extract-MarkdownLinks -FilePath $file.FullName
    foreach ($link in $links) {
        $resolution = Resolve-LinkPath -LinkPath $link.Url -FromFile $file.FullName

        if ($resolution.Type -eq "External") {
            $externalLinks += @{
                From = $relativePath
                Url = $resolution.Path
                Text = $link.Text
            }
        } elseif ($resolution.Type -eq "Valid") {
            $validLinks += @{
                From = $relativePath
                To = $resolution.Path -replace [regex]::Escape($projectRoot), "."
                Text = $link.Text
            }
        } else {
            $brokenLinks += @{
                From = $relativePath
                Url = $resolution.Path
                Original = $link.Original
                Text = $link.Text
            }
            Write-Host "    BROKEN: $($link.Url)" -ForegroundColor Red
        }
    }
}

Write-Host "`n"
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "=======" -ForegroundColor Cyan
Write-Host "`nValid Links: $($validLinks.Count)" -ForegroundColor Green
Write-Host "External Links: $($externalLinks.Count)" -ForegroundColor Cyan
Write-Host "Broken Links: $($brokenLinks.Count)" -ForegroundColor Red

if ($brokenLinks.Count -gt 0) {
    Write-Host "`nBroken Links Details:" -ForegroundColor Red
    foreach ($broken in $brokenLinks) {
        Write-Host "  BROKEN: $($broken.From)" -ForegroundColor Red
        Write-Host "    Link: $($broken.Url)" -ForegroundColor DarkRed
        Write-Host "    Text: $($broken.Text)" -ForegroundColor DarkRed
        Write-Host ""
    }
    exit 1
}

Write-Host "`nAll links are valid!" -ForegroundColor Green
exit 0
