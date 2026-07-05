# LEO-Twin / SEES System v2 Upgrade Plan

Date: 2026-07-05
Branch: feature/T165-system-v2-roadmap
Status: active planning baseline

## 1. V2 Mission

System v2 moves LEO-Twin from a runnable engineering prototype toward an
industrial-grade digital twin product. The upgrade must improve:

- configuration-driven scenario authoring;
- backend-owned model semantics;
- trustworthy KPI provenance;
- scalable runtime behavior;
- user-facing observability;
- reproducible result packages;
- operator-friendly deployment and diagnostics.

The current product baseline is estimated at 25-35 / 100 for industrial product
readiness. V2 should target 55-65 / 100 before attempting high-fidelity or
external-tool integrations.

## 2. Non-Negotiable Constraints

- Do not modify Event Kernel ordering or domain behavior.
- Do not introduce STK, EXATA, AFSIM, DDS, or packet-level simulation.
- Keep all model behavior deterministic with seeded randomness only.
- Keep orbit, network, compute, metrics, services, and frontend boundaries
  explicit.
- Prefer backend-owned semantics over frontend inference.
- Every completed development task must update `docs/development_log.md`,
  commit only related files, and push to GitHub.
- Runtime/local generated config changes must not be committed unless the task
  explicitly scopes them.

## 3. V2 Workstreams

### WS1. Product Configuration v2

Goal: make scenarios understandable and controllable by users.

Tasks:

- V2-001: Define user-facing configuration schema v2.
  - Scope: schema fields, validation rules, defaults, comments, examples.
  - Output: docs and tests for accepted/rejected configs.
  - Depends on: existing generated config and templates.
- V2-002: Add template catalog metadata.
  - Scope: scenario name, purpose, scale, expected KPI behavior, fidelity mode.
  - Output: backend template endpoint and frontend selector metadata.
  - Depends on: V2-001.
- V2-003: Add config explanation summary.
  - Scope: backend-generated text/structured explanation for orbit, network,
    traffic, compute, runtime, fidelity.
  - Output: `backend_summary.configuration_explanation_v2`.
  - Depends on: V2-001.
  - Status: implemented in T196 as a read-only backend-derived explanation
    contract that maps accepted config sections to current model semantics and
    explicit exclusions.
- V2-004: Add import/export config workflow.
  - Scope: frontend upload/download for user config, backend validation errors.
  - Output: no silent fallback on invalid keys.
  - Depends on: V2-001, V2-003.
  - Status: preflight validation API implemented in T198 as
    `POST /scenario/user-config/validate`; dashboard JSON preflight UI
    implemented in T199; guarded preflight-to-apply flow implemented in T200 by
    sending backend-normalized config through explicit `CONFIG_UPDATE`;
    backend preflight diff summary implemented in T201; dashboard diff
    rendering implemented in T202; backend/runtime apply readiness and
    dashboard readiness rendering implemented in T203; backend JSON/YAML text
    preflight endpoint implemented in T204; dashboard JSON/YAML text preflight
    mode implemented in T205.

### WS2. Business Demand Model v2

Goal: model user demand as traceable communication and compute services.

Tasks:

- V2-010: Define service request contract v2.
  - Scope: service id, user id, class, priority, destination policy, input size,
    output size, duration, deadline, retry policy, generated flow/task ids.
  - Output: schema/tests only.
- V2-011: Add deterministic arrival profile model.
  - Scope: periodic, burst, diurnal, and region-weighted arrivals using seed.
  - Output: unit tests for identical seed and config.
  - Depends on: V2-010.
- V2-012: Add service mix profiles.
  - Scope: telemetry, bulk downlink, data transfer, compute service, emergency.
  - Output: summary counts and per-user active service state.
  - Depends on: V2-010, V2-011.
- V2-013: Add service lifecycle trace.
  - Scope: input flow, queue, compute, output flow, terminal state.
  - Output: timeline records for dashboard and result export.
  - Depends on: V2-012 and compute lifecycle work.

### WS3. Network Semantics and KPI Trust v2

Goal: make throughput, latency, loss, and jitter explainable.

