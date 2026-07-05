param(
    [int]$BackendPort = 8765,
    [int]$TimeoutSeconds = 10,
    [int]$SatelliteCount = 1200,
    [int]$UserCount = 20,
    [int]$ComputeNodeCount = 1200,
    [switch]$JsonSummary
)

$ErrorActionPreference = "Stop"

$BackendUrl = "http://127.0.0.1:$BackendPort"
$RuntimeStatusUrl = "$BackendUrl/runtime/status"
$ControlWebSocketUrl = "ws://127.0.0.1:$BackendPort/control"

function Write-Status {
    param([string]$Message)

    if (-not $JsonSummary) {
        Write-Host $Message
    }
}

function Get-RuntimeStatus {
    $response = Invoke-WebRequest -Uri $RuntimeStatusUrl -UseBasicParsing -TimeoutSec $TimeoutSeconds
    if ([int]$response.StatusCode -lt 200 -or [int]$response.StatusCode -ge 400) {
        throw "Runtime status returned HTTP $($response.StatusCode) at $RuntimeStatusUrl"
    }
    return ($response.Content | ConvertFrom-Json)
}

function Receive-WebSocketJson {
    param(
        [System.Net.WebSockets.ClientWebSocket]$Socket,
        [int]$ReceiveTimeoutSeconds
    )

    $buffer = New-Object byte[] 65536
    $segments = New-Object System.Collections.Generic.List[byte]
    $cts = [System.Threading.CancellationTokenSource]::new(
        [TimeSpan]::FromSeconds($ReceiveTimeoutSeconds)
    )
    try {
        do {
            $result = $Socket.ReceiveAsync(
                [ArraySegment[byte]]::new($buffer),
                $cts.Token
            ).GetAwaiter().GetResult()
            if ($result.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) {
                throw "Control websocket closed before a JSON response was received."
            }
            for ($index = 0; $index -lt $result.Count; $index += 1) {
                $segments.Add($buffer[$index])
            }
        } while (-not $result.EndOfMessage)
    }
    finally {
        $cts.Dispose()
    }

    $text = [System.Text.Encoding]::UTF8.GetString($segments.ToArray())
    return ($text | ConvertFrom-Json)
}

function Send-WebSocketJson {
    param(
        [System.Net.WebSockets.ClientWebSocket]$Socket,
        [object]$Payload
    )

    $json = $Payload | ConvertTo-Json -Depth 32 -Compress
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $Socket.SendAsync(
        [ArraySegment[byte]]::new($bytes),
        [System.Net.WebSockets.WebSocketMessageType]::Text,
        $true,
        [System.Threading.CancellationToken]::None
    ).GetAwaiter().GetResult() | Out-Null
}

