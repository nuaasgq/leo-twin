param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

$forbiddenPaths = @(
    "configs/generated_full_system_demo.json",
    "configs/sees_control.yaml"
)

Push-Location $RepoRoot
try {
    $staged = @(git diff --cached --name-only)
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to inspect staged files."
    }
    $blocked = @($staged | Where-Object { $forbiddenPaths -contains $_ })
    if ($blocked.Count -gt 0) {
        throw "Runtime/local config files are staged and must be excluded: $($blocked -join ', ')"
    }
    Write-Host "No runtime/local config files are staged."
}
finally {
    Pop-Location
}
