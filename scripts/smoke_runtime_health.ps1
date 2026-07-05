param(
    [int]$BackendPort = 8765,
    [int]$FrontendPort = 5173,
    [int]$TimeoutSeconds = 3,
    [switch]$JsonSummary
)

$ErrorActionPreference = "Stop"

$BackendUrl = "http://127.0.0.1:$BackendPort"
$FrontendUrl = "http://127.0.0.1:$FrontendPort"
$DashboardUrl = "$FrontendUrl/dashboard"
$RuntimeStatusUrl = "$BackendUrl/runtime/status"

function Write-Status {
    param([string]$Message)

    if (-not $JsonSummary) {
        Write-Host $Message
    }
}

function Get-HttpResponse {
    param([string]$Url)

    Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSeconds
}

function Assert-HttpOk {
    param(
        [string]$Name,
        [string]$Url
    )

    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $response = Get-HttpResponse -Url $Url
    $timer.Stop()
    $elapsedMs = [math]::Round($timer.Elapsed.TotalMilliseconds, 2)
    $statusCode = [int]$response.StatusCode
    if ($statusCode -lt 200 -or $statusCode -ge 400) {
        throw "$Name returned HTTP $statusCode at $Url"
    }
    Write-Status "$Name OK: $Url ($elapsedMs ms)"
    return @{
        Response = $response
        ElapsedMs = $elapsedMs
    }
}

$runtimeCheck = Assert-HttpOk -Name "Backend runtime status" -Url $RuntimeStatusUrl
$runtimeStatus = $runtimeCheck.Response.Content | ConvertFrom-Json

if ($runtimeStatus.type -ne "RUNTIME_STATUS") {
    throw "Backend runtime status type was '$($runtimeStatus.type)', expected RUNTIME_STATUS."
}
if ($null -eq $runtimeStatus.status) {
    throw "Backend runtime status is missing status object."
}
if (-not $runtimeStatus.status.lifecycle_state) {
    throw "Backend runtime status is missing status.lifecycle_state."
}
if ($null -eq $runtimeStatus.generated_config) {
    throw "Backend runtime status is missing generated_config."
}
if ($null -eq $runtimeStatus.generated_config.backend_summary) {
    throw "Backend runtime status is missing generated_config.backend_summary."
}
$backendSummary = $runtimeStatus.generated_config.backend_summary
if ($null -eq $backendSummary.derived_constellation_summary) {
    throw "Backend runtime status is missing generated_config.backend_summary.derived_constellation_summary."
}
if ($null -eq $backendSummary.traffic_demand_summary) {
    throw "Backend runtime status is missing generated_config.backend_summary.traffic_demand_summary."
}
if ($null -eq $backendSummary.compute_resource_summary) {
    throw "Backend runtime status is missing generated_config.backend_summary.compute_resource_summary."
}

$consoleCheck = Assert-HttpOk -Name "Frontend console" -Url $FrontendUrl
$dashboardCheck = Assert-HttpOk -Name "Frontend dashboard" -Url $DashboardUrl

$summary = [ordered]@{
    ok = $true
    runtime_status_url = $RuntimeStatusUrl
    runtime_status_ms = $runtimeCheck.ElapsedMs
    lifecycle_state = $runtimeStatus.status.lifecycle_state
    simulation_status = $runtimeStatus.status.status
    session_id = $runtimeStatus.status.session_id
    satellite_count = $backendSummary.derived_constellation_summary.satellite_count
    user_count = $runtimeStatus.generated_config.user_count
    constellation_profile = $backendSummary.derived_constellation_summary.profile
    traffic_class = $backendSummary.traffic_demand_summary.traffic_class
    compute_node_count = $backendSummary.compute_resource_summary.compute_node_count
    console_url = $FrontendUrl
    console_ms = $consoleCheck.ElapsedMs
    dashboard_url = $DashboardUrl
    dashboard_ms = $dashboardCheck.ElapsedMs
}

if ($JsonSummary) {
    $summary | ConvertTo-Json -Depth 4
}
else {
    Write-Host "Runtime health smoke passed."
    Write-Host "  lifecycle_state: $($summary.lifecycle_state)"
    Write-Host "  simulation status: $($summary.simulation_status)"
    Write-Host "  constellation: $($summary.satellite_count) satellites / $($summary.user_count) users / $($summary.constellation_profile)"
    Write-Host "  traffic class: $($summary.traffic_class)"
    Write-Host "  compute nodes: $($summary.compute_node_count)"
    Write-Host "  runtime status: $($summary.runtime_status_ms) ms"
    Write-Host "  console: $($summary.console_url) ($($summary.console_ms) ms)"
    Write-Host "  dashboard: $($summary.dashboard_url) ($($summary.dashboard_ms) ms)"
}
