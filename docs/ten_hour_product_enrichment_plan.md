# 10-Hour Product Enrichment Plan

Date: 2026-07-05
Branch: `feature/T163-frontend-dashboard-compute-v2`

This plan turns the next product-improvement discussion into a bounded,
testable, multi-agent development flow. It preserves the frozen deterministic
event kernel and keeps all realism improvements inside documented contracts,
configuration, event-driven models, and frontend observation surfaces.

## Operating Rules

- Do not modify Event Kernel ordering or time authority.
- Do not introduce STK, EXATA, AFSIM, DDS, packet-level simulation, or hidden
  external simulator dependencies.
- Use Starlink-like language only for approximate constellation profiles, not
  exact proprietary Starlink fidelity.
- Use EXATA-like language only for layered flow-level abstractions and KPI
  semantics, not for integration with EXATA.
- Keep backend as source of truth for product semantics.
- Update `docs/development_log.md`, commit, and push every completed task.
- Do not commit local runtime/generated config state.

## Checked Public Asset Sources

- NASA 3D Resources provides free downloadable mission-related 3D assets and
  points users to NASA media usage guidance:
  <https://science.nasa.gov/3d-resources/>
- NASA 3D Resources GitHub mirrors many assets and describes them as free and
  without copyright, still subject to NASA usage guidance:
  <https://github.com/nasa/NASA-3D-Resources>
- NASA Images and Media Usage Guidelines are the required licensing reference
  before bundling NASA assets:
  <https://www.nasa.gov/nasa-brand-center/images-and-media/>
- Natural Earth provides public-domain raster/vector map data suitable for
  country borders and Earth texture overlays:
  <https://www.naturalearthdata.com/>
- CesiumJS remains a future option for high-end 3D geospatial visualization, but
  adopting it would be a separate architecture task:
  <https://cesium.com/platform/cesiumjs/>

## 100 Product Improvement Suggestions

### A. Frontend-Backend Consistency

1. Make runtime status, WorldSnapshot, and dashboard cards consume one backend
   product summary object.
2. Add a schema version field to every frontend-consumed runtime payload.
3. Add frontend fallback text for missing optional backend fields.
4. Display backend-derived constellation profile names instead of local labels.
5. Show backend-selected fidelity mode in both control console and dashboard.
6. Keep simulation time, wall-clock run state, and cursor state synchronized
   across routes.
7. Persist the active session id when switching between console and dashboard.
8. Show stream cursor lag and last update age in developer diagnostics.
9. Add explicit status text for starting, running, paused, stopping, stopped,
   and reset states.
10. Add contract tests that compare backend JSON fields with frontend TypeScript
    types.

### B. Frontend Control Experience

11. Move simulation mode controls above progress as the primary control group.
12. Replace the unattractive mode frame with a compact segmented control.
13. Add numeric inputs next to sliders for satellite count, users, duration,
    and update rate.
14. Add min, max, and step labels for every numeric control.
15. Disable only controls that truly cannot be changed during a running session.
16. Add immediate validation messages for unsafe large-scale configurations.
17. Add a one-click 72, 300, and 1200 satellite scenario selector.
18. Add a small session health strip with backend, frontend stream, and cursor
    states.
19. Keep reset behavior visually atomic: progress, time, selected satellite,
    and charts reset together.
20. Add keyboard-free accessible controls for camera follow, pause, stop, and
    reset.

### C. 3D Earth Visual Quality

21. Replace transparent Earth material with opaque day-side surface rendering.
22. Add country boundary overlays using public-domain map data.
23. Add optional coastline and major land/water contrast layers.
24. Add low-cost night-side shading without exposing opposite-side satellites.
25. Add atmosphere rim and cloud layer as separate toggles.
26. Keep Earth texture loading deterministic with bundled or pinned assets.
27. Add level-of-detail controls for large satellite counts.
28. Add clear visual separation between Earth surface, orbit lines, and beams.
29. Add camera clipping and depth settings so far-side objects do not bleed
    through the globe.
