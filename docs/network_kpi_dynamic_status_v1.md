# Network KPI Dynamic Status v1

Date: 2026-07-09
Branch: `feature/T429-network-kpi-dynamic-status-v1`

## Goal

`network_kpi_dynamic_status_v1` gives operators and frontend surfaces one
backend-owned answer for whether network KPI proxy values are moving over
simulation time. It is derived from `network_kpi_calibration_v1`.

This contract does not change KPI formulas, route selection, network events,
runtime progression, or Event Kernel behavior.

## Runtime Status Field

The integration demo runtime status exposes:

```text
network_kpi_dynamic_status_v1
```

with status id:

```text
leo_twin.network_kpi_dynamic_status.v1
```

## Runtime Result Package Export

T430 persists the same backend-owned status into runtime result packages as:

```text
network_kpi_dynamic_status_v1.json
```

The standalone artifact has id:

```text
leo_twin.runtime_export_network_kpi_dynamic_status.v1
```

It is included in the result-package recommended files, artifact browser,
review summary, diagnostics bundle, scenario review bundle, scenario review
checklist evidence mapping, and long-term audit index. The export reads
`config_snapshot.status.network_kpi_dynamic_status_v1`; it does not replay
events, recompute metrics, or ask the frontend to infer KPI semantics.

## Status Values

- `DYNAMIC`: at least two network KPIs vary over the observed time series.
- `PARTIALLY_DYNAMIC`: exactly one network KPI varies.
- `FLAT_WITH_ACTIVITY`: traffic/network activity exists, but KPI proxy samples
  are flat.
- `FLAT_NO_ACTIVITY`: KPI proxy samples are flat and no active demand context
  was observed.
- `INSUFFICIENT_SERIES`: fewer than two samples or no positive simulation time
  span.
- `NO_KPI_EVIDENCE`: no observed KPI calibration rows.

## Important Fields

- `sample_count`
- `sim_time_span_s`
- `activity_active`
- `dynamic_status`
- `time_varying_kpi_count`
- `flat_kpi_count`
- `zero_latest_kpi_count`
- `dynamic_metric_names`
- `flat_metric_names`
- `zero_latest_metric_names`
- `items`
- `blocking_reasons`
- `recommended_next_action`
- `status_hash`

Each item includes metric name, runtime summary key, sample key, current
variation status, latest/min/max values, deltas, zero-value note, and a
visibility hint such as `SHOW_DYNAMIC_CHART`, `SHOW_FLAT_REASON`,
`SHOW_ZERO_VALUE_REASON`, or `WAIT_FOR_MORE_SAMPLES`.

## Model Boundary

All fields are flow-level proxy observations. Loss and delay variation are not
packet-level measurements. The summary explains backend evidence and does not
introduce STK, EXATA, AFSIM, DDS, RF propagation, or packet simulation.
