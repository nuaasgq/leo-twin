param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

function Invoke-CheckedCommand {
    param(
        [string]$Command,
        [string[]]$Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE`: $Command $($Arguments -join ' ')"
    }
}

$pnpm = Get-Command "pnpm.cmd" -ErrorAction SilentlyContinue
if ($null -eq $pnpm) {
    $pnpm = Get-Command "pnpm" -ErrorAction SilentlyContinue
}
if ($null -eq $pnpm) {
    throw "pnpm was not found. Install Node.js and pnpm, or run this script from an environment where pnpm is on PATH."
}

Push-Location $RepoRoot
try {
    & (Join-Path $PSScriptRoot "verify_frontend_assets.ps1") -RepoRoot $RepoRoot

    Invoke-CheckedCommand $pnpm.Source @(
        "--dir",
        "frontend",
        "test",
        "--",
        "satelliteVisuals.test.ts",
        "globeVisualPolicy.test.ts",
        "visualLayerLimits.test.ts",
        "orbitTrackRenderer.test.ts",
        "countryOverlays.test.ts",
        "dataPanel.test.ts",
        "runtimeContractFixture.test.ts",
        "appSurface.test.ts"
    )

    if (-not $SkipBuild) {
        Invoke-CheckedCommand $pnpm.Source @("--dir", "frontend", "build")
    }

    Write-Host "Frontend visual verification passed."
}
finally {
    Pop-Location
}