30. Add screenshot-based visual regression checks for globe opacity and country
    visibility.

### D. Satellite Assets and Camera Interaction

31. Replace circular satellite markers with a reusable glTF satellite model.
32. Use instancing or shared geometry so 1200 satellites remain responsive.
33. Add a simplified fallback icon for scale mode and low-end devices.
34. Add satellite orientation based on velocity tangent and nadir direction.
35. Add hover highlight and selected-state outline.
36. Add satellite follow camera mode.
37. Add a local picture-in-picture window for the followed satellite.
38. Add zoomed local orbit trail around the selected satellite.
39. Show satellite id, plane, slot, altitude, velocity, and resource status in
    the selection panel.
40. Add deterministic model asset metadata and licensing documentation.

### E. Coverage and Multi-Beam Visualization

41. Show a satellite coverage footprint on Earth as a projected cone/ellipse.
42. Add coverage radius derived from altitude and configured elevation angle.
43. Add beam count as a backend-provided satellite payload field.
44. Render honeycomb-like multi-beam cells for the selected satellite.
45. Add beam color by utilization, interference risk, or load.
46. Add beam labels only when zoomed enough to avoid clutter.
47. Add ground user points that light up when covered.
48. Add handover preview for users moving between beams.
49. Add coverage confidence/fidelity notice for simplified geometry.
50. Add tests that verify coverage fields are deterministic for a fixed seed.

### F. Satellite Resource Situation Awareness

51. Treat each satellite as a compute node by default unless configuration says
    otherwise.
52. Add per-satellite resource vectors: CPU FP32/FP64, GPU FP32/FP16, NPU INT8,
    memory, storage, power, thermal headroom.
53. Add resource utilization bars in the selected satellite panel.
54. Add task queue depth and estimated wait time per satellite.
55. Add current ingress, egress, and compute-service flow counts.
56. Add resource pool pie charts for constellation-wide compute consumption.
57. Add resource heat coloring for satellites in the 3D view.
58. Add overloaded, degraded, and idle resource states.
59. Add a deterministic service-time estimator per resource bottleneck.
60. Add compute-node summary in WorldSnapshot and runtime status.

### G. Network and KPI Model Fidelity

61. Replace always-zero loss and jitter with deterministic flow-level models.
62. Compute propagation delay from current geometric distance.
63. Add queueing delay based on link utilization and configured capacity.
64. Add jitter as deterministic variation of recent delay deltas.
65. Add loss as deterministic function of congestion and link quality class.
66. Add throughput as delivered data over simulated time, not static display
    decoration.
67. Add link utilization, bottleneck link, and route hop count metrics.
68. Add transport profile labels such as UDP-like, TCP-like, and best-effort at
    flow level only.
69. Add route recomputation cadence for moving topology.
70. Add network KPI acceptance fixtures for 72, 300, and 1200 satellite modes.

### H. Orbit and Constellation Design

71. Add approximate Starlink-shell-like presets with documented assumptions.
72. Add multi-shell profile summaries for altitude, inclination, planes, and
    slots.
73. Add plane/slot visualization and color grouping.
74. Add derived orbital period display so users understand LEO motion speed.
75. Add speed scaling controls that separate real orbital period from demo
    playback speed.
76. Add deterministic phase offsets per plane.
77. Add altitude and inclination validation ranges.
78. Add shell-level satellite counts and totals in the frontend summary.
79. Add selected-satellite ground track.
80. Add orbit fidelity notice clarifying circular/periodic approximation.

### I. Data Dashboard and Analytics

81. Replace static KPI cards with time-series backed by stream cursor data.
82. Add synchronized charts for average throughput, latency, packet-loss proxy,
    jitter, and compute consumption.
83. Add chart reset behavior tied to backend RESET.
84. Add per-mode KPI explanations sourced from backend assumptions.
85. Add scenario comparison table for 72, 300, and 1200 satellite runs.
86. Add stream freshness and sample count indicators.
87. Add top congested links and top overloaded satellites tables.
88. Add selectable aggregation windows.
89. Add CSV/JSON export for visible KPI data.
90. Add dashboard tests that verify charts update over simulated time.

