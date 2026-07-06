# Result Package Contract v1

Date: 2026-07-06
Branch: `feature/T220-result-package-export-v1`

`result_package_contract_v1` documents and validates the runtime result package
shape used by the SEES integration demo backend. It does not change Event
Kernel behavior and does not introduce packet-level replay.

## Contract Source

Python API:

```python
from leo_twin.services.result_package_contract import (
    build_runtime_export_diagnostics_bundle_v1,
    result_package_contract_v1_to_dict,
    summarize_result_package_record_v1,
)

contract = result_package_contract_v1_to_dict()
```

Contract id:

```text
leo_twin.result_package_contract.v1
```

## Export Routes

The integration demo backend already exposes:

- `GET /runtime/export`
- `GET /runtime/export/archive`
- `GET /runtime/export/catalog`
- `GET /runtime/export/packages/{package_id}`
- `GET /runtime/export/packages/{package_id}/manifest`
- `GET /runtime/export/packages/{package_id}/review-summary`
- `GET /runtime/export/packages/{package_id}/files/{filename}`

The persisted catalog file is:

```text
runtime_export_catalog_v1.json
```

## Required Files

Every v1 runtime export package must include:

| File | Format | Content |
| --- | --- | --- |
| `config_snapshot.json` | JSON | runtime status, applied SEES config, generated backend config |
| `events.jsonl` | JSONL | deterministically ordered processed runtime events |
| `metrics.csv` | CSV | sampled metric records and KPI observations |
| `summary.json` | JSON | metrics summary and aggregate runtime counters |
| `manifest.json` | JSON | runtime reproducibility manifest with stable hashes |

Current runtime exports may also include additional deterministic artifacts.
`service_lifecycle_trace_v2.json` is emitted as an optional observability file
for offline communication-compute service lifecycle review.
`route_detail_index_v1.json` is emitted as an optional route evidence artifact.
It preserves the exported `route_explanation_summary_v1` window, route trust
sample ids, indexed route ids, and compact flow-level route explanation rows
for offline route trust review.
`review_summary_v1.json` is emitted as a user-readable review entry point for
the package. It summarizes scenario scale, runtime progress, reproducibility
hashes, artifact coverage, route trust evidence, and review readiness without
adding wall-clock data.
`diagnostics_bundle_v1.json` is emitted as a deterministic operator-facing
diagnostics index. It summarizes package completeness, required/recommended
artifact health, route trust evidence, reproducibility hashes, model boundaries,
findings, and recommended next actions.
`scenario_review_bundle_v1.json` is emitted as a deterministic operator-facing
review entry point. It binds the effective user configuration evidence,
scenario scale, runtime progress, manifest hashes, review summary hash,
diagnostics hash, audit-index filename, model boundaries, and recommended
review order into one compact JSON artifact.

## Review Summary

The review summary artifact has type:

```text
RUNTIME_EXPORT_REVIEW_SUMMARY_V1
```

The summary id is:

```text
leo_twin.runtime_export_review_summary.v1
```

It reports:

- package id and package directory;
- scenario seed, satellite count, user count, compute-node count, and duration;
- runtime lifecycle state, simulation time, processed events, and queued events;
- route trust evidence derived from
  `config_snapshot.status.route_provenance_trust_summary_v1`;
- route comparison review metadata for package-vs-live route diagnostics;
- manifest id/hash plus config and generated-config hashes;
- required artifact coverage and missing required filenames;
- review notes explaining which artifacts support reproducibility review.

The persisted route
`GET /runtime/export/packages/{package_id}/review-summary` serves the
`review_summary_v1.json` artifact from the package catalog.
The standalone dashboard export catalog also links each package row to this
review summary so users can inspect it without constructing the URL manually.
The dashboard also loads the selected package's review summary as a read-only
card, showing review readiness, scenario scale, runtime progress, manifest
hashes, and artifact coverage alongside compare and restore-preflight context.
The same dashboard view derives artifact health rows from the backend export
catalog and selected review summary, showing required/optional status,
present/missing state, file size, short SHA-256 hash, and direct file links
without hardcoding artifact semantics in the frontend.

The manifest id must be:

```text
leo_twin.runtime_reproducibility_manifest.v1
```

New runtime exports also carry a unified reproducibility boundary object:

```text
leo_twin.runtime_export_reproducibility_boundary.v1
```

