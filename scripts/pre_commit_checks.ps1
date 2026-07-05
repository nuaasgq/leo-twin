param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
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

Push-Location $RepoRoot
try {
    Invoke-CheckedCommand "powershell" @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        (Join-Path $PSScriptRoot "check_no_runtime_config_staged.ps1"),
        "-RepoRoot",
        $RepoRoot
    )
    Invoke-CheckedCommand "powershell" @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        (Join-Path $PSScriptRoot "check_forbidden_runtime_imports.ps1"),
        "-RepoRoot",
        $RepoRoot
    )
    Invoke-CheckedCommand "git" @("diff", "--check")
    Write-Host "Pre-commit checks passed."
}
finally {
    Pop-Location
}
