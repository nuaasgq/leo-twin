param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [switch]$SkipRuntimeSmoke,
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

function Get-PythonCommand {
    $python = Get-Command "python.exe" -ErrorAction SilentlyContinue
    if ($null -ne $python) {
        return $python.Source
    }
    $python = Get-Command "python" -ErrorAction SilentlyContinue
    if ($null -ne $python) {
        return $python.Source
    }
    throw "Python was not found. Install Python 3 or run from a Python-enabled development shell."
}

Push-Location $RepoRoot
try {
    $env:PYTHONPATH = "src;."
    $python = Get-PythonCommand
    Invoke-CheckedCommand $python @(
        "-m",
        "pytest",
        "tests/unit/test_metrics_module.py::test_service_latency_history_includes_sorted_component_timeline",
        "tests/integration/test_compute_service_lifecycle.py",
        "-q"
    )

    $visualArgs = @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        (Join-Path $PSScriptRoot "verify_frontend_visuals.ps1"),
        "-RepoRoot",
        $RepoRoot
    )
    if ($SkipBuild) {
        $visualArgs += "-SkipBuild"
    }
    Invoke-CheckedCommand "powershell" $visualArgs

    if (-not $SkipRuntimeSmoke) {
        Invoke-CheckedCommand "powershell" @(
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            (Join-Path $PSScriptRoot "smoke_runtime_health.ps1")
        )
    }

    Write-Host "Product acceptance verification passed."
}
finally {
    Pop-Location
}