The boundary is written to `manifest.json` as
`runtime_export_reproducibility_boundary_v1`, copied into
`config_snapshot.status`, and surfaced by both `review_summary_v1.json` and
`diagnostics_bundle_v1.json`. It records the backend-owned review boundary for
the package: deterministic artifact evidence is available, restore is
configuration-only, compare covers config and generated config, reads use
persisted artifacts only, and the package does not perform live event replay
restore, recomputation on read, package mutation on read, packet capture,
packet-level simulation, or external simulator artifact binding. The manifest
hash is calculated after the boundary is attached, while the boundary hash is
reported separately so review and diagnostics artifacts can cross-check the
same boundary without a circular manifest hash dependency.

Package compare and restore-preflight summaries also expose
`runtime_export_boundary_alignment_v1`. This object is generated by the backend
from the persisted package boundary and the actual compare/preflight scope. It
reports the package boundary hash, optional current boundary hash, restore,
compare, read, and preflight scope alignment, forbidden replay/recompute/
mutation/packet/external-simulator flags, deterministic warnings, and an
`alignment_hash`. The field is read-only evidence for API consumers and
dashboard users; it does not replay events, mutate packages, recompute model
state, or execute a restore.

## Route Detail Index

The route detail index artifact has type:

```text
RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_V1
```

The index id is:

```text
leo_twin.runtime_export_route_detail_index.v1
```

It reports:

- package id and package directory;
- route model and model-boundary flags;
- route summary counters copied from
  `config_snapshot.status.route_explanation_summary_v1`;
- route detail export policy copied from
  `config_snapshot.status.runtime_export_route_detail_policy_v1`;
- route trust summary copied from
  `config_snapshot.status.route_provenance_trust_summary_v1`;
- route comparison review metadata, including compared fields, live-runtime
  requirement, status reasons, and no-recompute/no-replay boundaries;
- exported route ids, route-trust sample route ids, indexed sample ids, and
  missing sample ids;
- compact route explanation rows with flow id, user id, selected satellite,
  next hop, path label, capacity, demand, latency, loss proxy, business type,
  and bottleneck explanation.

The route detail index preserves the export route explanation window. The demo
backend rebuilds this window from `visible_snapshot.routes` during package
creation with the same deterministic route explanation model and the existing
detail endpoint max limit of 5000 rows. This keeps `/runtime/status` lightweight
while making packages more useful for offline review. The artifact does not
replay events, recompute paths, compute all satellite pairs, or simulate
packets.
The standalone dashboard loads the selected package's route evidence through
`GET /runtime/export/packages/{package_id}/routes` and renders a read-only
route evidence drawer with indexed route counts, export-window policy,
server-filtered sample route rows, cursor controls, route evidence search,
availability/business/bottleneck filters, package-owned route-detail rendering,
row actions for live route-detail lookup, a `compare with live` action that
loads both route detail channels for the selected route, and direct JSON links.
The full `route_detail_index_v1.json` file remains downloadable, but it is not
fetched by the dashboard by default. The package route-detail action reads
`GET /runtime/export/packages/{package_id}/routes/{route_id}` and displays the
exported row as replay evidence. The live route-detail action is a read-only
comparison aid: it uses the current runtime detail endpoint when the same route
id still exists, and it does not replay or mutate the exported package. When
both details are loaded for the same route id, the dashboard renders a
field-level package-vs-live comparison card so users can see which route
semantics changed between the exported package and the current runtime. If the
comparison is not available, the dashboard reports whether package detail,
live detail, or route-id mismatch is preventing the comparison.

The demo backend also exposes package-owned route evidence endpoints:

```text
GET /runtime/export/packages/{package_id}/routes
GET /runtime/export/packages/{package_id}/routes/{route_id}
```

The list endpoint returns `RUNTIME_EXPORT_ROUTE_DETAIL_PAGE_V1` with cursor,
limit, optional query, availability, business type, and bottleneck filters. The
exact endpoint returns `RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1` for a route id in
the exported index. Both endpoints read the persisted `route_detail_index_v1.json`
artifact and include the source `route_detail_index_hash` plus
`route_comparison_review` metadata; they do not inspect the current runtime
session, replay events, recompute routes, or mutate the package. They only
cover rows already present in the exported route detail index; if a scenario
has more than the export limit, the policy and summary fields report the
remaining hidden route count.

