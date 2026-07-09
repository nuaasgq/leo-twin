param(
    [ValidateSet("start", "stop", "restart", "status", "health")]
    [string]$Action = "start",
    [int]$BackendPort = 8765,
    [int]$FrontendPort = 5173,
    [switch]$NoBrowser,
    [switch]$VisibleWindows,
    [switch]$JsonSummary,
    [ValidateSet("console", "dashboard")]
    [string]$OpenSurface = "console"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendUrl = "http://127.0.0.1:$BackendPort"
$FrontendUrl = "http://127.0.0.1:$FrontendPort"
$DashboardUrl = "$FrontendUrl/dashboard"
$OpenFrontendUrl = $FrontendUrl
if ($OpenSurface -eq "dashboard") {
    $OpenFrontendUrl = $DashboardUrl
}
$BackendHealthUrl = "$BackendUrl/health"
$RuntimeStatusUrl = "$BackendUrl/runtime/status"
$FrontendHealthUrl = "$FrontendUrl/"
$LauncherLogDir = Join-Path $RepoRoot "artifacts\launcher"
$ScenarioConfigPath = Join-Path $RepoRoot "configs\integration_demo.yaml"
$ControlConfigPath = Join-Path $RepoRoot "configs\sees_control.yaml"
$GeneratedConfigPath = Join-Path $RepoRoot "configs\generated_full_system_demo.json"

function Get-InvocationPrefix {
    param(
        [string[]]$Names,
        [string[]]$ExtraArgs = @()
    )

    foreach ($name in $Names) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($null -ne $command) {
            $quoted = "'" + $command.Source.Replace("'", "''") + "'"
            $argsText = ""
            if ($ExtraArgs.Count -gt 0) {
                $argsText = " " + ($ExtraArgs -join " ")
            }
            return "& $quoted$argsText"
        }
    }
    return $null
}

function Get-PythonInvocation {
    $python = Get-InvocationPrefix -Names @("python.exe", "python")
    if ($null -ne $python) {
        return $python
    }
    $py = Get-InvocationPrefix -Names @("py.exe", "py") -ExtraArgs @("-3")
    if ($null -ne $py) {
        return $py
    }
    throw "Python was not found. Install Python 3 and make sure it is available from PATH."
}

function Get-PnpmInvocation {
    $pnpm = Get-InvocationPrefix -Names @("pnpm.cmd", "pnpm.exe", "pnpm")
    if ($null -ne $pnpm) {
        return $pnpm
    }
    $corepack = Get-InvocationPrefix -Names @("corepack.cmd", "corepack.exe", "corepack") -ExtraArgs @("pnpm")
    if ($null -ne $corepack) {
        return $corepack
    }
    throw "pnpm was not found. Install Node.js and enable pnpm with: corepack enable"
}

function Add-BundledNodeToPath {
    if ($null -ne (Get-Command "node" -ErrorAction SilentlyContinue)) {
        return
    }

    $pnpm = Get-Command "pnpm.cmd" -ErrorAction SilentlyContinue
    if ($null -eq $pnpm) {
        $pnpm = Get-Command "pnpm" -ErrorAction SilentlyContinue
    }
    if ($null -eq $pnpm) {
        return
    }

    $dependenciesBin = Split-Path -Parent $pnpm.Source
    $dependenciesRoot = Split-Path -Parent $dependenciesBin
    $nodeBin = Join-Path $dependenciesRoot "node\bin"
    $nodeExe = Join-Path $nodeBin "node.exe"
    if (-not (Test-Path -LiteralPath $nodeExe)) {
        return
    }

    $entries = @($nodeBin, $dependenciesBin)
    foreach ($entry in $entries) {
        if ($env:PATH -notlike "*$entry*") {
            $env:PATH = "$entry;$env:PATH"
        }
    }
}

function Get-ListeningProcesses {
    param([int]$Port)

    $connections = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
    $processIds = $connections |
        Select-Object -ExpandProperty OwningProcess -Unique |
        Where-Object { $_ -and $_ -ne $PID }
    foreach ($processId in $processIds) {
        Get-Process -Id $processId -ErrorAction SilentlyContinue
    }
}

function Stop-ListeningPort {
    param([int]$Port)

    $processes = @(Get-ListeningProcesses -Port $Port)
    foreach ($process in $processes) {
        Write-Host "Stopping port $Port process: $($process.ProcessName) [$($process.Id)]"
        Stop-Process -Id $process.Id -Force
    }
}