Tasks:

- V2-020: Document layered network model contract.
  - Scope: application, transport, routing, data link, channel abstraction.
  - Output: docs and schema enums; no behavior rewrite.
- V2-021: Add KPI provenance contract v2.
  - Scope: formula inputs for throughput, latency, loss proxy, jitter proxy.
  - Output: backend `network_kpi_provenance_v2`.
  - Depends on: V2-020.
  - Status: provenance contract implemented earlier; backend
    `network_kpi_credibility_v1` coverage/trust summary implemented in T206;
    standalone dashboard trust card bound to backend credibility fields in T207.
- V2-022: Add time-varying flow-level network pressure.
  - Scope: deterministic demand/capacity pressure, route blocking, congestion
    proxy, loss proxy, delay variation proxy.
  - Output: tests proving KPI movement under stress and stability under low load.
  - Depends on: V2-021.
  - Status: deterministic simulation-time pressure factor and tail-sample
    decomposition implemented in T208.
- V2-023: Add route explanation records.
  - Scope: selected route, alternative count, bottleneck reason, next hop,
    blocked reason.
  - Output: backend-owned detail rows for users/satellites.
  - Depends on: V2-022.
  - Status: backend `route_explanation_summary_v1` runtime status object
    implemented in T209; standalone dashboard route explanation table bound to
    backend fields in T210; dashboard text filter for route/user/satellite/
    bottleneck/business search implemented in T211; structured availability,
    business-type, and bottleneck filters implemented in T212.

### WS4. Compute Network Model v2

Goal: represent satellites as product-grade compute nodes and resource pools.

Tasks:

- V2-030: Stabilize compute resource vector v2.
  - Scope: FP32, FP64, FP16, INT8, memory, storage, compatibility rules.
  - Output: schema docs and unit tests.
  - Status: compute resource vector schema/summary already exists; T213 adds
    backend-owned bottleneck resource, utilization, available/used/total, and
    pressure status fields to runtime metrics, with the standalone dashboard
    consuming those fields instead of inferring bottlenecks locally.
- V2-031: Add service placement model.
  - Scope: deterministic service-to-satellite placement, capacity check,
    queue state, rejection reason.
  - Depends on: V2-030.
  - Status: service placement contract/runtime already exists; T214 adds a
    bounded backend-owned candidate queue observability label to service
    latency history, user request summaries, node detail cards, and dashboard
    placement labels.
- V2-032: Add task queue and execution timeline v2.
  - Scope: queue delay, execution delay, resource bottleneck, deadline status.
  - Depends on: V2-031.
  - Status: T215 adds backend-owned `compute_task_timeline_summary_v1` derived
    from service latency history, exposing task count, queued task count,
    aggregate queue/execution delay, and bounded recent task stage rows to the
    dashboard without changing the compute scheduling policy.
- V2-033: Add cache/offload/migration contracts.
  - Scope: contracts and observability only; behavior can be later.
  - Depends on: V2-032.
  - Status: T216 adds `cache_offload_migration_contract_v1` to schema and
    backend-derived summary. It defines cache lookup/fill, task offload, and
    service migration observability fields while explicitly keeping behavior
    disabled for v1.

### WS5. Runtime Scale and Stability v2

Goal: keep large-scale scenarios responsive and transparent.

Tasks:

- V2-040: Define scale policy v2.
  - Scope: 72, 300, 1200, 3000, 6000, 12000 profile rules.
  - Output: fidelity summary, explicit frontend notices, tests.
  - Status: T234 adds backend-owned `leo_twin.scale_policy.v2` with six
    product scale profiles (`baseline_72`, `medium_300`, `large_1200`,
    `xl_3000`, `xxl_6000`, `extreme_12000`). The policy is included in
    backend derived summaries and records orbit update mode, metrics mode,
    space-link mode, snapshot LOD policy, detail-window policy, frontend
    rendering policy, runtime guardrail policy, and result reproducibility
    expectations without changing Event Kernel or runtime behavior.
