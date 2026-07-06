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

The manifest id must be:

```text
leo_twin.runtime_reproducibility_manifest.v1
```

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
