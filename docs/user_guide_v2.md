# LEO-Twin / SEES User Guide v2

Date: 2026-07-06

This guide is the user-facing entry point for the current SEES v2 product
prototype. It is written for operators who need to start the system, configure
a scenario, inspect the dashboard, export results, and collect diagnostics.

## 1. Start The System

From the repository root, use the Windows launcher:

```powershell
.\leo_twin_launcher.bat
```

Direct shortcuts:

```powershell
.\start_leo_twin.bat
.\dashboard_leo_twin.bat
.\restart_leo_twin.bat
.\stop_leo_twin.bat
.\status_leo_twin.bat
```

Default surfaces:

- console: `http://127.0.0.1:5173`
- dashboard: `http://127.0.0.1:5173/dashboard`
- backend status: `http://127.0.0.1:8765/runtime/status`
- backend version: `http://127.0.0.1:8765/runtime/version`

## 2. Check Health

Human-readable status:

```powershell
.\status_leo_twin.bat
.\scripts\sees_launcher.ps1 status
```

Machine-readable launcher health:

```powershell
.\scripts\sees_launcher.ps1 status -JsonSummary
.\scripts\sees_launcher.ps1 health -JsonSummary
```

Read-only runtime smoke:

```powershell
.\smoke_leo_twin.bat
.\scripts\smoke_runtime_health.ps1 -JsonSummary
```

Control-path smoke, which mutates and resets the active session:

```powershell
.\control_smoke_leo_twin.bat
.\scripts\smoke_runtime_control_cycle.ps1 -JsonSummary
```

## 3. Configure A Scenario

The frontend shows key controls only. The full detailed configuration remains
file/API driven.

Main user configuration endpoints:

- `GET /scenario/user-config/schema`
- `GET /scenario/user-config/templates`
- `GET /scenario/user-config/export`
- `POST /scenario/user-config/validate`
- `POST /scenario/user-config/validate-text`

Minimal YAML example:

```yaml
scenario:
  satellite_count: 72
  compute_nodes: 72
runtime:
  duration: 600
  seed: 20260703
```

Validation is explicit. A valid preflight response provides a normalized config
and an apply command. Applying a config reinitializes the active runtime session.

Runtime/local generated config files are not source files:

- `configs\sees_control.yaml`
- `configs\generated_full_system_demo.json`

Do not commit them unless a task explicitly says they are part of the change.

## 4. Use The Console And Dashboard

The console is for simulation control and 3D inspection:

- initialize, start, pause, resume, stop, reset;
- configure key scenario controls;
- inspect the 3D Earth, satellites, links, users, and selected-satellite views;
- see scale/fidelity notices from backend runtime status.

The standalone dashboard is for data situation awareness:

- network KPI trend and provenance;
- business/service traces;
- route explanations;
- compute resource and task timeline summaries;
- user, satellite, and node detail pages;
- configuration explanation and model assumptions.

Backend runtime status is the source of truth. The frontend should not invent
business semantics locally.

## 5. Export Results