- V2-041: Add LOD snapshot policy.
  - Scope: detail windows, top-K summaries, sampled histories, raw counts.
  - Depends on: V2-040.
  - Status: T235 adds backend-owned `leo_twin.lod_snapshot_policy.v2` derived
    from `scale_policy_v2`. The policy is included in backend derived summaries
    and records raw count fields, bounded detail windows, Top-K summary limits,
    sampled history lengths, cursor requirements, hidden-row explanations, and
    deterministic ordering/sampling rules without changing current runtime
    snapshot publication behavior.
- V2-042: Add runtime guardrails.
  - Scope: event volume estimate, memory estimate, stream backlog estimate,
    explicit refusal/degrade reason.
  - Depends on: V2-040.
  - Status: T236 adds backend-owned `leo_twin.runtime_guardrails.v2`.
    The guardrail summary derives from `scale_policy_v2`,
    `lod_snapshot_policy_v2`, and existing scale safety estimates. It reports
    configured counts, runtime limits, event/memory/stream backlog estimates,
    scale safety violations/risks, explicit `ALLOW` / `DEGRADE` / `REFUSE`
    decisions, runtime actions, and a no-Event-Kernel-change policy in backend
    derived summaries.
- V2-043: Add large detail pagination contract.
  - Scope: users, satellites, routes, services, compute nodes.
  - Depends on: V2-041.
  - Status: T237 adds backend-owned
    `leo_twin.large_detail_pagination_contract.v2` to backend derived
    summaries. The contract covers ground users, satellites, routes, services,
    and compute nodes with stable cursor semantics, endpoint metadata,
    recommended LOD-derived limits, hidden-row estimates, and no frontend-local
    pagination inference. The demo server now also exposes read-only cursor
    endpoints for routes, service lifecycle rows, and compute-node resource
    rows while preserving existing user, satellite, and combined-node endpoints.

### WS6. Dashboard and Frontend Product UX v3

Goal: turn the dashboard into a product observability surface.

Tasks:

- V2-050: Define dashboard information architecture v3.
  - Scope: overview, network, business, compute, node detail, assumptions,
    diagnostics.
  - Output: frontend structure and CSS tests.
  - Status: T225 adds backend-owned
    `dashboard_information_architecture_v3` to `backend_summary`, documents
    the seven-section dashboard structure, and adds frontend typing, display
    builder tests, runtime fixture checks, and a CSS style hook test.
- V2-051: Add user detail drawer.
  - Scope: active service, selected satellite, route, queue, latency timeline.
  - Depends on: V2-023, V2-013.
  - Status: T226 adds a deterministic user detail drawer v1 fallback view model
    from `user_request_summary_v1` rows. It groups selected-user details into
    business request, network/path/queue, and compute service sections while
    still preferring backend `node_detail_summary_v1` cards when available.
- V2-052: Add satellite detail drawer.
  - Scope: served users, next hops, compute resource vector, task queue,
    network KPIs, coverage summary.
  - Depends on: V2-023, V2-032.
  - Status: T227 adds a deterministic satellite detail drawer v1 fallback view
    model from satellite resource rows. It groups selected-satellite details
    into service/routing, compute resource pool, and network/task sections
    while still preferring backend `node_detail_summary_v1` cards when
    available.
