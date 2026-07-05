# Network KPI Provenance v2

Date: 2026-07-05
Provenance id: `leo_twin.network_kpi_provenance.v2`

## Purpose

Network KPI Provenance v2 binds runtime network KPI values to the Network Model
Contract v2. It makes the source of throughput, latency, loss proxy, and
delay-variation proxy explicit for users and frontend displays.

This task does not change KPI formulas. It adds a structured runtime contract
for explaining existing values.

## Runtime Status Field

The integration demo runtime status now includes:

```text
status.network_kpi_provenance_v2
```

The existing field remains for compatibility:

```text
status.network_quality_provenance_v1
```

## Contract Shape

The v2 provenance object includes:

- `version`
- `provenance_id`
- `source`
- `network_model_contract_id`
- `network_model_contract_version`
- `metric_model`
- `packet_level_simulation`
- `proxy_note`
- `provenance_note`
- `kpi_count`
- `kpis`

Each item in `kpis` includes:

- metric name
- runtime summary key
- current value
- observed/missing status
- display name
- owning network layer
- unit
- formula summary
- interpretation
- zero-value semantics
- packet-level flag
- observed dominant source
- zero reason when applicable
- source-field values when present in `metrics_summary`

## KPI Semantics

All v2 KPI items are flow-level proxies:

- throughput is a delivered-flow or available-route throughput estimate;
- latency is completed-flow or available-route flow latency;
- loss is a flow-level quality degradation proxy, not packet loss;
- delay variation is a flow-level delay variation proxy, not packet jitter.

Frontend surfaces should use v2 provenance for product explanations once the
dashboard migrates away from the v1 helper fields.

## Follow-Up

V2-022 should improve time-varying network pressure inputs while preserving this
contract. Dashboard work can then consume `network_kpi_provenance_v2.kpis`
instead of locally mapping individual metric keys.