### J. Engineering, Validation, and Productization

91. Add a typed frontend API client for all runtime endpoints.
92. Add a backend contract fixture used by frontend tests.
93. Add Playwright smoke tests for console, dashboard, reset, and route switch.
94. Add deterministic screenshot checks for globe, satellite icon, and fidelity
    notice.
95. Add startup health checks to the Windows launcher UI/script output.
96. Add performance budget tests for 1200 satellites.
97. Add a docs page explaining model assumptions and forbidden external tools.
98. Add a product demo script with exact commands and expected screens.
99. Add release checklist entries for logs, tests, commits, and GitHub push.
100. Add issue-sized roadmap labels so future work stays reviewable.

## 10-Hour Task Flow

The first 10 hours should not attempt full realism. It should produce a visible
product-quality jump and a better semantic foundation.

### Hour 0.0-0.5: Baseline and Work Split

- Confirm branch, dirty files, latest remote, and service start status.
- Keep local runtime configs excluded.
- Spawn parallel read-only agents for frontend/3D, backend semantics, and
  validation flow.
- Deliverable: this plan and a development-log entry.

### Hour 0.5-2.0: Contract and Synchronization Slice

- Backend agent: identify canonical runtime summary fields for session, scale
  fidelity, constellation, KPI assumptions, and compute resources.
- Frontend agent: identify components consuming runtime status and snapshot.
- Main implementation target: ensure route switching does not restart the active
  session and RESET clears frontend progress/charts.
- Validation: targeted backend runtime tests plus frontend tests.

### Hour 2.0-3.5: 3D Earth and Satellite Asset Slice

- Replace transparent Earth rendering with opaque material and depth-safe
  settings.
- Add country/coastline overlay path using pinned public-domain map assets or a
  generated lightweight bundled texture.
- Add satellite model/asset pipeline with license notes; use instancing or a
  scale-mode fallback.
- Validation: frontend test/build and screenshot/manual browser check.

### Hour 3.5-5.0: Coverage and Multi-Beam Slice

- Add backend-derived selected-satellite coverage summary.
- Add selected-satellite coverage footprint and honeycomb beam visualization.
- Keep global 1200-node view aggregated; show detailed beams only for selected
  satellite.
- Validation: deterministic coverage tests and frontend render tests.

### Hour 5.0-6.5: Satellite Resource Inspector Slice

- Make satellite-as-compute-node semantics explicit.
- Add per-satellite resource vector summary to snapshot/status.
- Add selected satellite resource panel and constellation resource pool chart.
- Validation: compute model unit tests and dashboard tests.

### Hour 6.5-8.0: Network KPI Semantics Slice

- Add deterministic flow-level latency, throughput, jitter, and loss proxy
  calculations.
- Use geometric distance, utilization, route hops, and congestion class.
- Preserve no-packet-level rule.
- Validation: deterministic network KPI fixtures.

### Hour 8.0-9.0: Dashboard Dynamics Slice

- Bind dashboard charts to stream cursor samples.
- Add reset synchronization for chart buffers.
- Add top congested links and overloaded satellites using backend fields.
- Validation: frontend tests and build.

### Hour 9.0-10.0: Acceptance, Logs, Commits, Pushes

- Run targeted backend tests.
- Run frontend tests/build.
- Update development log for each delivered slice.
- Commit and push each completed issue-sized task.
- Report changed files, tests, limitations, and recommended next task.

## Parallel Agent Roles

- Agent Frontend/3D: owns visual components, 3D scene, asset rendering, and
  route-level state synchronization.
- Agent Backend Semantics: owns runtime summaries, model assumptions, KPI
  summaries, and snapshot fields.
- Agent Network Metrics: owns flow-level delay, throughput, jitter, loss proxy,
  and deterministic tests.
- Agent Compute: owns resource vector semantics and service-time estimation.
- Agent Validation: owns tests, development log checks, commit scope review, and
  launcher smoke checks.