- V2-053: Add virtualized large tables.
  - Scope: avoid rendering hundreds/thousands of rows directly.
  - Depends on: V2-043.
  - Status: T228 adds dashboard detail window policy v1. The dashboard now
    exposes the active user/satellite table render budget and verifies that
    1200-node scenarios render only the current bounded windows. True
    continuous virtual scrolling or backend cursor APIs remain follow-up work.
  - Status: T238 binds the standalone dashboard and App runtime detail refresh
    path to `leo_twin.large_detail_pagination_contract.v2`. The frontend now
    reads backend endpoint metadata and recommended limits for users,
    satellites, routes, services, and compute nodes, requests all six detail
    pages where available, prefers route cursor pages over bounded status
    summaries, and displays the backend pagination contract as the source of
    detail table budgets while preserving compatibility fallbacks.
  - Status: T239 renders the backend service lifecycle cursor page and
    compute-node resource cursor page as dedicated standalone dashboard
    tables. The dashboard now exposes service state, placement, network and
    compute latency splits, node resource vectors, and task counts from
    backend-owned detail pages without adding frontend-local model inference.
  - Status: T240 adds visible backend cursor controls for the service
    lifecycle and compute-node resource dashboard tables. The frontend keeps
    separate cursor state for these two backend pages, shows current row range,
    previous/next/refresh actions, and resets the cursors on config-version
    changes without altering backend pagination semantics.
  - Status: T241 extends visible backend cursor controls to user, satellite,
    and route detail pages. The dashboard detail refresh loop now preserves
    active cursors for all five visible detail collections while hiding cursor
    controls for legacy summaries that do not carry cursor metadata.
  - Status: T242 adds a backend-cursor-derived filter scope notice to the
    dashboard detail observability notes. Users can now see that current text
    and structured filters apply only to the loaded backend page and local
    render window until filter-aware backend cursor requests are implemented.
  - Status: T243 implements filter-aware backend cursor requests for user,
    satellite, and route detail pages. The backend applies filters before
    cursor pagination and the frontend sends active text/availability/business/
    bottleneck filters during refresh and page-turn actions.
- V2-054: Add model assumptions panel.
  - Scope: backend-derived model caveats, fidelity mode, KPI provenance.
  - Depends on: V2-003, V2-021.
  - Status: T229 adds a standalone dashboard model assumptions panel v1 that
    combines backend `model_assumptions`, runtime fidelity warnings, network
    KPI credibility, and configuration boundary labels without adding frontend
    model inference.

### WS7. 3D Scene Productization v2

Goal: improve visual understanding without changing simulation physics.

Tasks:

- V2-060: Add 3D asset manifest.
  - Scope: Earth texture, satellite models/icons, license/source hashes.
  - Status: T230 adds `leo_twin.3d_asset_manifest.v1` for the Cesium scene,
    covering the package-managed NaturalEarthII Earth texture, SHA-verified
    Natural Earth country boundaries, SHA-verified NASA Satellite Kit GLB
    model parts, and the project-generated satellite SVG icon. The Cesium
    layer summary now exposes the active asset manifest version and counts.
- V2-061: Add Earth visual policy v2.
  - Scope: opaque default, country borders, day/night optional, no far-side
    satellites through globe unless explicitly enabled.
  - Depends on: V2-060.
  - Status: T231 adds `leo_twin.earth_visual_policy.v2` as a deterministic
    frontend observation-layer policy. The 3D layer summary now reports the
    active opaque/transparent Earth mode, country-border visibility, far-side
    occlusion behavior, disabled day/night mode, and source asset manifest
    binding without changing simulation semantics.
- V2-062: Add selected-satellite coverage visualization v2.
  - Scope: deterministic footprint and honeycomb multi-beam visualization;
    no RF propagation.
  - Depends on: V2-061.
  - Status: T232 formalizes the existing selected-satellite coverage renderer
    as `leo_twin.selected_coverage_visual_policy.v2`. The 3D layer summary now
    exposes backend-derived footprint radius, bounded honeycomb beam count,
    selected-satellite-only detail mode, RF exclusions, and no-access-semantics
    boundaries.
- V2-063: Add selected-satellite camera/detail mode v2.
  - Scope: follow camera, inset, local motion trail, resource overlay.
  - Depends on: V2-052, V2-062.
  - Status: T233 formalizes the existing Earth/satellite camera toggle and
    selected-satellite inset as `leo_twin.satellite_camera_detail_policy.v2`.
    The 3D summary now reports active camera mode, selectable target count,
    target satellite, inset state, bounded local trail, coverage overlay, and
    compute-resource overlay availability without changing simulation
    semantics.

### WS8. Verification and Acceptance v2

Goal: make results reproducible and reviewable.

Tasks:

- V2-070: Define benchmark scenarios.
  - Scope: 72, 300, 1200 baseline configs with expected ranges.
  - Status: T217 adds backend-owned
    `leo_twin.benchmark_scenario_matrix.v1`, resolving the shipped 72/300/1200
    acceptance YAML files into deterministic scenario specs with expected
    fidelity modes, compact backend summaries, exact numeric guardrails, result
    artifact expectations, and acceptance command shapes.
