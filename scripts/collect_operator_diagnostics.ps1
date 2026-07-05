param(
    [int]$BackendPort = 8765,
    [int]$FrontendPort = 5173,
    [int]$TimeoutSeconds = 3,
    [string]$OutputRoot = "",
    [switch]$JsonSummary
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not $OutputRoot) {
    $OutputRoot = Join-Path $RepoRoot "artifacts\operator_diagnostics"
}
$BackendUrl = "http://127.0.0.1:$BackendPort"
$BundleId = "operator-diagnostics-" + (Get-Date -Format "yyyyMMdd-HHmmss")
$BundleDir = Join-Path $OutputRoot $BundleId
$LogDir = Join-Path $BundleDir "logs"
New-Item -ItemType Directory -Force -Path $BundleDir | Out-Null
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-JsonArtifact {
    param(
        [string]$Filename,
        [object]$Payload
    )

    $path = Join-Path $BundleDir $Filename
    $Payload | ConvertTo-Json -Depth 64 | Set-Content -Path $path -Encoding UTF8
    return $path
}

function Get-JsonEndpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Filename
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSeconds
        $payload = $response.Content | ConvertFrom-Json
        Write-JsonArtifact -Filename $Filename -Payload $payload | Out-Null
        return @{
            Name = $Name
            Filename = $Filename
            Present = $true
            Error = ""
            Payload = $payload
        }
    }
    catch {
        $errorPayload = [ordered]@{
            type = "DIAGNOSTIC_SECTION_ERROR"
            section = $Name
            url = $Url
            error = $_.Exception.Message
        }
        Write-JsonArtifact -Filename $Filename -Payload $errorPayload | Out-Null
        return @{
            Name = $Name
            Filename = $Filename
            Present = $false
            Error = $_.Exception.Message
            Payload = $null
        }
    }
}

function Get-FileRecord {
    param(
        [string]$Name,
        [string]$Path
    )

    if (-not $Path -or -not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    $source = Get-Item -LiteralPath $Path
    $target = Join-Path $LogDir $source.Name
    Copy-Item -LiteralPath $source.FullName -Destination $target -Force
    $hash = Get-FileHash -LiteralPath $target -Algorithm SHA256
    return [ordered]@{
        name = $Name
        filename = $source.Name
        path = $target
        bytes = $source.Length
        sha256 = "sha256:$($hash.Hash.ToLowerInvariant())"
    }
}

function New-SectionRecord {
    param(
        [string]$Name,
        [string]$Filename,
        [bool]$Present,
        [bool]$Valid,
        [string]$Error
    )

    return [ordered]@{
        name = $Name
        filename = $Filename
        present = $Present
        valid = $Valid
        error = $Error
    }
}

$launcherRaw = & (Join-Path $PSScriptRoot "sees_launcher.ps1") status `
    -BackendPort $BackendPort `
    -FrontendPort $FrontendPort `
    -JsonSummary
$launcherHealth = $launcherRaw | ConvertFrom-Json
Write-JsonArtifact -Filename "launcher_health.json" -Payload $launcherHealth | Out-Null

$runtimeStatus = Get-JsonEndpoint `
    -Name "runtime_status" `
    -Url "$BackendUrl/runtime/status" `
    -Filename "runtime_status.json"
$versionInfo = Get-JsonEndpoint `
    -Name "version_info" `
    -Url "$BackendUrl/runtime/version" `
    -Filename "version_info.json"
$userConfig = Get-JsonEndpoint `
    -Name "user_config_export" `
    -Url "$BackendUrl/scenario/user-config/export" `
    -Filename "user_config_export.json"
$exportCatalog = Get-JsonEndpoint `
    -Name "runtime_export_catalog" `
    -Url "$BackendUrl/runtime/export/catalog" `
    -Filename "runtime_export_catalog.json"

$logFiles = @()
foreach ($service in @($launcherHealth.services)) {
    $stdout = Get-FileRecord -Name "$($service.service)_stdout" -Path ([string]$service.stdout_log)
    if ($null -ne $stdout) {
        $logFiles += $stdout
    }
    $stderr = Get-FileRecord -Name "$($service.service)_stderr" -Path ([string]$service.stderr_log)
    if ($null -ne $stderr) {
        $logFiles += $stderr
    }
}

$sections = [ordered]@{
    launcher_health = New-SectionRecord `
        -Name "launcher_health" `
        -Filename "launcher_health.json" `
        -Present $true `
        -Valid ([string]$launcherHealth.health_id -eq "leo_twin.launcher_health.v2") `
        -Error ""
    runtime_status = New-SectionRecord `
        -Name "runtime_status" `
        -Filename "runtime_status.json" `
        -Present ([bool]$runtimeStatus.Present) `
        -Valid ([bool]$runtimeStatus.Present -and [string]$runtimeStatus.Payload.type -eq "RUNTIME_STATUS") `
        -Error ([string]$runtimeStatus.Error)
    version_info = New-SectionRecord `
        -Name "version_info" `
        -Filename "version_info.json" `
        -Present ([bool]$versionInfo.Present) `
        -Valid ([bool]$versionInfo.Present -and [string]$versionInfo.Payload.summary.version_info_id -eq "leo_twin.version_info.v1") `
        -Error ([string]$versionInfo.Error)
    user_config_export = New-SectionRecord `
        -Name "user_config_export" `
        -Filename "user_config_export.json" `
        -Present ([bool]$userConfig.Present) `
        -Valid ([bool]$userConfig.Present -and [string]$userConfig.Payload.type -eq "USER_CONFIGURATION_EXPORT") `
        -Error ([string]$userConfig.Error)
    runtime_export_catalog = New-SectionRecord `
        -Name "runtime_export_catalog" `
        -Filename "runtime_export_catalog.json" `
        -Present ([bool]$exportCatalog.Present) `
        -Valid ([bool]$exportCatalog.Present -and [string]$exportCatalog.Payload.type -eq "RUNTIME_EXPORT_CATALOG") `
        -Error ([string]$exportCatalog.Error)
}