## Commit Slices

1. `docs(plan): add ten hour product enrichment plan`
2. `fix(frontend): preserve runtime session across dashboard routes`
3. `feat(visual): improve globe opacity and satellite asset rendering`
4. `feat(visual): show selected satellite coverage and beams`
5. `feat(compute): expose satellite resource inspector summary`
6. `feat(network): add deterministic flow-level KPI dynamics`
7. `feat(dashboard): bind KPI charts to runtime streams`
8. `test(product): add visual and runtime acceptance checks`

## Execution Progress

The following issue-sized slices have now been delivered on
`feature/T163-frontend-dashboard-compute-v2` and pushed to GitHub:

- `3dac262 feat(globe): show selected satellite resource detail`
  - Maps to suggestions 39, 51, 52, 55, and the Hour 5.0-6.5 satellite
    resource inspector slice.
  - The selected satellite strip now expands CPU FP32/FP64, GPU FP32/FP16,
    NPU INT8, memory, and storage usage rows from existing backend/snapshot
    resource vectors.
- `15815e1 feat(dashboard): add selectable compute series`
  - Maps to suggestions 57, 61, 62, 65, and the Hour 8.0-9.0 dashboard
    dynamics slice.
  - The data panel compute chart can switch between FP32, FP64, GPU, NPU,
    memory, and storage series from backend KPI samples.
- `025bd10 test(metrics): lock network quality proxies`
  - Maps to suggestions 66-75 and the Hour 6.5-8.0 network KPI semantics
    slice.
  - Integration coverage now prevents demo network loss and delay-variation
    proxies from regressing to all-zero values.
- `5cb497d feat(config): add network quality presets`
  - Maps to suggestions 14, 65, 66, 68, 72, and the network KPI semantics
    configuration path.
  - Users can choose stable low-load, congested demand, lossy access, and
    high delay-variation presets without changing backend schema or runtime
    config files.
- `c39fd72 test(frontend): add runtime contract fixture`
  - Maps to suggestions 1, 2, 10, 91, and 92.
  - Frontend tests now decode a representative backend `/runtime/status`
    envelope covering fidelity, generated config, KPI series, satellite slices,
    stream diagnostics, and compute resource summaries.
- `95b3953 feat(metrics): extend satellite kpi resource slices`
  - Maps to suggestions 51, 52, 55, 57, and the satellite resource inspector
    slice.
  - Backend satellite KPI slices now include optional compute vector usage
    fields, and the selected-satellite detail summary can use those fields when
    a compute-node snapshot is not present.
- `feat(globe): add selected satellite resource sparkline`
  - Maps to suggestions 53, 57, 58, and the selected satellite resource
    inspector slice.
  - The selected satellite strip now renders a bounded local history sparkline
    for the current satellite's resource utilization, resetting the history
    when the operator switches satellites.
- `feat(metrics): expose satellite kpi history`
  - Maps to suggestions 53, 57, 58, 91, and the backend/frontend semantic
    alignment slice.
  - Runtime status now exposes bounded `satellite_kpi_history_v1` resource
    samples from satellite compute-node observations, and the 3D control view
    uses that backend history before falling back to local observation.
- `feat(metrics): expose network quality provenance`
  - Maps to suggestions 66-75 and 91.
  - Runtime status now exposes structured `network_quality_provenance_v1`, and
    the data panel uses it to explain throughput, latency, loss, and
    delay-variation proxy sources without introducing packet-level simulation.
- `test(frontend): lock dashboard attach progress`
  - Maps to suggestions 1, 2, 10, and 92.
  - Frontend tests now guard that dashboard/control route switches attach to an
    already running runtime without resetting local stream state or rolling back
    the shared display progress clock.
- `test(frontend): expand visual verification scope`
  - Maps to suggestions 30, 93, 94, and 95.
  - `scripts/verify_frontend_visuals.ps1` now verifies visual assets, globe and
    dashboard visual logic, runtime status contract decoding, dashboard attach
    progress behavior, and frontend build in one command.