- V2-071: Add model verification report template.
  - Scope: formulas, assumptions, boundary conditions, deterministic seed,
    expected outputs.
  - Depends on: V2-070.
  - Status: T218 adds
    `leo_twin.model_verification_report_template.v1`, a deterministic
    report-template service that consumes the benchmark scenario matrix plus
    network and compute contracts to produce per-scenario boundary conditions,
    determinism plans, formula checks, expected outputs, evidence checklists,
    known limitations, and review decision values.
- V2-072: Add benchmark acceptance tests.
  - Scope: deterministic summaries, KPI ranges, scale policy behavior.
  - Depends on: V2-070, V2-071.
  - Status: T219 adds benchmark acceptance tests that align the report
    template with the scenario matrix, verify deterministic backend summaries
    for the 72/300/1200 baselines, check scale policy behavior against matrix
    expectations, validate small-baseline runtime KPI safety ranges, and bind
    expected numeric ranges back to their config sources.
- V2-073: Add result package export.
  - Scope: config snapshot, events, metrics, summary, model assumptions,
    runtime logs.
  - Depends on: V2-071.
  - Status: T220 adds `leo_twin.result_package_contract.v1`, documenting the
    existing runtime export package routes and required artifacts
    (`config_snapshot.json`, `events.jsonl`, `metrics.csv`, `summary.json`,
    `manifest.json`). It also adds a package-record summary validator and a
    real integration export test that verifies the package satisfies the
    contract.

### WS9. Delivery and Operations v2

Goal: make the system usable by non-developer operators.

Tasks:

- V2-080: Add version and build info endpoint.
  - Scope: git commit, branch, frontend build, backend version.
  - Status: T221 adds `leo_twin.version_info.v1` and exposes it through
    `DemoControlPlane.version_info()`, `GET /runtime/version`, and `GET /version`.
    The payload reports backend/frontend versions, git commit/branch/dirty
    state, runtime diagnostics, endpoint list, and hard product constraints.
- V2-081: Add launcher health check v2.
  - Scope: port status, backend/frontend readiness, config path, log paths.
  - Status: T222 adds `leo_twin.launcher_health.v2`, a tested launcher health
    summary contract plus `scripts/sees_launcher.ps1 status -JsonSummary` and
    `health -JsonSummary`. The summary reports backend/frontend port and HTTP
    readiness, process ids, latest log paths, config paths, generated config
    path, and recommended actions.
- V2-082: Add operator diagnostics bundle.
  - Scope: logs, runtime status, latest config, stream diagnostics.
  - Depends on: V2-080, V2-081.
  - Status: T223 adds `leo_twin.operator_diagnostics_bundle.v1` and
    `scripts/collect_operator_diagnostics.ps1`. The collector writes launcher
    health, runtime status, version info, user config export, runtime export
    catalog, diagnostics manifest, and copied launcher logs under
    `artifacts\operator_diagnostics`.
- V2-083: Add user documentation v2.
  - Scope: quickstart, config guide, dashboard guide, troubleshooting.
  - Depends on: V2-001, V2-050, V2-081.
  - Status: T224 adds `docs/user_guide_v2.md` as the consolidated user-facing
    guide covering startup, health checks, configuration, console/dashboard
    usage, result export, diagnostics bundles, benchmark acceptance, and current
    model boundaries.

## 4. Sequencing

### Phase 0: V2 Contract Baseline

Purpose: establish stable contracts before implementation.

Serial tasks:

1. V2-001 user-facing config schema v2.
2. V2-010 service request contract v2.
3. V2-020 layered network model contract.
4. V2-030 compute resource vector v2.
5. V2-040 scale policy v2.

Parallel after initial contracts:

- V2-003 config explanation summary.
- V2-021 KPI provenance contract.
- V2-070 benchmark scenarios.
- V2-080 version/build endpoint.

Exit criteria:

