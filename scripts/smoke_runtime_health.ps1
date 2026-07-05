param(
    [int]$BackendPort = 8765,
    [int]$FrontendPort = 5173,
    [int]$TimeoutSeconds = 3,
    [switch]$JsonSummary,
    [int]$ExpectedSatelliteCount = -1,
    [int]$ExpectedUserCount = -1,
    [int]$ExpectedComputeNodeCount = -1,
    [string]$ExpectedTrafficClass = ""
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

function Assert-FrontendShell {
    param(
        [string]$Name,
        [object]$Check
    )

    if ($Check.Response.Content -notmatch 'id="root"') {
        throw "$Name did not return the expected frontend application shell."
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
if ([string]$backendSummary.compute_resource_summary.resource_model -ne "ComputeResourceVector") {
    throw "Backend compute resource summary resource_model was '$($backendSummary.compute_resource_summary.resource_model)', expected ComputeResourceVector."
}

$consoleCheck = Assert-HttpOk -Name "Frontend console" -Url $FrontendUrl
$dashboardCheck = Assert-HttpOk -Name "Frontend dashboard" -Url $DashboardUrl
Assert-FrontendShell -Name "Frontend console" -Check $consoleCheck
Assert-FrontendShell -Name "Frontend dashboard" -Check $dashboardCheck

$satelliteCount = [int]$backendSummary.derived_constellation_summary.satellite_count
$userCount = [int]$runtimeStatus.generated_config.user_count
$computeNodeCount = [int]$backendSummary.compute_resource_summary.compute_node_count
$trafficClass = [string]$backendSummary.traffic_demand_summary.traffic_class

if ($ExpectedSatelliteCount -ge 0 -and $satelliteCount -ne $ExpectedSatelliteCount) {
    throw "Expected satellite_count=$ExpectedSatelliteCount, got $satelliteCount."
}
if ($ExpectedUserCount -ge 0 -and $userCount -ne $ExpectedUserCount) {
    throw "Expected user_count=$ExpectedUserCount, got $userCount."
}
if ($ExpectedComputeNodeCount -ge 0 -and $computeNodeCount -ne $ExpectedComputeNodeCount) {
    throw "Expected compute_node_count=$ExpectedComputeNodeCount, got $computeNodeCount."
}
if ($ExpectedTrafficClass -and $trafficClass -ne $ExpectedTrafficClass) {
    throw "Expected traffic_class=$ExpectedTrafficClass, got $trafficClass."
}

$summary = [ordered]@{
    ok = $true
    runtime_status_url = $RuntimeStatusUrl
    runtime_status_ms = $runtimeCheck.ElapsedMs
    lifecycle_state = $runtimeStatus.status.lifecycle_state
    simulation_status = $runtimeStatus.status.status
    session_id = $runtimeStatus.status.session_id
    satellite_count = $satelliteCount
    user_count = $userCount
    constellation_profile = $backendSummary.derived_constellation_summary.profile
    traffic_class = $trafficClass
    compute_node_count = $computeNodeCount
    compute_resource_model = $backendSummary.compute_resource_summary.resource_model
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
    Write-Host "  compute nodes: $($summary.compute_node_count) / $($summary.compute_resource_model)"
    Write-Host "  runtime status: $($summary.runtime_status_ms) ms"
    Write-Host "  console: $($summary.console_url) ($($summary.console_ms) ms)"
    Write-Host "  dashboard: $($summary.dashboard_url) ($($summary.dashboard_ms) ms)"
}
