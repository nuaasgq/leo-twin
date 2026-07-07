param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [switch]$SkipRuntimeSmoke,
    [switch]$SkipBuild,
    [string]$AcceptanceConfig = "",
    [int]$ExpectedSatelliteCount = -1,
    [int]$ExpectedUserCount = -1,
    [int]$ExpectedComputeNodeCount = -1,
    [string]$ExpectedConstellationProfile = "",
    [string]$ExpectedTrafficClass = "",
    [switch]$RunControlCycleSmoke,
    [int]$ControlSmokeSatelliteCount = 1200,
    [int]$ControlSmokeUserCount = 20,
    [int]$ControlSmokeComputeNodeCount = 1200,
    [switch]$RunBrowserSmoke,
    [string]$BrowserSmokeChannel = "",
    [switch]$BrowserSmokeHeaded
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

function Get-AcceptanceExpectations {
    param(
        [string]$Python,
        [string]$ConfigPath
    )

    $script = @'
import json
import sys
from pathlib import Path

import yaml

path = Path(sys.argv[1])
data = yaml.safe_load(path.read_text(encoding='utf-8'))
scenario = data.get('scenario', {})
network = data.get('network', {})
application_protocol = str(network.get('application_protocol', ''))
traffic_class = 'COMPUTE_SERVICE' if application_protocol == 'TASK_OFFLOAD_FLOW' else ''
print(json.dumps({
    'satellite_count': int(scenario.get('satellite_count', -1)),
    'user_count': int(scenario.get('user_count', -1)),
    'compute_node_count': int(scenario.get('compute_nodes', -1)),
    'constellation_profile': str(scenario.get('constellation_profile', '')),
    'traffic_class': traffic_class,
}, sort_keys=True))
'@
    $output = & $Python -c $script $ConfigPath
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to read acceptance config: $ConfigPath"
    }
    return ($output | ConvertFrom-Json)
}

Push-Location $RepoRoot
try {
    $env:PYTHONPATH = "src;."
    $python = Get-PythonCommand
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
    if ($AcceptanceConfig) {
        $resolvedConfig = Resolve-Path -LiteralPath $AcceptanceConfig
        $expectations = Get-AcceptanceExpectations -Python $python -ConfigPath $resolvedConfig.Path
        if ($ExpectedSatelliteCount -lt 0) {
            $ExpectedSatelliteCount = [int]$expectations.satellite_count
        }
        if ($ExpectedUserCount -lt 0) {
            $ExpectedUserCount = [int]$expectations.user_count
        }
        if ($ExpectedComputeNodeCount -lt 0) {
            $ExpectedComputeNodeCount = [int]$expectations.compute_node_count
        }
        if (-not $ExpectedConstellationProfile -and $expectations.constellation_profile) {
            $ExpectedConstellationProfile = [string]$expectations.constellation_profile
        }
        if (-not $ExpectedTrafficClass -and $expectations.traffic_class) {
            $ExpectedTrafficClass = [string]$expectations.traffic_class
        }
    }
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
        $smokeArgs = @(
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            (Join-Path $PSScriptRoot "smoke_runtime_health.ps1")
        )
        if ($ExpectedSatelliteCount -ge 0) {
            $smokeArgs += @("-ExpectedSatelliteCount", "$ExpectedSatelliteCount")
        }
        if ($ExpectedUserCount -ge 0) {
            $smokeArgs += @("-ExpectedUserCount", "$ExpectedUserCount")
        }
        if ($ExpectedComputeNodeCount -ge 0) {
            $smokeArgs += @("-ExpectedComputeNodeCount", "$ExpectedComputeNodeCount")
        }
        if ($ExpectedConstellationProfile) {
            $smokeArgs += @("-ExpectedConstellationProfile", $ExpectedConstellationProfile)
        }
        if ($ExpectedTrafficClass) {
            $smokeArgs += @("-ExpectedTrafficClass", $ExpectedTrafficClass)
        }
        Invoke-CheckedCommand "powershell" $smokeArgs
    }

    if ($RunControlCycleSmoke) {
        Invoke-CheckedCommand "powershell" @(
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            (Join-Path $PSScriptRoot "smoke_runtime_control_cycle.ps1"),
            "-SatelliteCount",
            "$ControlSmokeSatelliteCount",
            "-UserCount",
            "$ControlSmokeUserCount",
            "-ComputeNodeCount",
            "$ControlSmokeComputeNodeCount"
        )
    }

    if ($RunBrowserSmoke) {
        $browserSmokeArgs = @(
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            (Join-Path $PSScriptRoot "smoke_browser_acceptance.ps1")
        )
        if ($BrowserSmokeChannel) {
            $browserSmokeArgs += @("-BrowserChannel", $BrowserSmokeChannel)
        }
        if ($BrowserSmokeHeaded) {
            $browserSmokeArgs += "-Headed"
        }
        Invoke-CheckedCommand "powershell" $browserSmokeArgs
    }

    Write-Host "Product acceptance verification passed."
}
finally {
    Pop-Location
}
