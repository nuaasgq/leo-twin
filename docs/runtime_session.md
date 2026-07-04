# Runtime Session / Control Plane v1

## Purpose

Runtime lifecycle control lives outside the Event Kernel. The Event Kernel
remains the only owner of simulation time, event ordering, queue dispatch, and
module callbacks. The runtime layer only creates a kernel instance, schedules
scenario initialization events, and drives it through the public
`kernel.run(until_time=...)`, `kernel.stop()`, and `kernel.get_current_time()`
surface.

This keeps replay determinism and event ordering frozen while giving the
backend a product control surface for UI and automation.

## Runtime Package

Reusable runtime services live in `src/leo_twin/runtime`:

- `SimulationSession` owns one run instance, config, kernel reference,
  processed events, status, and current snapshot.
- `SimulationClockController` maps wall-clock policy to requested simulation
  targets without mutating kernel time.
- `RuntimeStatus` reports lifecycle state, mode, speed, current sim time,
  wall-clock start time, processed event count, queued event count when
  available, and last error.
- `ControlProtocol` parses runtime commands and returns deterministic ACK/NACK
  responses.
- `SnapshotStream` projects processed events into throttled frontend snapshots.
- `SimulationController` is a thin facade for adapters such as the demo server.
- `SimulationSessionRegistry` owns multiple sessions by stable `session_id`.
- `StreamBuffer` provides bounded cursor reads for events and snapshots.
- `SessionAdvanceLoop` advances a session from a backend-owned loop and
  publishes stream buffers.

## Session States

The session lifecycle states are:

- `UNINITIALIZED`: no kernel has been created.
- `INITIALIZED`: a fresh kernel exists and scenario initialization events are
  scheduled.
- `RUNNING`: external control is advancing the kernel.
- `PAUSED`: no further kernel advancement is requested.
- `STOPPED`: the session has called `kernel.stop()` and must be reset before a
  new run.
- `COMPLETED`: the session has run all queued events.
- `ERROR`: a runtime operation failed; `last_error` reports the reason.

The demo status keeps the legacy `status` field (`STOPPED`, `RUNNING`,
`PAUSED`) for frontend compatibility and adds `lifecycle_state` for the product
session lifecycle.

## Simulation Modes

`REAL_TIME` maps wall-clock elapsed seconds to the same simulation-time delta.

`ACCELERATED` maps wall-clock elapsed seconds by `speed_factor`. For example,
a speed factor of `10` requests ten simulation seconds per wall-clock second.

`PAUSED` returns the current kernel time as the target, so the session does not
advance.

Deterministic replay mode avoids wall-clock dependency for tests and replay.
It advances by explicit control steps. The kernel still determines the actual
accepted time based on queued events and `until_time`.

## Control Protocol

Supported commands:

- `INITIALIZE`
- `START`
- `PAUSE`
- `RESUME`
- `STOP`
- `RESET`
- `SET_SPEED`
- `SET_MODE`
- `REQUEST_STATUS`
- `REQUEST_SNAPSHOT`

Messages may use the product shape:

```json
{"command":"SET_SPEED","payload":{"speed_factor":10}}
```

The demo adapter also accepts the existing frontend shape:

```json
{"type":"RUNTIME_CONTROL","action":"START","payload":{}}
```

Every command returns a deterministic ACK/NACK:

```json
{"type":"CONTROL_ACK","ok":true,"command":"START","status":{}}
```

Failures are returned as NACKs rather than uncaught exceptions:

```json
{"type":"CONTROL_ACK","ok":false,"command":"UNKNOWN","status":{},"error":"..."}
```

## Frontend Interaction Model

The demo frontend can keep using:

- `GET /runtime/status`
- `WS /control`
- `WS /stream/state`
- `WS /stream/events`

The server remains an adapter. It delegates runtime status, lifecycle control,
event access, and snapshot access to the reusable runtime session layer, then
adds demo-specific config and generated-scenario metadata.

`SnapshotStream` keeps the frontend independent from raw internal event volume.
It applies processed events to a projector and emits snapshots at a configured
event interval and optional wall-clock frequency.

## Runtime Session v2

The v2 runtime layer adds three reusable backend primitives.

`SimulationSessionRegistry` is a process-local registry for multiple
`SimulationSession` instances. It creates, registers, lists, looks up, and
removes sessions without changing the Event Kernel or scenario modules.

`StreamBuffer` is a bounded cursor stream. Each published item gets a
monotonic sequence number. A reader passes its last cursor and receives items
after that cursor plus `next_cursor`. If a reader falls behind the retained
window, the response reports `overflow=true` and `dropped_count`.

`SessionAdvanceLoop` is the server-side driver for long-running sessions. It
ticks a session while the session lifecycle is `RUNNING`, publishes new
processed events into an event stream, and publishes projected snapshots into a
snapshot stream. The loop does not inspect or reorder kernel internals; it only
calls the session, which drives the kernel through public methods.

The integration demo still exposes the legacy websocket array streams, but the
adapter now also has cursor batch methods over the same reusable stream
buffers. This lets future HTTP/WebSocket handlers keep long-lived clients
independent from raw event flood and apply backpressure deterministically.

In the demo server, the existing stream paths keep their WebSocket behavior.
When called as plain HTTP GET, they also expose cursor batches:

- `GET /stream/events?cursor=0&limit=100`
- `GET /stream/state?cursor=0&limit=20`

The response includes `items`, `cursor`, `next_cursor`, `overflow`, and
`dropped_count`.

## Replay And Determinism

Replay determinism is preserved by these rules:

- Runtime services do not modify Event Kernel internals.
- Runtime services do not reorder events.
- The kernel is driven only through public `run(until_time=...)` calls.
- Deterministic replay mode advances by explicit control steps instead of wall
  time.
- Snapshot projection consumes the processed event sequence in kernel order.

Given the same scenario config, runtime config, deterministic step sequence,
and module implementations, status and snapshot sequences are reproducible.

Cursor streams do not affect replay determinism. Dropping old retained stream
items is a transport/backpressure concern only; the session keeps its own
processed event sequence and current snapshot.

## Demo-Specific Boundary

The integration demo still owns:

- demo YAML loading and SEES config translation;
- writing `configs/sees_control.yaml` and
  `configs/generated_full_system_demo.json`;
- construction of orbit/network/compute/metrics modules for the demo scenario;
- demo-specific frontend JSON projection.

The reusable runtime layer owns lifecycle, status, command ACK/NACK behavior,
clock policy, snapshot throttling, and kernel driving.