$presentCount = @($sections.Values | Where-Object { $_.present }).Count
$invalidCount = @($sections.Values | Where-Object { $_.present -and -not $_.valid }).Count
$bundleStatus = "EMPTY"
if ($invalidCount -gt 0) {
    $bundleStatus = "INVALID"
}
elseif ($presentCount -eq $sections.Count -and $logFiles.Count -gt 0) {
    $bundleStatus = "COMPLETE"
}
elseif ($presentCount -gt 0 -or $logFiles.Count -gt 0) {
    $bundleStatus = "PARTIAL"
}

$manifest = [ordered]@{
    type = "OPERATOR_DIAGNOSTICS_BUNDLE"
    bundle_id = "leo_twin.operator_diagnostics_bundle.v1"
    version = "v1"
    bundle_dir = $BundleDir
    bundle_status = $bundleStatus
    sections = $sections
    section_count = $sections.Count
    present_section_count = $presentCount
    log_files = $logFiles
    log_file_count = $logFiles.Count
    source_urls = [ordered]@{
        backend = $BackendUrl
        runtime_status = "$BackendUrl/runtime/status"
        version_info = "$BackendUrl/runtime/version"
        user_config_export = "$BackendUrl/scenario/user-config/export"
        runtime_export_catalog = "$BackendUrl/runtime/export/catalog"
    }
    constraints = [ordered]@{
        event_kernel_frozen = $true
        packet_level_simulation = $false
        forbidden_integrations = @("STK", "EXATA", "AFSIM", "DDS")
    }
}
Write-JsonArtifact -Filename "diagnostics_manifest.json" -Payload $manifest | Out-Null

$summary = [ordered]@{
    ok = $bundleStatus -ne "INVALID"
    bundle_dir = $BundleDir
    bundle_status = $bundleStatus
    present_section_count = $presentCount
    section_count = $sections.Count
    log_file_count = $logFiles.Count
    manifest = Join-Path $BundleDir "diagnostics_manifest.json"
}

if ($JsonSummary) {
    $summary | ConvertTo-Json -Depth 8
}
else {
    Write-Host "Operator diagnostics bundle: $BundleDir"
    Write-Host "  status: $bundleStatus"
    Write-Host "  sections: $presentCount / $($sections.Count)"
    Write-Host "  logs: $($logFiles.Count)"
    Write-Host "  manifest: $($summary.manifest)"
}
