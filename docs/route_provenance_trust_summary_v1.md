# Route Provenance Trust Summary v1

Date: 2026-07-06

## Purpose

Route provenance trust summary v1 gives dashboard and result-review surfaces a
compact backend-owned trust signal for route explanations.

It does not change route calculation. It summarizes the existing
`route_explanation_summary_v1` rows and reports whether the visible route window
has enough explanation, bottleneck, next-hop, path, and context fields for
product interpretation.

## Runtime Status Field

The integration demo runtime status includes:

```text
status.route_provenance_trust_summary_v1
```

The summary is produced beside `route_explanation_summary_v1` by the runtime
observability service.

## Contract Shape

The v1 summary includes:

- `version`
- `trust_id`
- `source`
- `route_model`
- `packet_level_simulation`
- `all_pairs_computation`
- `trust_status`
- route, window, hidden, and unassessed route counts
- available, blocked, over-demand, compute-service, and network-service counts
- explained route count and missing explanation count
- path-context, next-hop, and loss-proxy route counts
- core and context source-field coverage
- bottleneck components and sample route ids
- caveats

## Trust Status

- `COMPLETE_FLOW_LEVEL_ROUTE_PROXY`: current route window has complete core
  explanation fields and no hidden route window.
- `PARTIAL_ROUTE_EXPLANATIONS`: current evidence is usable but partial, usually
  because the route window is paged or context fields are missing.
- `MISSING_ROUTE_EXPLANATIONS`: no assessed route explanation is available.

## Model Boundary

- The route model remains a flow-level route proxy.
- The summary reuses `route_explanation_summary_v1`; it does not recompute
  routes.
- No all-pairs satellite link computation is introduced.
- No packet-level routing or queueing is introduced.
- No Event Kernel behavior is changed.
- No STK, EXATA, AFSIM, or DDS integration is introduced.

## Dashboard Use

The standalone dashboard consumes the summary in the model trust evidence
workspace. Route evidence appears after KPI formula provenance and before
replay/export evidence so users can see whether network path explanations are
currently backed by backend route records.

## Follow-Up

- Add route explanation acceptance checks to benchmark scenarios.
- Link route trust rows to exact route detail endpoints when a selected route
  is available.
- Add a wider route provenance drawer if future routing policies expose
  multiple candidate path alternatives.