function Wait-ForPort {
    param(
        [string]$Name,
        [int]$Port,
        [int]$TimeoutSeconds
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $processes = @(Get-ListeningProcesses -Port $Port)
        if ($processes.Count -gt 0) {
            Write-Host "$Name is ready on port $Port"
            return $true
        }
        Start-Sleep -Milliseconds 500
    }

    Write-Host "$Name did not become ready on port $Port within $TimeoutSeconds seconds"
    return $false
}

function Test-HttpEndpoint {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 2
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSeconds
        return ([int]$response.StatusCode -ge 200 -and [int]$response.StatusCode -lt 400)
    }
    catch {
        return $false
    }
}

function Wait-ForHttp {
    param(
        [string]$Name,
        [string]$Url,
        [int]$TimeoutSeconds
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $lastError = ""
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
            if ([int]$response.StatusCode -ge 200 -and [int]$response.StatusCode -lt 400) {
                Write-Host "$Name HTTP health check passed at $Url"
                return $true
            }
            $lastError = "HTTP $($response.StatusCode)"
        }
        catch {
            $lastError = $_.Exception.Message
        }
        Start-Sleep -Milliseconds 500
    }

    Write-Host "$Name HTTP health check failed at $Url within $TimeoutSeconds seconds"
    if ($lastError) {
        Write-Host "$Name last health error: $lastError"
    }
    return $false
}

function New-LauncherLogSet {
    param([string]$Name)

    New-Item -ItemType Directory -Force -Path $LauncherLogDir | Out-Null
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    return @{
        Out = Join-Path $LauncherLogDir "$timestamp-$Name.out.log"
        Err = Join-Path $LauncherLogDir "$timestamp-$Name.err.log"
    }
}

function Show-LogTail {
    param(
        [string]$Name,
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }
    $tail = @(Get-Content -Path $Path -Tail 20 -ErrorAction SilentlyContinue)
    if ($tail.Count -eq 0) {
        return
    }
    Write-Host "$Name log tail ($Path):"
    foreach ($line in $tail) {
        Write-Host "  $line"
    }
}

function Get-LatestLauncherLogPath {
    param(
        [string]$Name,
        [string]$Stream
    )

    if (-not (Test-Path -LiteralPath $LauncherLogDir)) {
        return ""
    }
    $match = Get-ChildItem -Path $LauncherLogDir -Filter "*-$Name.$Stream.log" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
    if ($null -eq $match) {
        return ""
    }
    return $match.FullName
}

function New-ServiceHealthEntry {
    param(
        [string]$Service,
        [string]$Role,
        [int]$Port,
        [string]$Url,
        [string]$HealthUrl,
        [string]$LogName
    )

    $processes = @(Get-ListeningProcesses -Port $Port)
    $listening = $processes.Count -gt 0
    $httpHealthy = $false
    if ($listening) {
        $httpHealthy = Test-HttpEndpoint -Url $HealthUrl -TimeoutSeconds 2
    }
    $readiness = "STOPPED"
    if ($listening -and $httpHealthy) {
        $readiness = "READY"
    }
    elseif ($listening) {
        $readiness = "PORT_ONLY"
    }
    return [ordered]@{
        service = $Service
        role = $Role
        port = $Port
        url = $Url
        health_url = $HealthUrl
        listening = $listening
        http_healthy = $httpHealthy
        readiness = $readiness
        process_ids = @($processes | Select-Object -ExpandProperty Id)
        process_names = @($processes | Select-Object -ExpandProperty ProcessName)
        process_count = $processes.Count
        stdout_log = Get-LatestLauncherLogPath -Name $LogName -Stream "out"
        stderr_log = Get-LatestLauncherLogPath -Name $LogName -Stream "err"
    }
}