Live runtime export:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/runtime/export
```

Archive export:

```text
http://127.0.0.1:8765/runtime/export/archive
```

Each result package contains:

- `config_snapshot.json`
- `events.jsonl`
- `metrics.csv`
- `summary.json`
- `manifest.json`
- `service_lifecycle_trace_v2.json`
- `route_detail_index_v1.json`
- `review_summary_v1.json`
- `diagnostics_bundle_v1.json`

The standalone dashboard export review area loads the selected package's
server-side route evidence page and shows route evidence counts,
export-window policy, cursor navigation, searchable/filterable route rows, and
package route-detail review without rerunning the simulation. The package
review area also loads `service_lifecycle_trace_v2.json` when it is present in
the export catalog and displays a read-only communication-compute service chain
review with trace counts, terminal-state totals, bounded stage rows, local
artifact filters, and deterministic local page controls. These filters cover
trace text, terminal state, compute node id, lifecycle stage, and terminal
reason. The package detail view reads the exported package itself and does not
rerun the simulation. The separate live lookup only
compares against the current runtime route detail endpoint when the same route
id is still present. Use `compare with live` to load both detail channels for
the same route in one click. If both package and live details are loaded for
the same route, the dashboard shows a package-vs-live comparison card with
matched and different route fields. If the comparison is not ready, the same
area explains whether package detail, live detail, or route-id mismatch is the
reason. The package review artifacts include `route_comparison_review`
metadata so the available comparison fields, live-runtime requirement, and
no-recompute boundaries are visible outside the dashboard UI. The same metadata
declares the `RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1` template for
recording selected route comparison outcomes with deterministic record ordering.
Runtime export rebuilds the package route evidence window with a 5000-row
maximum; hidden rows beyond that limit are reported in the package policy.
After using `compare with live`, the package-vs-live route comparison card can
save the currently displayed comparison into
`route_comparison_review_report_v1.json`. The saved record includes the
compared fields, different fields, package route detail hash, live route detail
hash, status reason, and dashboard operator note. After the save completes, the
dashboard package review area shows the report artifact from the backend export
catalog with a direct JSON link and file hash. If the report artifact is
available, the dashboard loads it read-only and summarizes saved record counts,
MATCH/DIFFERENT/UNAVAILABLE/ERROR totals, route detail hash pairs, and operator
notes. The report drawer can filter by status, search route id/status/hash/note
text, and page through matching records without opening the raw JSON.
For package-owned review, use:

```powershell
Invoke-RestMethod "http://127.0.0.1:8765/runtime/export/packages/<package_id>/routes?cursor=0&limit=100"
Invoke-RestMethod "http://127.0.0.1:8765/runtime/export/packages/<package_id>/routes/<route_id>"
$body = @{
  records = @(
    @{
      route_id = "<route_id>"
      comparison_status = "DIFFERENT"
      compared_fields = @("latency", "bottleneck")
      different_fields = @("latency")
      status_reason = "FIELDS_DIFFER"
      operator_note = "manual review note"
    }
  )
} | ConvertTo-Json -Depth 5
Invoke-RestMethod `
  -Method Post `
  -ContentType "application/json" `
  -Body $body `
  "http://127.0.0.1:8765/runtime/export/packages/<package_id>/route-comparison-review-report"
```

The first two calls read the exported route detail index artifact. They do not
require the current runtime to contain the same route id. The POST call writes
`route_comparison_review_report_v1.json` into the selected package and updates
the export catalog; it records supplied review outcomes and does not rerun a
route comparison automatically.

Export catalog:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/runtime/export/catalog
```

## 6. Collect Diagnostics

When reporting a problem, collect an operator diagnostics bundle:

```powershell
.\diagnostics_leo_twin.bat
.\scripts\collect_operator_diagnostics.ps1 -JsonSummary
```

Default output:

```text
artifacts\operator_diagnostics
```

The bundle includes launcher health, runtime status, version info, current
config export, export catalog, diagnostics manifest, and copied launcher logs.

## 7. Benchmark And Acceptance

Baseline scenarios:

- 72 satellites: detailed baseline;
- 300 satellites: bounded scale transition;
- 1200 satellites: large-scale short responsiveness baseline.

Acceptance commands:

```powershell
.\scripts\verify_product_acceptance.ps1 -SkipBuild
.\scripts\verify_product_acceptance.ps1 -AcceptanceConfig configs\acceptance\small_demo_72sat.yaml
```

Benchmark contracts:

- `leo_twin.benchmark_scenario_matrix.v1`
- `leo_twin.model_verification_report_template.v1`
- `leo_twin.result_package_contract.v1`

## 8. Current Model Boundaries

SEES v2 is a deterministic flow-level digital twin prototype. It is useful for
controlled scenario exploration, dashboard semantics, and reproducible
engineering experiments.

It is not yet a high-fidelity engineering decision simulator. Current limits:

- no STK, EXATA, AFSIM, or DDS integration;
- no packet-level simulation;
- no RF propagation field solver;
- no antenna pattern modeling;
- no SGP4 orbital fidelity;
- no real code execution on compute nodes;
- large-scale scenarios use explicit fidelity reduction such as batched orbit
  updates and bounded candidate ISL links.

When scale mode is active, the backend reports the selected fidelity policy in
runtime status and the frontend displays it to users.

## 9. Where To Read More

- `docs\integration_demo.md`
- `docs\user_configuration_schema_v2.md`
- `docs\launcher_health_check_v2.md`
- `docs\operator_diagnostics_bundle_v1.md`
- `docs\result_package_contract_v1.md`
- `docs\product_acceptance_scenarios.md`
- `docs\launcher_troubleshooting.md`
