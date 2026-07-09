param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string[]]$AcceptanceConfig = @(
        "configs\acceptance\small_demo_72sat.yaml",
        "configs\acceptance\medium_demo_300sat.yaml",
        "configs\acceptance\scale_demo_1200sat_short.yaml"
    ),
    [int]$BackendPort = 8765,
    [int]$FrontendPort = 5173,
    [int]$TimeoutSeconds = 120,
    [int]$CommandTimeoutSeconds = 600,
    [switch]$SkipBuild,
    [switch]$RunBrowserSmoke,
    [switch]$ExportPackage,
    [switch]$KeepServices,
    [switch]$PlanOnly,
    [switch]$JsonSummary
)

$ErrorActionPreference = "Stop"

$BackendUrl = "http://127.0.0.1:$BackendPort"
$RuntimeStatusUrl = "$BackendUrl/runtime/status"
$ControlUrl = "$BackendUrl/control"
$HelperPath = Join-Path $PSScriptRoot "disposable_acceptance_payload.py"
$RuntimeConfigPaths = @(
    "configs\sees_control.yaml",
    "configs\generated_full_system_demo.json"
)

function Write-Status {
    param([string]$Message)

    if (-not $JsonSummary) {
        Write-Host $Message
    }
}

function Get-PythonCommand {
    if ($env:PYTHON) {
        return $env:PYTHON
    }
    $python = Get-Command "python.exe" -ErrorAction SilentlyContinue
    if ($null -ne $python) {
        return $python.Source
    }
    $python = Get-Command "python" -ErrorAction SilentlyContinue
    if ($null -ne $python) {
        return $python.Source
    }
    $py = Get-Command "py.exe" -ErrorAction SilentlyContinue
    if ($null -ne $py) {
        return "$($py.Source) -3"
    }
    $py = Get-Command "py" -ErrorAction SilentlyContinue
    if ($null -ne $py) {
        return "$($py.Source) -3"
    }
    throw "Python was not found. Install Python 3 or run from a Python-enabled development shell."
}

function Invoke-PythonJson {
    param([string[]]$Arguments)

    $pythonCommand = Get-PythonCommand
    $parts = $pythonCommand.Split(" ")
    $exe = $parts[0]
    $prefixArgs = @()
    if ($parts.Count -gt 1) {
        $prefixArgs = @($parts[1..($parts.Count - 1)])
    }
    $output = & $exe @prefixArgs $HelperPath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python helper failed: $HelperPath $($Arguments -join ' ')"
    }
    return ($output | ConvertFrom-Json)
}

function Get-ScenarioPlan {
    param([string]$ConfigPath)

    return Invoke-PythonJson @(
        "--repo-root",
        $RepoRoot,
        "--config",
        $ConfigPath
    )
}

function Get-StandardPlan {
    return Invoke-PythonJson @(
        "--repo-root",
        $RepoRoot,
        "--standard-plan"
    )
}

