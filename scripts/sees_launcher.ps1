param(
    [ValidateSet("start", "stop", "restart", "status")]
    [string]$Action = "start",
    [int]$BackendPort = 8765,
    [int]$FrontendPort = 5173,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendUrl = "http://127.0.0.1:$BackendPort"
$FrontendUrl = "http://127.0.0.1:$FrontendPort"

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

function Show-Status {
    foreach ($entry in @(
        @{ Name = "Backend"; Port = $BackendPort; Url = $BackendUrl },
        @{ Name = "Frontend"; Port = $FrontendPort; Url = $FrontendUrl }
    )) {
        $processes = @(Get-ListeningProcesses -Port $entry.Port)
        if ($processes.Count -eq 0) {
            Write-Host "$($entry.Name): stopped on port $($entry.Port)"
            continue
        }
        foreach ($process in $processes) {
            Write-Host "$($entry.Name): running at $($entry.Url) via $($process.ProcessName) [$($process.Id)]"
        }
    }
}

function Start-ServiceWindow {
    param(
        [string]$Title,
        [string]$CommandText
    )

    $escapedRoot = $RepoRoot.Replace("'", "''")
    $escapedTitle = $Title.Replace("'", "''")
    $script = "`$Host.UI.RawUI.WindowTitle = '$escapedTitle'; Set-Location -LiteralPath '$escapedRoot'; $CommandText"
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        $script
    ) -WorkingDirectory $RepoRoot
}

function Start-Sees {
    $python = Get-PythonInvocation
    $pnpm = Get-PnpmInvocation

    Stop-ListeningPort -Port $BackendPort
    Stop-ListeningPort -Port $FrontendPort

    Start-ServiceWindow `
        -Title "LEO-Twin Backend :$BackendPort" `
        -CommandText "$python run_demo.py"
    Start-Sleep -Seconds 2
    Start-ServiceWindow `
        -Title "LEO-Twin Frontend :$FrontendPort" `
        -CommandText "$pnpm --dir frontend dev"

    Write-Host "Backend:  $BackendUrl"
    Write-Host "Frontend: $FrontendUrl"
    if (-not $NoBrowser) {
        Start-Process $FrontendUrl
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