- Contracts documented and tested.
- Frontend can display backend-owned assumptions without local inference.
- No Event Kernel changes.

### Phase 1: Trustworthy Runtime Semantics

Purpose: make live behavior explainable.

Parallel lanes:

- Business lane: V2-011, V2-012, V2-013.
- Network lane: V2-022, V2-023.
- Compute lane: V2-031, V2-032.
- Scale lane: V2-041, V2-042, V2-043.

Integration tasks:

1. Connect service lifecycle to network and compute timelines.
2. Expose user/satellite detail records with backend-owned semantics.
3. Add deterministic acceptance tests for 72, 300, and 1200 scenarios.

Exit criteria:

- KPI movement can be explained by backend provenance fields.
- User and satellite detail rows are traceable to runtime service/network/compute
  state.
- 1200-node responsiveness is preserved.

### Phase 2: Product Observability Surfaces

Purpose: turn runtime semantics into usable product UI.

Serial tasks:

1. V2-050 dashboard information architecture v3.
2. V2-054 model assumptions panel.
3. V2-051 user detail drawer.
4. V2-052 satellite detail drawer.
5. V2-053 virtualized large tables.

Parallel visual lane:

- V2-060, V2-061, V2-062, V2-063.

Exit criteria:

- Dashboard has clear levels: overview, network, business, compute, detail,
  assumptions, diagnostics.
- 3D scene supports selected-satellite coverage and resource inspection.
- Large scenarios do not block browser interaction.

### Phase 3: Verification, Export, and Operations

Purpose: make runs reproducible and deliverable.

Serial tasks:

1. V2-071 verification report template.
2. V2-072 benchmark acceptance tests.
3. V2-073 result package export.
4. V2-081 launcher health check v2.
5. V2-082 diagnostics bundle.
6. V2-083 user documentation v2.

Exit criteria:

- A user can run a scenario, export a reproducible package, and inspect model
  assumptions and KPI provenance.
- Operator can diagnose service startup and runtime issues without reading code.

## 5. Parallel Agent Assignment Model

- Kernel Agent: guard Event Kernel boundaries; review that no domain behavior
  enters kernel.
- Orbit Agent: constellation allocation, orbit state summaries, visual coverage
  contracts.
- Network Agent: layered network contracts, route explanations, KPI provenance,
  bounded ISL behavior.
- Compute Agent: resource vector, service placement, task queue, execution
  timeline.
- Metrics Agent: KPI formulas, benchmark ranges, result export summaries.
- Frontend Agent: dashboard IA, detail drawers, virtual tables, 3D visual
  binding to backend summaries.
- Ops Agent: launcher, health checks, diagnostics bundle, documentation.

Agents may work in parallel only when write scopes are disjoint. Integration
tasks must be serialized through contracts and tests.

## 6. First Execution Batch

Recommended first commits:

1. V2-001 Product Configuration Schema v2
   - Files likely touched: `src/leo_twin/configuration/*`, config templates,
     tests, docs.
   - Reason: every later task needs stable user configuration semantics.
2. V2-020 Network Model Contract v2
   - Files likely touched: schema/docs/tests only.
   - Reason: KPI trust requires model-layer definitions before formulas.
3. V2-030 Compute Resource Vector v2
   - Files likely touched: schema/models/tests/docs.
   - Reason: service lifecycle and satellite detail drawers depend on this.
4. V2-070 Benchmark Scenario Matrix v1
   - Files likely touched: docs/config templates/tests.
   - Reason: acceptance gates should exist before broad behavior changes.

Do not start frontend dashboard v3 until at least one backend summary contract
is available. Do not start high-scale 3000+ runtime work until V2-040 defines
the fidelity policy and guardrails.

## 7. Definition of Done for V2 Tasks

Every task must include:

- deterministic tests;
- development log entry;
- explicit changed-file scope;
- no unrelated runtime config commits;
- no Event Kernel domain changes;
- source-of-truth backend semantics when UI text depends on model behavior;
- pushed GitHub branch.

For model-affecting tasks, also include:

- assumptions;
- formula inputs;
- known limitations;
- benchmark or acceptance scenario impact.
