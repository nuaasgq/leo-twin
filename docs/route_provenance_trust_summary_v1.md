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

## Benchmark Acceptance

T276 adds route trust acceptance to the standard benchmark scenarios:

- `small_demo_72sat`
- `medium_demo_300sat`
- `scale_demo_1200sat_short`

Each scenario must initialize, start, advance deterministically, and expose a
`route_provenance_trust_summary_v1` that is consistent with
`route_explanation_summary_v1`, uses `FLOW_LEVEL_ROUTE_PROXY`, and keeps
`packet_level_simulation=false` and `all_pairs_computation=false`.

## Result Package Evidence

T277 indexes route trust evidence in runtime result packages:

- `review_summary_v1.json.route_trust`
- `diagnostics_bundle_v1.json.route_trust`

Both fields are derived from
`config_snapshot.status.route_provenance_trust_summary_v1`. The result package
contract does not recompute routes. If an older package lacks the runtime
status field, the diagnostics bundle reports `ROUTE_TRUST_EVIDENCE_MISSING`
while preserving package export compatibility.

T278 adds `route_detail_index_v1.json` so a result package also contains the
exported route explanation window and the route ids referenced by
`route_trust.sample_route_ids`. The index is still a flow-level route evidence
artifact; it does not add packet-level replay, all-pairs computation, or new
route selection behavior.

## Follow-Up

- Link route trust rows in the dashboard export view directly to
  `route_detail_index_v1.json` rows.
- Add a wider route provenance drawer if future routing policies expose
  multiple candidate path alternatives.