- `feat(metrics): summarize service latency components`
  - Maps to suggestions 76-82 and the communication-compute lifecycle slice.
  - Metrics summary now aggregates existing `service.*` lifecycle samples into
    input-network, compute-queue, compute-execution, output-network, and total
    service latency fields.
- `feat(dashboard): show service latency components`
  - Maps to suggestions 76-82 and 91.
  - The dashboard now consumes backend `service_latency_*` summary fields and
    displays communication-compute component latency values in the compute
    resource panel when samples exist.
- `test(frontend): add service latency contract fixture`
  - Maps to suggestions 76-82 and 92.
  - The runtime status fixture now locks the `service_latency_*` metrics summary
    contract consumed by the dashboard service latency block.
- `feat(metrics): expose service latency history`
  - Maps to suggestions 76-82 and the per-service lifecycle trace path.
  - Runtime status now exposes bounded `service_latency_history_v1` items from
    existing lifecycle component samples for future trace-row UI.
- `feat(dashboard): show service trace rows`
  - Maps to suggestions 76-82 and 91.
  - The dashboard now renders bounded per-service trace labels from
    `service_latency_history_v1` with task id, closed-loop state, and total
    latency.
- `feat(metrics): include service trace metadata`
  - Maps to suggestions 76-82.
  - Service trace history now carries input/output flow ids and route ids from
    existing metric tags, and dashboard trace labels expose them in hover
    titles.
- `feat(metrics): include service trace timing`
  - Maps to suggestions 76-82.
  - Service trace history now carries first/last service metric sample
    simulation times, and dashboard trace labels expose the observation window
    in hover titles.
- `feat(metrics): include service trace detail`
  - Maps to suggestions 76-82 and 91.
  - Service trace history now carries deterministic `component_timeline` rows
    for input network, compute queue, compute execution, output network, and
    total latency; dashboard trace labels expose the timeline without a layout
    redesign.
- `feat(dashboard): show service trace timeline`
  - Maps to suggestions 76-82 and 91.
  - The dashboard compute panel now renders backend-provided service
    `component_timeline` rows as compact visible stage chips while preserving
    compatibility for legacy status packets.
- `test(frontend): harden visual verification runtime path`
  - Maps to suggestions 92-95.
  - The frontend visual verification script now repairs a missing `node.exe`
    PATH entry when it is launched with the bundled `pnpm.cmd` dependency path,
    keeping dashboard/service-timeline visual checks runnable from a narrower
    shell environment.
- `feat(launcher): add dashboard open surface`
  - Maps to suggestions 18, 91, 93, and 95.
  - `scripts/sees_launcher.ps1` now accepts `-OpenSurface dashboard` and
    reports both console and dashboard URLs from `status`, reducing manual
    navigation for dashboard-first validation.
- `docs(readme): document local launcher workflow`
  - Maps to suggestions 18, 91, 93, and 95.
  - The repository README now advertises the supported Windows launcher,
    dashboard URL, backend runtime status URL, launcher logs, and the frontend
    visual/dashboard verification command.
- `test(runtime): add read-only health smoke script`
  - Maps to suggestions 18, 91, 93, 94, and 95.
  - `scripts/smoke_runtime_health.ps1` verifies backend `/runtime/status`,
    required generated summary fields, frontend console, and dashboard without
    issuing control commands or mutating runtime configuration.
- `docs(acceptance): add service timeline checks`
  - Maps to suggestions 76-82 and 91-95.
  - Product acceptance scenarios now include the read-only runtime health smoke,
    backend `component_timeline`, and dashboard service timeline rendering as
    documented acceptance checks.
- `test(product): add aggregate acceptance verification`
  - Maps to suggestions 91-95.
  - `scripts/verify_product_acceptance.ps1` runs targeted backend service
    timeline tests, frontend visual/dashboard verification, and read-only
    runtime health smoke as one local acceptance command.
- `test(runtime): add health smoke json summary`
  - Maps to suggestions 91-95.
  - `scripts/smoke_runtime_health.ps1 -JsonSummary` now emits structured
    health output for automation while preserving human-readable output by
    default.
