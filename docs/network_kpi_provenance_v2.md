# Network KPI Provenance v2

Date: 2026-07-05
Provenance id: `leo_twin.network_kpi_provenance.v2`

## Purpose

Network KPI Provenance v2 binds runtime network KPI values to the Network Model
Contract v2. It makes the source of throughput, latency, loss proxy, and
delay-variation proxy explicit for users and frontend displays.

The original provenance task added a structured runtime contract for explaining
existing values. T208 extends the flow-level proxy formulas with deterministic
time-window pressure fields while preserving the same provenance contract and
the packet-level exclusion.

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
- `formula_inputs`: backend-auditable formula inputs with current value,
  observed flag, selected-for-current-value flag, role, and selection reason;
- `formula_trace`: backend-owned selection policy, observed source, selected
  source fields, input coverage counts, and missing-input count for the current
  runtime value.

## KPI Semantics

All v2 KPI items are flow-level proxies:

- throughput is a completed-flow or available-route throughput estimate,
  optionally adjusted by deterministic time-window pressure;
- latency is completed-flow or available-route flow latency;
- loss is a flow-level quality degradation proxy, not packet loss;
- delay variation is a flow-level delay variation proxy, not packet jitter.

## Time-Varying Pressure v1

Runtime KPI samples now include deterministic time-window pressure fields:

- `network_quality_time_pressure_period_s`
- `network_quality_time_pressure_phase`
- `network_quality_time_pressure_factor`
- `network_quality_time_pressure_loss_proxy_rate`
- `network_quality_time_pressure_delay_variation_proxy_s`
- `network_quality_time_adjusted_delivered_throughput_mbps`

The time pressure factor uses simulation time, not wall-clock time, and is
derived from existing flow-level demand, completed-flow throughput pressure, and
link congestion pressure. It does not introduce random behavior or packet-level
simulation. The pressure fields are included in Network Model Contract v2 source
fields for effective throughput, effective loss proxy, and effective
delay-variation proxy.

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

The dashboard also renders `network_kpi_provenance_v2.kpis` as a read-only KPI
formula inspector. Each visible row shows the KPI display name, runtime value,
owning layer, observed source, formula summary, source-field coverage, formula
input audit, current selection trace, and zero-value reason or semantics. This
keeps frontend explanations tied to the backend contract instead of local
dashboard guesses.

## Benchmark Validation v1

`status.network_kpi_benchmark_validation_v1` is a backend-owned product
guardrail summary for the current runtime KPI values. It is derived from
`metrics_summary` and `network_kpi_provenance_v2`; it does not change formulas
or simulation behavior. The validation profile is
`FLOW_LEVEL_PROXY_RUNTIME_GUARDRAILS`.

The checks cover:

- packet-level simulation guard;
- runtime KPI value coverage;
- selected formula input coverage;
- non-negative throughput, latency, and delay-variation proxy;
- ratio bounds for loss proxy, route blocking, failed-flow ratio, and
  congestion proxy;
- positive throughput when route demand or available routes exist;
- positive latency when available routes exist.

Validation statuses are `PASS`, `WARN`, `FAIL`, or `INSUFFICIENT_DATA`.
`WARN` highlights product-demonstration issues such as flat zero throughput
under active demand. `FAIL` is reserved for hard guardrail violations such as
out-of-range ratios or packet-level metrics.

The standalone dashboard renders this validation as a compact benchmark card in
the network KPI section and indexes it into the model-trust evidence workspace.

## Follow-Up

V2-022 added deterministic time-window pressure inputs while preserving this
contract. T323 added per-KPI `formula_inputs` and `formula_trace` audit fields.
T324 added `network_kpi_benchmark_validation_v1` runtime guardrails.
Future dashboard work can add filtering or a wider drawer for large
KPI/source-field/input tables if additional KPI families are added.
