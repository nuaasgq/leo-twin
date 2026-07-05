param(
    [ValidateSet("start", "stop", "restart", "status")]
    [string]$Action = "start",
    [int]$BackendPort = 8765,
    [int]$FrontendPort = 5173,
    [switch]$NoBrowser,
    [switch]$VisibleWindows,
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

function Show-Status {
    foreach ($entry in @(
        @{ Name = "Backend"; Port = $BackendPort; Url = $BackendUrl; HealthUrl = $RuntimeStatusUrl },
        @{ Name = "Frontend"; Port = $FrontendPort; Url = $FrontendUrl; HealthUrl = $FrontendHealthUrl }
    )) {
        $processes = @(Get-ListeningProcesses -Port $entry.Port)
        if ($processes.Count -eq 0) {
            Write-Host "$($entry.Name): stopped on port $($entry.Port)"
            continue
        }
        $healthText = "HTTP unhealthy"
        if (Test-HttpEndpoint -Url $entry.HealthUrl -TimeoutSeconds 2) {
            $healthText = "HTTP healthy"
        }
        foreach ($process in $processes) {
            Write-Host "$($entry.Name): running at $($entry.Url) via $($process.ProcessName) [$($process.Id)] - $healthText"
        }
    }
    Write-Host "Launcher logs: $LauncherLogDir"
    Write-Host "Console URL: $FrontendUrl"
    Write-Host "Dashboard URL: $DashboardUrl"
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
}