function Invoke-ControlAction {
    param(
        [System.Net.WebSockets.ClientWebSocket]$Socket,
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
    Send-WebSocketJson -Socket $Socket -Payload $message
    $ack = Receive-WebSocketJson -Socket $Socket -ReceiveTimeoutSeconds $TimeoutSeconds
    if ($ack.type -ne "CONTROL_ACK") {
        throw "$Action returned message type '$($ack.type)', expected CONTROL_ACK."
    }
    if ($ack.ok -ne $true) {
        throw "$Action failed: $($ack.error)"
    }
    Write-Status "$Action OK: status=$($ack.status.status), lifecycle=$($ack.status.lifecycle_state), sim_time=$($ack.status.current_sim_time)"
    return $ack
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

function New-ScaleSafeInitializePayload {
    return @{
        satellite_count = $SatelliteCount
        user_count = $UserCount
        compute_nodes = $ComputeNodeCount
        duration = 120
        orbit = @{
            update_interval_seconds = 60
            plane_count = 12
            altitude_m = 550000.0
            inclination_deg = 53.0
        }
        traffic_model = @{
            flow_interval_seconds = 60
            task_interval_seconds = 60
            flow_demand_capacity = 25.0
            task_compute_demand = 20.0
            task_data_size = 2.0
        }
        mode = "ACCELERATED"
        speed_factor = 20
    }
}

$socket = [System.Net.WebSockets.ClientWebSocket]::new()
try {
    $socket.ConnectAsync(
        [Uri]::new($ControlWebSocketUrl),
        [System.Threading.CancellationToken]::None
    ).GetAwaiter().GetResult() | Out-Null
    $initialStatus = Receive-WebSocketJson -Socket $socket -ReceiveTimeoutSeconds $TimeoutSeconds
    if ($initialStatus.type -ne "RUNTIME_STATUS") {
        throw "Initial control websocket message type was '$($initialStatus.type)', expected RUNTIME_STATUS."
    }

    $initializeAck = Invoke-ControlAction `
        -Socket $socket `
        -Action "INITIALIZE" `
        -Payload (New-ScaleSafeInitializePayload)
    $startAck = Invoke-ControlAction -Socket $socket -Action "START"

    $runningStatus = Wait-ForRuntimeCondition `
        -Description "simulation time to advance after START" `
        -Condition {
            param($status)
            $status.status.status -eq "RUNNING" -and [double]$status.status.current_sim_time -gt 0
        }
    $runningSimTime = [double]$runningStatus.status.current_sim_time

    $pauseAck = Invoke-ControlAction -Socket $socket -Action "PAUSE"
    Start-Sleep -Milliseconds 750
    $pausedStatus = Get-RuntimeStatus
    if ($pausedStatus.status.status -ne "PAUSED") {
        throw "Runtime status after PAUSE was '$($pausedStatus.status.status)', expected PAUSED."
    }
    $pausedSimTime = [double]$pausedStatus.status.current_sim_time
    Start-Sleep -Milliseconds 750
    $pausedStatusAgain = Get-RuntimeStatus
    $pausedSimTimeAgain = [double]$pausedStatusAgain.status.current_sim_time
    if ($pausedSimTimeAgain -ne $pausedSimTime) {
        throw "Simulation time advanced while paused: $pausedSimTime -> $pausedSimTimeAgain."
    }

    $resumeAck = Invoke-ControlAction -Socket $socket -Action "RESUME"
    $resumedStatus = Wait-ForRuntimeCondition `
        -Description "simulation time to continue after RESUME" `
        -Condition {
            param($status)
            $status.status.status -eq "RUNNING" -and [double]$status.status.current_sim_time -gt $pausedSimTime
        }
    $resumedSimTime = [double]$resumedStatus.status.current_sim_time

    $stopAck = Invoke-ControlAction -Socket $socket -Action "STOP"
    if ($stopAck.status.status -ne "STOPPED") {
        throw "STOP returned status '$($stopAck.status.status)', expected STOPPED."
    }

    $resetAck = Invoke-ControlAction -Socket $socket -Action "RESET"
    if ($resetAck.status.last_action -ne "RESET") {
        throw "RESET returned last_action '$($resetAck.status.last_action)', expected RESET."
    }
    if ($resetAck.status.initialized -ne $false) {
        throw "RESET should leave initialized=false."
    }

    $summary = [ordered]@{
        ok = $true
        backend_url = $BackendUrl
        satellite_count = $SatelliteCount
        user_count = $UserCount
        compute_node_count = $ComputeNodeCount
        initialized_lifecycle = $initializeAck.status.lifecycle_state
        start_sim_time = [double]$startAck.status.current_sim_time
        running_sim_time = $runningSimTime
        paused_sim_time = $pausedSimTime
        resumed_sim_time = $resumedSimTime
        stop_status = $stopAck.status.status
        reset_lifecycle = $resetAck.status.lifecycle_state
    }

    if ($JsonSummary) {
        $summary | ConvertTo-Json -Depth 4
    }
    else {
        Write-Host "Runtime control cycle smoke passed."
        Write-Host "  scenario: $SatelliteCount satellites / $UserCount users / $ComputeNodeCount compute nodes"
        Write-Host "  running sim time: $runningSimTime"
        Write-Host "  paused sim time: $pausedSimTime"
        Write-Host "  resumed sim time: $resumedSimTime"
        Write-Host "  final reset lifecycle: $($resetAck.status.lifecycle_state)"
    }
}
finally {
    if ($socket.State -eq [System.Net.WebSockets.WebSocketState]::Open) {
        $socket.CloseAsync(
            [System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure,
            "smoke complete",
            [System.Threading.CancellationToken]::None
        ).GetAwaiter().GetResult() | Out-Null
    }
    $socket.Dispose()
}