function Resolve-RepoPath {
    param([string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return (Resolve-Path -LiteralPath $Path).Path
    }
    return (Resolve-Path -LiteralPath (Join-Path $RepoRoot $Path)).Path
}

function Assert-PathUnderRepo {
    param([string]$Path)

    $resolvedRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
    $resolvedPath = [System.IO.Path]::GetFullPath($Path)
    if (-not $resolvedPath.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to operate outside repo root: $resolvedPath"
    }
}

function Backup-RuntimeConfigPaths {
    $backupRoot = Join-Path $RepoRoot "artifacts\disposable_acceptance\backup"
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
    $entries = @()
    foreach ($relativePath in $RuntimeConfigPaths) {
        $target = Join-Path $RepoRoot $relativePath
        Assert-PathUnderRepo -Path $target
        $backupName = ($relativePath -replace "[\\/]", "__")
        $backupPath = Join-Path $backupRoot $backupName
        $existed = Test-Path -LiteralPath $target
        if ($existed) {
            Copy-Item -LiteralPath $target -Destination $backupPath -Force
        }
        elseif (Test-Path -LiteralPath $backupPath) {
            Remove-Item -LiteralPath $backupPath -Force
        }
        $entries += [ordered]@{
            relative_path = $relativePath
            target_path = $target
            backup_path = $backupPath
            existed = [bool]$existed
        }
    }
    return $entries
}

function Restore-RuntimeConfigPaths {
    param([object[]]$BackupEntries)

    foreach ($entry in $BackupEntries) {
        $target = [string]$entry.target_path
        $backup = [string]$entry.backup_path
        Assert-PathUnderRepo -Path $target
        if ([bool]$entry.existed) {
            Copy-Item -LiteralPath $backup -Destination $target -Force
        }
        elseif (Test-Path -LiteralPath $target) {
            Remove-Item -LiteralPath $target -Force
        }
    }
}

function Invoke-CheckedCommand {
    param(
        [string]$Command,
        [string[]]$Arguments
    )

    $logRoot = Join-Path $RepoRoot "artifacts\disposable_acceptance\commands"
    New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss-fff"
    $safeName = [System.IO.Path]::GetFileNameWithoutExtension($Command)
    if (-not $safeName) {
        $safeName = "command"
    }
    $stdoutPath = Join-Path $logRoot "$timestamp-$safeName.out.log"
    $stderrPath = Join-Path $logRoot "$timestamp-$safeName.err.log"
    $process = Start-Process `
        -FilePath $Command `
        -ArgumentList $Arguments `
        -WorkingDirectory $RepoRoot `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath `
        -PassThru `
        -WindowStyle Hidden
    if (-not $process.WaitForExit($CommandTimeoutSeconds * 1000)) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        $stdoutTail = @()
        $stderrTail = @()
        if (Test-Path -LiteralPath $stdoutPath) {
            $stdoutTail = @(Get-Content -LiteralPath $stdoutPath -Tail 20 -ErrorAction SilentlyContinue)
        }
        if (Test-Path -LiteralPath $stderrPath) {
            $stderrTail = @(Get-Content -LiteralPath $stderrPath -Tail 20 -ErrorAction SilentlyContinue)
        }
        throw "Command timed out after $CommandTimeoutSeconds seconds: $Command $($Arguments -join ' ')`nstdout=$stdoutPath`nstderr=$stderrPath`n$($stdoutTail -join "`n")`n$($stderrTail -join "`n")"
    }
    $process.Refresh()
    $exitCode = $process.ExitCode
    if ($null -eq $exitCode) {
        $exitCode = 0
    }
    $output = @()
    if (Test-Path -LiteralPath $stdoutPath) {
        $output += @(Get-Content -LiteralPath $stdoutPath -ErrorAction SilentlyContinue)
    }
    if (Test-Path -LiteralPath $stderrPath) {
        $output += @(Get-Content -LiteralPath $stderrPath -ErrorAction SilentlyContinue)
    }
    if (-not $JsonSummary) {
        foreach ($line in $output) {
            Write-Host $line
        }
    }
    if ($exitCode -ne 0) {
        $tail = @($output | Select-Object -Last 20) -join "`n"
        throw "Command failed with exit code $exitCode`: $Command $($Arguments -join ' ')`n$tail"
    }
}

