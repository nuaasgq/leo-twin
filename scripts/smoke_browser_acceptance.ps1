param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [int]$BackendPort = 8765,
    [int]$FrontendPort = 5173,
    [int]$TimeoutSeconds = 90,
    [string]$BrowserChannel = "",
    [switch]$Headed,
    [switch]$JsonSummary
)

$ErrorActionPreference = "Stop"

function Get-NodeCommand {
    $node = Get-Command "node.exe" -ErrorAction SilentlyContinue
    if ($null -ne $node) {
        return $node.Source
    }
    $pnpm = Get-Command "pnpm.cmd" -ErrorAction SilentlyContinue
    if ($null -eq $pnpm) {
        $pnpm = Get-Command "pnpm" -ErrorAction SilentlyContinue
    }
    if ($null -ne $pnpm) {
        $dependencyRoot = Split-Path -Parent (Split-Path -Parent $pnpm.Source)
        $bundledNode = Join-Path $dependencyRoot "node\bin\node.exe"
        if (Test-Path -LiteralPath $bundledNode) {
            $env:PATH = "$(Split-Path -Parent $bundledNode);$env:PATH"
            return $bundledNode
        }
    }
    throw "node was not found. Install Node.js or run from the bundled Codex dependency runtime."
}

Push-Location $RepoRoot
try {
    $node = Get-NodeCommand
    $script = Join-Path $PSScriptRoot "smoke_browser_acceptance.mjs"
    $frontendUrl = "http://127.0.0.1:$FrontendPort"
    $backendUrl = "http://127.0.0.1:$BackendPort"
    $args = @(
        $script,
        "--frontend-url",
        $frontendUrl,
        "--backend-url",
        $backendUrl,
        "--timeout-seconds",
        "$TimeoutSeconds"
    )
    if ($BrowserChannel) {
        $args += @("--browser-channel", $BrowserChannel)
    }
    if ($Headed) {
        $args += "--headed"
    }
    if ($JsonSummary) {
        $args += "--json"
    }
    & $node @args
    if ($LASTEXITCODE -ne 0) {
        throw "Browser acceptance smoke failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
