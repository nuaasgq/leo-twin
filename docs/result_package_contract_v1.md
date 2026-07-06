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
- route trust summary copied from
  `config_snapshot.status.route_provenance_trust_summary_v1`;
- exported route ids, route-trust sample route ids, indexed sample ids, and
  missing sample ids;
- compact route explanation rows with flow id, user id, selected satellite,
  next hop, path label, capacity, demand, latency, loss proxy, business type,
  and bottleneck explanation.

The route detail index preserves the current backend route explanation window.
It does not replay events, recompute paths, compute all satellite pairs, or
simulate packets.

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
- manifest id/hash plus config, generated-config, and review-summary hashes;
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