function Get-LauncherHealthSummary {
    $services = @(
        (New-ServiceHealthEntry `
            -Service "backend" `
            -Role "SEES demo backend" `
            -Port $BackendPort `
            -Url $BackendUrl `
            -HealthUrl $RuntimeStatusUrl `
            -LogName "backend")
        (New-ServiceHealthEntry `
            -Service "frontend" `
            -Role "React observability frontend" `
            -Port $FrontendPort `
            -Url $FrontendUrl `
            -HealthUrl $FrontendHealthUrl `
            -LogName "frontend")
    )
    $readyCount = @($services | Where-Object { $_.readiness -eq "READY" }).Count
    $stoppedCount = @($services | Where-Object { $_.readiness -eq "STOPPED" }).Count
    $overall = "DEGRADED"
    if ($readyCount -eq $services.Count) {
        $overall = "HEALTHY"
    }
    elseif ($stoppedCount -eq $services.Count) {
        $overall = "STOPPED"
    }
    $actions = @()
    if ($overall -eq "HEALTHY") {
        $actions += "Open frontend URL or run smoke_runtime_health.ps1."
    }
    elseif ($overall -eq "STOPPED") {
        $actions += "Run scripts\sees_launcher.ps1 start."
    }
    else {
        $actions += "Inspect artifacts\launcher logs for unhealthy services."
        $actions += "Run scripts\sees_launcher.ps1 restart if stale processes own the ports."
        foreach ($service in $services) {
            if ($service.readiness -eq "PORT_ONLY") {
                $actions += "$($service.service) port is open but HTTP health failed."
            }
            elseif ($service.readiness -eq "STOPPED") {
                $actions += "$($service.service) is not listening on its configured port."
            }
        }
    }
    $blockingServices = @($services | Where-Object { $_.readiness -ne "READY" } | ForEach-Object { $_.service })
    $acceptanceStatus = "BLOCKED"
    $acceptanceNextAction = "Inspect launcher logs and restart unhealthy services."
    if ($blockingServices.Count -eq 0) {
        $acceptanceStatus = "PASS"
        $acceptanceNextAction = "Open the console or dashboard and run the smoke check."
    }
    elseif ($overall -eq "STOPPED") {
        $acceptanceStatus = "STOPPED"
        $acceptanceNextAction = "Run scripts\sees_launcher.ps1 start."
    }
    $oneClickAcceptance = [ordered]@{
        acceptance_id = "leo_twin.launcher_one_click_acceptance.v1"
        status = $acceptanceStatus
        ready = ($acceptanceStatus -eq "PASS")
        required_service_count = $services.Count
        ready_service_count = $readyCount
        blocked_service_count = $blockingServices.Count
        blocking_services = @($blockingServices)
        smoke_command = "scripts\smoke_runtime_health.ps1"
        next_action = $acceptanceNextAction
        criteria = @(
            "backend HTTP health READY",
            "frontend HTTP health READY",
            "launcher logs captured",
            "read-only smoke command available"
        )
    }
    return [ordered]@{
        type = "LAUNCHER_HEALTH"
        health_id = "leo_twin.launcher_health.v2"
        version = "v2"
        overall_status = $overall
        ready_service_count = $readyCount
        service_count = $services.Count
        services = $services
        paths = [ordered]@{
            repo_root = $RepoRoot
            launcher_log_dir = $LauncherLogDir
            config_path = $ScenarioConfigPath
            control_config_path = $ControlConfigPath
            generated_config_path = $GeneratedConfigPath
        }
        console_url = $FrontendUrl
        dashboard_url = $DashboardUrl
        one_click_acceptance_v1 = $oneClickAcceptance
        diagnostic_commands = @(
            "scripts\sees_launcher.ps1 status",
            "scripts\sees_launcher.ps1 status -JsonSummary",
            "scripts\smoke_runtime_health.ps1",
            "scripts\sees_launcher.ps1 restart"
        )
        recommended_actions = $actions
        constraints = [ordered]@{
            event_kernel_frozen = $true
            packet_level_simulation = $false
            forbidden_integrations = @("STK", "EXATA", "AFSIM", "DDS")
        }
    }
}

function Show-Status {
    $summary = Get-LauncherHealthSummary
    if ($JsonSummary) {
        $summary | ConvertTo-Json -Depth 8
        return
    }
    foreach ($entry in $summary.services) {
        if (-not $entry.listening) {
            Write-Host "$($entry.service): stopped on port $($entry.port)"
            continue
        }
        $healthText = "HTTP unhealthy"
        if ($entry.http_healthy) {
            $healthText = "HTTP healthy"
        }
        foreach ($index in 0..([Math]::Max(0, $entry.process_count - 1))) {
            if ($entry.process_count -eq 0) {
                break
            }
            Write-Host "$($entry.service): running at $($entry.url) via $($entry.process_names[$index]) [$($entry.process_ids[$index])] - $healthText"
        }
    }
    Write-Host "Overall launcher health: $($summary.overall_status)"
    Write-Host "Launcher logs: $LauncherLogDir"
    Write-Host "Config path: $ScenarioConfigPath"
    Write-Host "Control config path: $ControlConfigPath"
    Write-Host "Generated config path: $GeneratedConfigPath"
    Write-Host "Console URL: $FrontendUrl"
    Write-Host "Dashboard URL: $DashboardUrl"
    Write-Host "One-click acceptance: $($summary.one_click_acceptance_v1.status)"
    Write-Host "Acceptance next action: $($summary.one_click_acceptance_v1.next_action)"
    Write-Host "Smoke check: .\smoke_leo_twin.bat"
    Write-Host "Dashboard launcher: .\dashboard_leo_twin.bat"
}