The demo backend also exposes a package-owned service trace page endpoint:

```text
GET /runtime/export/packages/{package_id}/service-traces
```

The endpoint returns `RUNTIME_EXPORT_SERVICE_TRACE_PAGE_V1` with cursor, limit,
optional text query, terminal state, compute node id, lifecycle stage, and
terminal reason filters. It reads the persisted
`service_lifecycle_trace_v2.json` artifact and reports
`artifact_window_only=true`, because it pages and filters only the exported
trace window already present in the package. It does not inspect the current
runtime session, replay events, recompute services, or mutate the package.
Runtime export records the window boundary in
`config_snapshot.status.runtime_export_service_trace_policy_v1` and copies the
same policy into `service_lifecycle_trace_v2.json` and
`RUNTIME_EXPORT_SERVICE_TRACE_PAGE_V1`. The default service trace export limit
matches the large-detail maximum of 5000 rows; `hidden_trace_count` reports any
trace rows outside that persisted artifact window.

`route_comparison_review` also declares the deterministic
`RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1` report template. The
template defines the selected route comparison record schema, accepted status
values (`MATCH`, `DIFFERENT`, `UNAVAILABLE`, `ERROR`), ordering rule, and
no-recompute/no-replay boundaries. A review report records operator-selected
package-vs-live comparison outcomes; it does not mutate the package, run a
route recomputation, or infer route semantics in the frontend.

The demo backend can persist that report through:

```text
POST /runtime/export/packages/{package_id}/route-comparison-review-report
```

The request body is a JSON object with a `records` array. The backend reads the
package's `route_detail_index_v1.json`, builds
`route_comparison_review_report_v1.json` with stable ordering and a
`report_hash`, writes it into the package directory, and updates
`runtime_export_catalog_v1.json` so the artifact is retrievable through the
normal `/files/route_comparison_review_report_v1.json` path. The report also
copies the current backend `runtime_export_boundary_alignment_v1` evidence from
the package restore-preflight path, including `boundary_alignment_hash`,
`boundary_alignment_status`, `boundary_alignment_warnings`, and
`runtime_export_boundary_hash`. This lets an archived operator report cite the
exact compare/preflight boundary evidence used when the report was saved. The
endpoint saves selected operator review outcomes only; it does not compute
route diffs by itself, replay events, recompute routes, or update existing
archive zip files.

`scenario_review_bundle_v1.json` also declares a guided package review order.
The demo backend can persist operator decisions for that guided flow through:

```text
POST /runtime/export/packages/{package_id}/scenario-review-checklist
```

The request body is a JSON object with a `records` array. Each record may
include `artifact_filename`, `step_label`, `review_status`, `operator_note`,
`status_reason`, and `evidence_hash`. Accepted review statuses are
`REVIEWED`, `SKIPPED`, `NEEDS_FOLLOWUP`, and `ERROR`; invalid statuses are
recorded deterministically as `ERROR`. The backend writes
`scenario_review_checklist_v1.json`, sorts records by the backend-provided
review order, computes `checklist_hash`, updates the export catalog, and
regenerates `export_package_audit_index_v1.json` with checklist presence,
hash, status, and record count. The checklist records operator decisions only;
it does not replay events, recompute models, mutate package files on read, or
rewrite archives created before the save.

## Package Audit Index

Runtime exports include a compact long-term audit index artifact:

```text
RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1
```

The audit index id is:

```text
leo_twin.runtime_export_package_audit_index.v1
```

The artifact is written as `export_package_audit_index_v1.json`. It records the
package manifest hash, config/generated/runtime hashes, runtime export boundary
hash, boundary-alignment hash/status/warnings, user configuration audit binding,
user configuration schema id, user configuration config/export hashes,
validation status, review summary hash, diagnostics hash, optional route
comparison review report hash, optional scenario review checklist hash/status,
backend-owned package review completion status/hash, and the SHA-256 hashes of
package artifacts. The
audit index excludes its own file from `artifact_hashes` to avoid a circular
self-hash and excludes archive zip files because archives are generated after
the package evidence files. It is regenerated when a route comparison review
report or scenario review checklist is saved, so the report hash, checklist
hash, user configuration binding, scenario review bundle file hash, and the
preflight-derived boundary alignment evidence become part of the long-term
package audit trail.

The audit index embeds a machine-readable
`package_review_completion_v1` object with id:

