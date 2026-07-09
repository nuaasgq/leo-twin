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
status.network_kpi_formula_evidence_v1
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

## Network Quality Proxy Model v2

`leo_twin.network_quality_proxy_model.v2` centralizes the deterministic
flow-level KPI estimate that combines route latency/variation, route blocking,
failed-flow ratio, route loss proxy, congestion pressure, offered capacity,
requested demand, completed-flow capacity, completed-flow latency, and temporal
pressure. `MetricsCollector` now supplies collected state to this model and
publishes the same runtime fields as before. The model does not collect events,
read wall-clock time, replay packets, or call external simulators.

Frontend and export layers should continue to consume backend runtime fields and
provenance rows; they should not reimplement this quality estimate locally.

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

## Calibration Summary v1

`status.network_kpi_calibration_v1` is a backend-owned calibration summary for
the runtime KPI time series. It does not change the formulas. It audits
`kpi_time_series_v1.samples` plus `metrics_summary` and reports whether the
current run shows deterministic movement over simulation time.

The summary includes:

- `sample_count`, `sim_time_start_s`, `sim_time_end_s`, and `sim_time_span_s`;
- `activity_context` for route demand, offered route capacity, recent flow
  count, and available route count;
- `time_driver` fields for simulation-time pressure period, phase, factor,
  loss proxy, and delay-variation proxy;
- one row for each core KPI: throughput, latency, loss proxy, and
  delay-variation proxy;
- first, latest, minimum, maximum, absolute delta, endpoint delta, relative
  delta, zero-latest flag, and variation status for each KPI;
- `calibration_status`: `TIME_VARYING_OBSERVED`,
  `PARTIAL_TIME_VARIATION`, `FLAT_UNDER_ACTIVITY`, `FLAT_NO_ACTIVITY`, or
  `INSUFFICIENT_SERIES`.

This field gives the frontend a backend source of truth for explaining whether
network KPI charts are moving because the model inputs changed, or whether a
flat value is expected because route, flow, and pressure inputs stayed constant.
It remains a deterministic flow-level proxy audit and does not introduce
packet-level loss or jitter.

The standalone dashboard consumes this field directly in the network KPI
section. It renders the calibration status, sample/time span, activity context,
simulation-time driver, flat/latest-zero counts, and per-KPI variation rows.
The same calibration card is indexed into the model-trust evidence workspace so
dashboard users can distinguish a live time-varying run from an insufficient or
flat KPI series without local frontend inference.

## Formula Evidence Summary v1

`status.network_kpi_formula_evidence_v1` is a backend-owned formula evidence
summary that combines `network_kpi_provenance_v2` with
`network_kpi_calibration_v1`. It does not change KPI formulas or simulation
behavior. It reports whether each runtime KPI has:

- a declared runtime summary key and observed current value;
- selected formula inputs for the current observed source;
- observed selected inputs in `metrics_summary`;
- a calibration status showing time-varying, flat, or sample-limited behavior.

The summary includes:

- `evidence_id`: `leo_twin.network_kpi_formula_evidence.v1`;
- `source`: `NETWORK_KPI_PROVENANCE_V2_AND_CALIBRATION_V1`;
- provenance and calibration ids used to build the evidence;
- `metric_model` and `packet_level_simulation` guard fields;
- KPI counts, observed runtime-value counts, selected-input coverage counts,
  time-varying KPI count, and flat KPI count;
- `formula_evidence_status`, such as `FORMULA_AND_TIME_EVIDENCE_READY`,
  `FORMULA_READY_FLAT_SERIES`, `FORMULA_READY_INSUFFICIENT_SERIES`, or
  missing-data statuses;
- one row per KPI with current value, selected inputs, observed source,
  formula summary, selection policy, variation status, and evidence status.

The standalone dashboard consumes this field directly in the network KPI
section and model-trust evidence workspace. It shows whether formulas,
selected inputs, and time-series movement are backed by the backend runtime
state instead of inferring formula credibility in the browser.

## Follow-Up

V2-022 added deterministic time-window pressure inputs while preserving this
contract. T323 added per-KPI `formula_inputs` and `formula_trace` audit fields.
T324 added `network_kpi_benchmark_validation_v1` runtime guardrails.
T325 exports the same guardrail evidence as
`network_kpi_benchmark_validation_v1.json` inside runtime result packages and
binds compact status/hash labels into the dashboard export review surfaces.
T362 adds `network_kpi_calibration_v1` so runtime status can prove whether the
KPI time series is actually moving over simulation time and explain flat
metrics without frontend inference.
T363 binds that backend calibration summary into the standalone dashboard
network KPI panel and model-trust evidence workspace. Future dashboard work can
add filtering or a wider drawer for large
KPI/source-field/input tables if additional KPI families are added.
T369 adds `network_kpi_formula_evidence_v1` so the backend can prove formula
input coverage and time-series evidence together, and binds that summary into
the dashboard network KPI panel and model-trust evidence workspace.
T370 exports the same formula evidence as
`network_kpi_formula_evidence_v1.json` inside runtime result packages and binds
compact status/hash labels into review summary, diagnostics, scenario review,
audit-index, and dashboard export review surfaces.
