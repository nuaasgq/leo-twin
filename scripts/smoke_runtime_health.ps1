param(
    [int]$BackendPort = 8765,
    [int]$FrontendPort = 5173,
    [int]$TimeoutSeconds = 3,
    [switch]$JsonSummary,
    [int]$ExpectedSatelliteCount = -1,
    [int]$ExpectedUserCount = -1,
    [int]$ExpectedComputeNodeCount = -1,
    [string]$ExpectedConstellationProfile = "",
    [string]$ExpectedTrafficClass = "",
    [string]$ExpectedStandardScenarioId = ""
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

function Test-AllowedForbiddenMarkerContext {
    param(
        [string]$Path,
        [string]$Text
    )

    $allowedPathFragments = @(
        "forbidden_integrations",
        "forbidden_external_integrations",
        "model_boundaries",
        "constraints",
        "assumptions",
        "limitations",
        "guardrails",
        "exclusions"
    )
    foreach ($fragment in $allowedPathFragments) {
        if ($Path -match [regex]::Escape($fragment)) {
            return $true
        }
    }

    $allowedTextPatterns = @(
        "\bno\s+STK\b",
        "\bno\s+EXATA\b",
        "\bno\s+AFSIM\b",
        "\bno\s+DDS\b",
        "\bforbid",
        "\bforbidden\b",
        "\bnot\s+introduced\b",
        "\bremain\s+forbidden\b"
    )
    foreach ($pattern in $allowedTextPatterns) {
        if ($Text -match $pattern) {
            return $true
        }
    }
    return $false
}

function Get-ForbiddenRuntimeMarkerFindings {
    param(
        [object]$Value,
        [string]$Path = "$"
    )

    $findings = @()
    if ($null -eq $Value) {
        return $findings
    }
    if ($Value -is [string]) {
        foreach ($forbiddenName in @("STK", "EXATA", "AFSIM", "DDS")) {
            if ($Value -match "\b$forbiddenName\b" -and `
                -not (Test-AllowedForbiddenMarkerContext -Path $Path -Text $Value)) {
                $findings += "$Path=$Value"
            }
        }
        return $findings
    }
    if ($Value -is [System.Collections.IDictionary]) {
        foreach ($key in @($Value.Keys)) {
            $findings += Get-ForbiddenRuntimeMarkerFindings `
                -Value $Value[$key] `
                -Path "$Path.$key"
        }
        return $findings
    }
    if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) {
        $index = 0
        foreach ($item in $Value) {
            $findings += Get-ForbiddenRuntimeMarkerFindings `
                -Value $item `
                -Path "$Path[$index]"
            $index += 1
        }
        return $findings
    }
    foreach ($property in @($Value.PSObject.Properties)) {
        $findings += Get-ForbiddenRuntimeMarkerFindings `
            -Value $property.Value `
            -Path "$Path.$($property.Name)"
    }
    return $findings
}

$runtimeCheck = Assert-HttpOk -Name "Backend runtime status" -Url $RuntimeStatusUrl
$runtimeStatus = $runtimeCheck.Response.Content | ConvertFrom-Json
$forbiddenRuntimeMarkerFindings = @(
    Get-ForbiddenRuntimeMarkerFindings -Value $runtimeStatus
)
if ($forbiddenRuntimeMarkerFindings.Count -gt 0) {
    throw "Backend runtime status contains forbidden external simulator/runtime marker outside an explicit boundary declaration: $($forbiddenRuntimeMarkerFindings -join '; ')"
}

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
$constellationProfile = [string]$backendSummary.derived_constellation_summary.profile
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
if ($ExpectedConstellationProfile -and $constellationProfile -ne $ExpectedConstellationProfile) {
    throw "Expected constellation_profile=$ExpectedConstellationProfile, got $constellationProfile."
}
if ($ExpectedTrafficClass -and $trafficClass -ne $ExpectedTrafficClass) {
    throw "Expected traffic_class=$ExpectedTrafficClass, got $trafficClass."
}

$standardScenarioAcceptance = $runtimeStatus.status.standard_scenario_acceptance_v2
if ($ExpectedStandardScenarioId) {
    if ($null -eq $standardScenarioAcceptance) {
        throw "Backend runtime status is missing status.standard_scenario_acceptance_v2."
    }
    if ([string]$standardScenarioAcceptance.current_scenario_id -ne $ExpectedStandardScenarioId) {
        throw "Expected standard_scenario_acceptance_v2.current_scenario_id=$ExpectedStandardScenarioId, got $($standardScenarioAcceptance.current_scenario_id)."
    }
    if ($standardScenarioAcceptance.matched_standard_scenario -ne $true) {
        throw "Expected standard_scenario_acceptance_v2.matched_standard_scenario=true."
    }
    if ([string]$standardScenarioAcceptance.acceptance_status -ne "PASS") {
        throw "Expected standard_scenario_acceptance_v2.acceptance_status=PASS, got $($standardScenarioAcceptance.acceptance_status)."
    }
    if (@($standardScenarioAcceptance.missing_runtime_status_fields).Count -ne 0) {
        throw "Expected standard_scenario_acceptance_v2.missing_runtime_status_fields to be empty."
    }
    if (-not (@($standardScenarioAcceptance.result_package_evidence_filenames) -contains "standard_scenario_acceptance_v2.json")) {
        throw "Expected standard_scenario_acceptance_v2 result package evidence to include standard_scenario_acceptance_v2.json."
    }
}

$standardScenarioId = ""
$standardScenarioStatus = ""
if ($null -ne $standardScenarioAcceptance) {
    $standardScenarioId = [string]$standardScenarioAcceptance.current_scenario_id
    $standardScenarioStatus = [string]$standardScenarioAcceptance.acceptance_status
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
    constellation_profile = $constellationProfile
    traffic_class = $trafficClass
    standard_scenario_id = $standardScenarioId
    standard_scenario_acceptance_status = $standardScenarioStatus
    orbit_model = $runtimeStatus.generated_config.orbit_propagation_model
    application_protocol = $runtimeStatus.generated_config.application_protocol
    transport_protocol = $runtimeStatus.generated_config.transport_protocol
    routing_protocol = $runtimeStatus.generated_config.routing_protocol
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
    if ($summary.standard_scenario_id) {
        Write-Host "  standard scenario: $($summary.standard_scenario_id) / $($summary.standard_scenario_acceptance_status)"
    }
    Write-Host "  protocols: $($summary.application_protocol) / $($summary.transport_protocol) / $($summary.routing_protocol)"
    Write-Host "  orbit model: $($summary.orbit_model)"
    Write-Host "  compute nodes: $($summary.compute_node_count) / $($summary.compute_resource_model)"
    Write-Host "  runtime status: $($summary.runtime_status_ms) ms"
    Write-Host "  console: $($summary.console_url) ($($summary.console_ms) ms)"
    Write-Host "  dashboard: $($summary.dashboard_url) ($($summary.dashboard_ms) ms)"
}