- `test(runtime): add health endpoint timings`
  - Maps to suggestions 18, 91, 94, and 95.
  - Runtime health smoke now reports backend status, console, and dashboard
    endpoint timings in both human-readable and JSON outputs.
- `test(runtime): validate health product summary`
  - Maps to suggestions 1, 5, 76-82, and 91-95.
  - Runtime health smoke now verifies backend-derived constellation, traffic,
    and compute summaries and reports satellite count, user count, profile,
    traffic class, and compute node count.
- `test(runtime): add expected health summary checks`
  - Maps to suggestions 91-95.
  - Runtime health smoke now supports opt-in expected satellite count, user
    count, and traffic class assertions for acceptance scenario checks.
- `test(product): pass expected summary checks`
  - Maps to suggestions 91-95.
  - Aggregate product acceptance verification now forwards expected satellite
    count, user count, and traffic class into the read-only runtime health
    smoke check.
- `test(product): read acceptance config expectations`
  - Maps to suggestions 91-95.
  - Aggregate product acceptance verification can now read minimal expected
    satellite count, user count, and traffic class values from acceptance YAML,
    while still allowing explicit CLI overrides.
- `test(runtime): add compute count expectation`
  - Maps to suggestions 51, 76-82, and 91-95.
  - Runtime health and aggregate acceptance scripts now support expected compute
    node count checks and read `scenario.compute_nodes` from acceptance YAML.
- `feat(launcher): add dashboard batch shortcut`
  - Maps to suggestions 18, 91, and 95.
  - `dashboard_leo_twin.bat` gives Windows users a direct dashboard-first
    launcher without typing PowerShell arguments.
- `feat(launcher): add status and smoke shortcuts`
  - Maps to suggestions 18, 91, and 95.
  - `status_leo_twin.bat` and `smoke_leo_twin.bat` provide non-destructive
    service-status and runtime-health checks without PowerShell argument
    assembly.
- `feat(launcher): add interactive menu`
  - Maps to suggestions 18, 91, and 95.
  - `leo_twin_launcher.bat` provides a simple Windows menu for start console,
    start dashboard, status, smoke health check, restart, and stop operations.
- `feat(launcher): add acceptance menu option`
  - Maps to suggestions 91-95.
  - The interactive launcher menu now includes product acceptance verification
    through the aggregate script for dashboard/service/runtime checks.
- `feat(launcher): add full acceptance menu option`
  - Maps to suggestions 91-95.
  - The launcher menu now separates fast acceptance without frontend build from
    full acceptance with build.
- `docs(launcher): add troubleshooting guide`
  - Maps to suggestions 18, 91, and 95.
  - Launcher troubleshooting now documents non-destructive status/smoke checks,
    common frontend/backend startup symptoms, logs, Node/Pnpm issues, and
    dashboard-first startup.
- `test(git): add runtime config staging guard`
  - Maps to suggestions 91-95 and the project rule to avoid committing local
    generated runtime config.
  - `scripts/check_no_runtime_config_staged.ps1` fails if the known local
    runtime config files are staged before commit.
- `test(product): run staging guard in acceptance`
  - Maps to suggestions 91-95 and the project rule to avoid committing local
    generated runtime config.
  - Aggregate product acceptance verification now runs the staged runtime config
    guard before backend/frontend/runtime smoke checks.
- `feat(launcher): show status action hints`
  - Maps to suggestions 18 and 95.
  - Launcher status output now points directly to smoke and dashboard launcher
    shortcuts after reporting service URLs.
- `test(runtime): verify frontend shell in smoke`
  - Maps to suggestions 91-95.
  - Runtime health smoke now confirms console and dashboard URLs return the
    expected frontend application shell, not only HTTP success.
- `test(runtime): validate compute vector model`
  - Maps to suggestions 51, 57, and 91-95.
  - Runtime health smoke now asserts `ComputeResourceVector` in backend compute
    summary and exposes the resource model in JSON output.