function Invoke-ControlAction {
    param(
        [string]$Action,
        [object]$Payload = $null
    )

    $message = [ordered]@{
        type = "RUNTIME_CONTROL"
        action = $Action
    }
    if ($null -ne $Payload) {
        $message.payload = $Payload
    }
    $body = $message | ConvertTo-Json -Depth 80 -Compress
    $response = Invoke-RestMethod `
        -Method Post `
        -Uri $ControlUrl `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec $TimeoutSeconds
    if ($response.type -ne "CONTROL_ACK") {
        throw "$Action returned type '$($response.type)', expected CONTROL_ACK."
    }
    if ($response.ok -ne $true) {
        throw "$Action failed: $($response.error)"
    }
    return $response
}

function Get-RuntimeStatus {
    $response = Invoke-RestMethod -Uri $RuntimeStatusUrl -TimeoutSec $TimeoutSeconds
    if ($response.type -ne "RUNTIME_STATUS") {
        throw "Runtime status type was '$($response.type)', expected RUNTIME_STATUS."
    }
    return $response
}

function Wait-ForRuntimeCondition {
    param(
        [string]$Description,
        [scriptblock]$Condition
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        $status = Get-RuntimeStatus
        if (& $Condition $status) {
            return $status
        }
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $deadline)
    throw "Timed out waiting for runtime condition: $Description"
}

function Invoke-ProductAcceptance {
    param([string]$ConfigPath)

    $args = @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        (Join-Path $PSScriptRoot "verify_product_acceptance.ps1"),
        "-AcceptanceConfig",
        $ConfigPath
    )
    if ($SkipBuild) {
        $args += "-SkipBuild"
    }
    Invoke-CheckedCommand "powershell" $args
}

function Invoke-BrowserSmoke {
    $args = @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        (Join-Path $PSScriptRoot "smoke_browser_acceptance.ps1"),
        "-BackendPort",
        "$BackendPort",
        "-FrontendPort",
        "$FrontendPort",
        "-TimeoutSeconds",
        "$TimeoutSeconds"
    )
    Invoke-CheckedCommand "powershell" $args
}

function Export-RuntimePackage {
    try {
        return Invoke-RestMethod -Uri "$BackendUrl/runtime/export" -TimeoutSec $TimeoutSeconds
    }
    catch {
        return [ordered]@{
            ok = $false
            error = $_.Exception.Message
        }
    }
}

function Invoke-DisposableScenario {
    param([object]$Plan)

    $configPath = Resolve-RepoPath -Path ([string]$Plan.config_path)
    Write-Status "Disposable scenario: $($Plan.scenario_id) ($($Plan.config_path))"
    $resetAck = Invoke-ControlAction -Action "RESET"
    $initializeAck = Invoke-ControlAction `
        -Action "INITIALIZE" `
        -Payload $Plan.initialize_payload
    $initializedStatus = Wait-ForRuntimeCondition `
        -Description "$($Plan.scenario_id) initialized" `
        -Condition {
            param($status)
            $status.status.initialized -eq $true -and `
                [string]$status.status.last_action -eq "INITIALIZE"
        }
    $startAck = Invoke-ControlAction -Action "START"
    $runningStatus = Wait-ForRuntimeCondition `
        -Description "$($Plan.scenario_id) running" `
        -Condition {
            param($status)
            [string]$status.status.lifecycle_state -eq "RUNNING"
        }
    Start-Sleep -Milliseconds 500
    $stopAck = Invoke-ControlAction -Action "STOP"
    $stoppedStatus = Wait-ForRuntimeCondition `
        -Description "$($Plan.scenario_id) stopped" `
        -Condition {
            param($status)
            [string]$status.status.lifecycle_state -eq "STOPPED"
        }

    Invoke-ProductAcceptance -ConfigPath $configPath
    $exportResult = $null
    if ($ExportPackage) {
        $exportResult = Export-RuntimePackage
    }

    return [ordered]@{
        scenario_id = $Plan.scenario_id
        config_path = $Plan.config_path
        expected_satellite_count = $Plan.expectations.satellite_count
        expected_user_count = $Plan.expectations.user_count
        expected_compute_node_count = $Plan.expectations.compute_node_count
        reset_lifecycle = $resetAck.status.lifecycle_state
        initialize_lifecycle = $initializeAck.status.lifecycle_state
        initialized_lifecycle = $initializedStatus.status.lifecycle_state
        running_lifecycle = $runningStatus.status.lifecycle_state
        stopped_lifecycle = $stoppedStatus.status.lifecycle_state
        processed_event_count = $stoppedStatus.status.processed_event_count
        benchmark_acceptance = $Plan.benchmark_acceptance
        export_result = $exportResult
    }
}