```text
leo_twin.runtime_export_package_review_completion.v1
```

This object is the backend-owned handoff readiness summary for result-package
review. It reports audit status, saved route-comparison report presence and
error count, scenario-review bundle presence, checklist presence/status/count,
review summary status, diagnostics error count, boundary-alignment status, user
configuration validation, missing/warning evidence, and a deterministic
`completion_hash`. It deliberately does not include `audit_hash`, so the audit
index can hash the completion object without a self-reference.

For tools that only need the handoff summary, the demo backend exposes the same
object without returning the full audit index:

```text
GET /runtime/export/packages/{package_id}/review-completion
```

The endpoint reads `export_package_audit_index_v1.json` and returns its
`package_review_completion_v1` subobject plus the audit-index source artifact
record. It does not replay events, recompute package evidence, or mutate the
package.

The audit index is read-only evidence. It does not replay events, recompute
routes or services, mutate packages on read, capture packets, or call external
simulators.

## Scenario Review Bundle

The scenario review bundle artifact has type:

```text
RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1
```

The bundle id is:

```text
leo_twin.runtime_export_scenario_review_bundle.v1
```

It reports:

- package id and package directory;
- scenario scale and runtime progress copied from `review_summary_v1.json`;
- user configuration binding copied from the backend user configuration export;
- manifest, generated config, runtime state, metrics, and boundary hashes;
- review summary hash and diagnostics bundle hash;
- the audit index filename that will record the scenario review bundle file hash;
- deterministic model boundaries and recommended review order.

The scenario review bundle is an entry-point index only. It does not replay
events, recompute routes or services, mutate packages, capture packets, or call
external simulators.

## Diagnostics Bundle

The diagnostics bundle artifact has type:

```text
RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1
```

The bundle id is:

```text
leo_twin.runtime_export_diagnostics_bundle.v1
```

It reports:

- package id, package directory, contract id, package completeness, and review
  status;
- runtime lifecycle state, simulation time, processed events, and queued events;
- route trust evidence, including route model, trust status, assessed route
  count, explanation coverage, bottleneck components, and model-boundary flags;
- route comparison review metadata for package-vs-live route diagnostics;
- manifest id/hash plus config, generated-config, and review-summary hashes;
- the package reproducibility boundary copied from
  `config_snapshot.status.runtime_export_reproducibility_boundary_v1`;
- required and recommended artifact coverage;
- explicit model boundaries: no Event Kernel behavior change, no packet-level
  simulation, and no STK/EXATA/AFSIM/DDS integration;
- deterministic findings and operator next actions.

The diagnostics bundle is an index artifact only. It does not replay events,
capture packets, introduce wall-clock fields, or call external simulators.
If an older package lacks `route_provenance_trust_summary_v1`, the diagnostics
bundle remains readable and emits a deterministic
`ROUTE_TRUST_EVIDENCE_MISSING` warning instead of failing package export.
The standalone dashboard loads the selected package's
`diagnostics_bundle_v1.json` through the package file endpoint and renders its
package completeness, artifact-health counters, findings, model boundaries, and
recommended next actions as a read-only diagnostics drawer.
The dashboard also loads the selected package's `manifest.json` and renders a
read-only manifest inspector that shows stable manifest/scenario/config/
generated/metrics/runtime hashes, catalog file hashes, diagnostics manifest
hash agreement, and manifest artifact source/status rows.

## Hash Policy

- File records use SHA-256 over artifact bytes.
- Manifest hash uses stable canonical JSON.
- Catalog records preserve file hashes for package lookup and comparison.

## Archive Policy

Archive exports are deterministic ZIP files:

- entries are ordered by filename;
- entry timestamps are fixed at `2026-01-01T00:00:00`;
- each package archive is written inside the package directory.

## Restore Policy

Runtime export restore is configuration-scoped in v1:

- restore preflight compares exported and current config snapshots;
- restore writes a rollback export package before applying the selected config;
- exported event timelines are not replayed back into the live runtime.

## Benchmark Binding

Result packages are the evidence artifact for:

- `leo_twin.benchmark_scenario_matrix.v1`;
- `leo_twin.model_verification_report_template.v1`.

A benchmark run should attach the package manifest, config snapshot, events,
metrics, and summary to the verification report.

## Explicit Exclusions

- packet capture;
- binary trace format;
- external simulator artifacts;
- live event replay restore.
