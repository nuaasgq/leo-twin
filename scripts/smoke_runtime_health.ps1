param(
    [int]$BackendPort = 8765,
    [int]$FrontendPort = 5173,
    [int]$TimeoutSeconds = 3
)

$ErrorActionPreference = "Stop"

$BackendUrl = "http://127.0.0.1:$BackendPort"
$FrontendUrl = "http://127.0.0.1:$FrontendPort"
$DashboardUrl = "$FrontendUrl/dashboard"
$RuntimeStatusUrl = "$BackendUrl/runtime/status"

function Get-HttpResponse {
    param([string]$Url)

    Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSeconds
}

function Assert-HttpOk {
    param(
        [string]$Name,
        [string]$Url
    )

    $response = Get-HttpResponse -Url $Url
    $statusCode = [int]$response.StatusCode
    if ($statusCode -lt 200 -or $statusCode -ge 400) {
        throw "$Name returned HTTP $statusCode at $Url"
    }
    Write-Host "$Name OK: $Url"
    return $response
}

$runtimeResponse = Assert-HttpOk -Name "Backend runtime status" -Url $RuntimeStatusUrl
$runtimeStatus = $runtimeResponse.Content | ConvertFrom-Json

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

Assert-HttpOk -Name "Frontend console" -Url $FrontendUrl | Out-Null
Assert-HttpOk -Name "Frontend dashboard" -Url $DashboardUrl | Out-Null

Write-Host "Runtime health smoke passed."
Write-Host "  lifecycle_state: $($runtimeStatus.status.lifecycle_state)"
Write-Host "  simulation status: $($runtimeStatus.status.status)"
Write-Host "  console: $FrontendUrl"
Write-Host "  dashboard: $DashboardUrl"