Push-Location $RepoRoot
$backupEntries = @()
$servicesStarted = $false
$scriptFailed = $false
try {
    $plans = @()
    if ($AcceptanceConfig.Count -eq 3 -and `
        $AcceptanceConfig[0] -eq "configs\acceptance\small_demo_72sat.yaml" -and `
        $AcceptanceConfig[1] -eq "configs\acceptance\medium_demo_300sat.yaml" -and `
        $AcceptanceConfig[2] -eq "configs\acceptance\scale_demo_1200sat_short.yaml") {
        $standardPlan = Get-StandardPlan
        $plans = @($standardPlan.scenarios)
    }
    else {
        foreach ($configPath in $AcceptanceConfig) {
            $plans += Get-ScenarioPlan -ConfigPath $configPath
        }
    }

    if ($PlanOnly) {
        $benchmark = $null
        if ($plans.Count -gt 0) {
            $benchmark = $plans[0].benchmark_acceptance
        }
        $summary = [ordered]@{
            type = "DISPOSABLE_ACCEPTANCE_PLAN"
            version = "v1"
            backend_url = $BackendUrl
            frontend_url = "http://127.0.0.1:$FrontendPort"
            benchmark_matrix_id = $benchmark.matrix_id
            benchmark_acceptance_binding_id = $benchmark.binding_id
            package_acceptance_report_id = $benchmark.acceptance_report_id
            acceptance_gate_check_id = $benchmark.acceptance_gate_check_id
            scenario_count = $plans.Count
            scenarios = $plans
            runtime_config_drift_paths = $RuntimeConfigPaths
        }
        if ($JsonSummary) {
            $summary | ConvertTo-Json -Depth 80
        }
        else {
            Write-Host "Disposable acceptance plan:"
            foreach ($plan in $plans) {
                Write-Host "  - $($plan.scenario_id): $($plan.config_path)"
            }
        }
        return
    }

    $backupEntries = @(Backup-RuntimeConfigPaths)
    $servicesStarted = $true
    Invoke-CheckedCommand "powershell" @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        (Join-Path $PSScriptRoot "sees_launcher.ps1"),
        "restart",
        "-BackendPort",
        "$BackendPort",
        "-FrontendPort",
        "$FrontendPort",
        "-NoBrowser"
    )

    $results = @()
    foreach ($plan in $plans) {
        $results += Invoke-DisposableScenario -Plan $plan
    }
    if ($RunBrowserSmoke) {
        Invoke-BrowserSmoke
    }

    $summary = [ordered]@{
        type = "DISPOSABLE_ACCEPTANCE_RESULT"
        version = "v1"
        ok = $true
        backend_url = $BackendUrl
        frontend_url = "http://127.0.0.1:$FrontendPort"
        scenario_count = $results.Count
        scenarios = $results
        benchmark_matrix_id = $(if ($plans.Count -gt 0) { $plans[0].benchmark_acceptance.matrix_id } else { $null })
        acceptance_gate_check_id = $(if ($plans.Count -gt 0) { $plans[0].benchmark_acceptance.acceptance_gate_check_id } else { $null })
        runtime_config_restored = $true
        services_left_running = [bool]$KeepServices
    }
    if ($JsonSummary) {
        $summary | ConvertTo-Json -Depth 80
    }
    else {
        Write-Host "Disposable acceptance passed for $($results.Count) scenario(s)."
    }
}
catch {
    $scriptFailed = $true
    $message = $_.Exception.Message
    if ($JsonSummary) {
        [ordered]@{
            type = "DISPOSABLE_ACCEPTANCE_RESULT"
            version = "v1"
            ok = $false
            error = $message
            backend_url = $BackendUrl
            frontend_url = "http://127.0.0.1:$FrontendPort"
            services_left_running = [bool]$KeepServices
        } | ConvertTo-Json -Depth 12
    }
    else {
        Write-Error $message
    }
}
finally {
    if ($backupEntries.Count -gt 0) {
        Restore-RuntimeConfigPaths -BackupEntries $backupEntries
    }
    if ($servicesStarted -and -not $KeepServices) {
        try {
            Invoke-CheckedCommand "powershell" @(
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                (Join-Path $PSScriptRoot "sees_launcher.ps1"),
                "stop",
                "-BackendPort",
                "$BackendPort",
                "-FrontendPort",
                "$FrontendPort",
                "-NoBrowser"
            )
        }
        catch {
            Write-Warning "Failed to stop disposable acceptance services: $($_.Exception.Message)"
        }
    }
    Pop-Location
}
if ($scriptFailed) {
    exit 1
}
