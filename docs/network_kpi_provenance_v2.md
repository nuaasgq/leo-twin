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
status.network_kpi_credibility_v1
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

## Credibility Summary v1

`status.network_kpi_credibility_v1` is a compact backend-owned coverage and
trust summary derived from `network_kpi_provenance_v2`. It does not change KPI
formulas. It reports:

- `credibility_status`: `COMPLETE_FLOW_LEVEL_PROXY`,
  `PARTIAL_RUNTIME_VALUES`, `MISSING_RUNTIME_VALUES`, or
  `INVALID_PACKET_LEVEL_METRIC`;
- observed and missing KPI counts;
- packet-level metric count, which must remain zero under the current product
  constraints;
- flow-level proxy metric count;
- zero-valued KPI count and zero-explanation coverage;
- source-field coverage from `metrics_summary`;
- missing metric names and zero-valued KPI names that lack explicit
  explanation;
- caveats suitable for user-facing model trust displays.

This field gives the frontend a single backend-derived signal for whether the
network KPI panel is fully backed by runtime values or should be presented as a
partial/missing proxy view.

The standalone dashboard consumes this field directly in the network KPI panel.
It renders a compact trust card from backend values rather than inferring KPI
credibility locally. The card reports status, KPI coverage, source-field
coverage, proxy/packet guard counts, zero-value explanation coverage, missing
metric names, and backend caveats.

## Follow-Up

V2-022 should improve time-varying network pressure inputs while preserving this
contract. A later dashboard pass can render the full
`network_kpi_provenance_v2.kpis` table instead of only the compact
`network_kpi_credibility_v1` trust summary.