- `test(runtime): add constellation profile expectation`
  - Maps to suggestions 1, 4, 5, and 91-95.
  - Runtime health and aggregate acceptance scripts can now assert backend
    derived constellation profile names.
- `test(runtime): add protocol guard to health smoke`
  - Maps to suggestions 66-75 and 91-95, plus the external-simulator ban.
  - Runtime health smoke now rejects forbidden STK/EXATA/AFSIM/DDS markers and
    reports orbit model plus application/transport/routing protocols.
- `test(product): add forbidden import guard`
  - Maps to suggestions 91-95 and the external-simulator ban.
  - Aggregate product acceptance now runs a static import guard for forbidden
    STK/EXATA/GloMoSim/AFSIM/DDS runtime packages before backend/frontend
    checks.
- `docs(readme): document guard commands`
  - Maps to suggestions 91-95.
  - README now lists both runtime config staging and forbidden runtime import
    guard commands for local pre-commit checks.
- `test(git): add pre-commit aggregate checks`
  - Maps to suggestions 91-95.
  - `scripts/pre_commit_checks.ps1` now runs the staged runtime config guard,
    forbidden runtime import guard, and `git diff --check` through one local
    pre-commit entry point.
- `test(runtime): add control cycle smoke`
  - Maps to suggestions 14-18 and 91-95.
  - `scripts/smoke_runtime_control_cycle.ps1` and `control_smoke_leo_twin.bat`
    exercise INITIALIZE, START, PAUSE, RESUME, STOP, and RESET through the
    existing control websocket for a scale-safe 1200-satellite scenario.
- `test(product): add optional control cycle gate`
  - Maps to suggestions 14-18 and 91-95.
  - `scripts/verify_product_acceptance.ps1 -RunControlCycleSmoke` can now add
    the mutating 1200-satellite control-cycle check after normal acceptance
    verification.
- `docs(status): refresh current product status`
  - Maps to suggestions 14-18 and 91-95.
  - `docs/current_product_status.md` now lists the control-cycle smoke,
    optional aggregate acceptance gate, and latest 1200-node control validation
    result.
- `fix(frontend): guard pending control actions`
  - Maps to suggestions 14-18 and 91-95.
  - The control panel now treats `*_PENDING` runtime actions as busy states so
    start, pause/resume, initialize, stop, and reset cannot be fired repeatedly
    while the local control transition is awaiting backend acknowledgement.
- `docs(acceptance): record final 10-hour checkpoint`
  - Maps to suggestions 91-95.
  - The final checkpoint records aggregate fast acceptance with the 1200-node
    control-cycle gate after the frontend pending-control guard.

Completed earlier slices in this thread also cover stream diagnostics, opaque
Earth rendering, country boundary assets, visual layer explanations, selected
satellite coverage/beam labels, compute vector KPI samples, and the frontend
visual verification script. The remaining high-value product gaps are backend
service-trace drill-down filtering, screenshot pixel baselines, and
browser-driven reset/control end-to-end smoke tests.

Latest full local acceptance run:

- Command:
  `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE`
- Result: passed.
- Coverage:
  runtime config staging guard, forbidden runtime import guard, backend service
  timeline tests, frontend visual/dashboard tests, frontend build, and
  read-only runtime health smoke.

Current handoff summary:

- `docs/current_product_status.md` records local entry points, acceptance
  command, latest full verification result, current product signals, and
  remaining gaps.

## Acceptance Gates

- Existing backend runtime/session tests pass.
- Existing frontend tests and build pass.
- 72-satellite demo remains visually detailed.
- 1200-satellite mode remains responsive and transparent about fidelity.
- Switching between console and dashboard does not restart the session.
- RESET clears backend session state, frontend progress, selected satellite, and
  dashboard chart buffers.
- Earth is opaque enough that far-side satellites are not visible through it.
- Selected satellite can show coverage, beam cells, and resource usage.
- Loss, jitter, latency, throughput, and compute utilization change over
  simulated time using deterministic flow-level abstractions.