function Start-ServiceWindow {
    param(
        [string]$Title,
        [string]$CommandText,
        [string]$StdoutLog,
        [string]$StderrLog
    )

    $escapedRoot = $RepoRoot.Replace("'", "''")
    $escapedTitle = $Title.Replace("'", "''")
    $script = "`$Host.UI.RawUI.WindowTitle = '$escapedTitle'; Set-Location -LiteralPath '$escapedRoot'; $CommandText"
    if ($VisibleWindows) {
        Start-Process powershell -ArgumentList @(
            "-NoExit",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            $script
        ) -WorkingDirectory $RepoRoot
        Write-Host "$Title started in a visible PowerShell window"
        return
    }

    Start-Process powershell -ArgumentList @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        $script
    ) -WorkingDirectory $RepoRoot -WindowStyle Hidden -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog | Out-Null
    Write-Host "$Title started hidden"
    Write-Host "  stdout: $StdoutLog"
    Write-Host "  stderr: $StderrLog"
}

function Start-Sees {
    Add-BundledNodeToPath
    $python = Get-PythonInvocation
    $pnpm = Get-PnpmInvocation

    Stop-ListeningPort -Port $BackendPort
    Stop-ListeningPort -Port $FrontendPort

    $backendLogs = New-LauncherLogSet -Name "backend"
    $frontendLogs = New-LauncherLogSet -Name "frontend"

    Start-ServiceWindow `
        -Title "LEO-Twin Backend :$BackendPort" `
        -CommandText "$python run_demo.py --host 127.0.0.1 --port $BackendPort" `
        -StdoutLog $backendLogs.Out `
        -StderrLog $backendLogs.Err
    Start-Sleep -Seconds 2
    Start-ServiceWindow `
        -Title "LEO-Twin Frontend :$FrontendPort" `
        -CommandText "$pnpm --dir frontend dev -- --host 127.0.0.1 --port $FrontendPort --strictPort" `
        -StdoutLog $frontendLogs.Out `
        -StderrLog $frontendLogs.Err

    $backendReady = Wait-ForPort -Name "Backend" -Port $BackendPort -TimeoutSeconds 120
    $frontendReady = Wait-ForPort -Name "Frontend" -Port $FrontendPort -TimeoutSeconds 60
    if ($backendReady) {
        $backendReady = Wait-ForHttp -Name "Backend" -Url $RuntimeStatusUrl -TimeoutSeconds 120
    }
    if ($frontendReady) {
        $frontendReady = Wait-ForHttp -Name "Frontend" -Url $FrontendHealthUrl -TimeoutSeconds 60
    }

    Write-Host "Backend:  $BackendUrl"
    Write-Host "Frontend: $FrontendUrl"
    Write-Host "Dashboard: $DashboardUrl"
    Write-Host "Backend health:  $RuntimeStatusUrl"
    Write-Host "Frontend health: $FrontendHealthUrl"
    Write-Host "Launcher logs:   $LauncherLogDir"
    if ((-not $NoBrowser) -and $frontendReady) {
        Start-Process $OpenFrontendUrl
    }
    if (-not $backendReady -or -not $frontendReady) {
        Show-LogTail -Name "Backend stdout" -Path $backendLogs.Out
        Show-LogTail -Name "Backend stderr" -Path $backendLogs.Err
        Show-LogTail -Name "Frontend stdout" -Path $frontendLogs.Out
        Show-LogTail -Name "Frontend stderr" -Path $frontendLogs.Err
        throw "LEO-Twin services did not become HTTP healthy. Run scripts\sees_launcher.ps1 status and check logs in $LauncherLogDir."
    }
}

switch ($Action) {
    "start" {
        Start-Sees
    }
    "stop" {
        Stop-ListeningPort -Port $FrontendPort
        Stop-ListeningPort -Port $BackendPort
        Show-Status
    }
    "restart" {
        Stop-ListeningPort -Port $FrontendPort
        Stop-ListeningPort -Port $BackendPort
        Start-Sees
    }
    "status" {
        Show-Status
    }
    "health" {
        Show-Status
    }
}
