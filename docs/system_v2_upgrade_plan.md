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
    `POST /scenario/user-config/validate`; guarded frontend upload/apply is
    still pending.

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
- V2-022: Add time-varying flow-level network pressure.
  - Scope: deterministic demand/capacity pressure, route blocking, congestion
    proxy, loss proxy, delay variation proxy.
  - Output: tests proving KPI movement under stress and stability under low load.
  - Depends on: V2-021.
- V2-023: Add route explanation records.
  - Scope: selected route, alternative count, bottleneck reason, next hop,
    blocked reason.
  - Output: backend-owned detail rows for users/satellites.
  - Depends on: V2-022.

### WS4. Compute Network Model v2

Goal: represent satellites as product-grade compute nodes and resource pools.

Tasks:

- V2-030: Stabilize compute resource vector v2.
  - Scope: FP32, FP64, FP16, INT8, memory, storage, compatibility rules.
  - Output: schema docs and unit tests.
- V2-031: Add service placement model.
  - Scope: deterministic service-to-satellite placement, capacity check,
    queue state, rejection reason.
  - Depends on: V2-030.
- V2-032: Add task queue and execution timeline v2.
  - Scope: queue delay, execution delay, resource bottleneck, deadline status.
  - Depends on: V2-031.
- V2-033: Add cache/offload/migration contracts.
  - Scope: contracts and observability only; behavior can be later.
  - Depends on: V2-032.

### WS5. Runtime Scale and Stability v2

Goal: keep large-scale scenarios responsive and transparent.

Tasks:

- V2-040: Define scale policy v2.
  - Scope: 72, 300, 1200, 3000, 6000, 12000 profile rules.
  - Output: fidelity summary, explicit frontend notices, tests.
- V2-041: Add LOD snapshot policy.
  - Scope: detail windows, top-K summaries, sampled histories, raw counts.
  - Depends on: V2-040.
- V2-042: Add runtime guardrails.
  - Scope: event volume estimate, memory estimate, stream backlog estimate,
    explicit refusal/degrade reason.
  - Depends on: V2-040.
- V2-043: Add large detail pagination contract.
  - Scope: users, satellites, routes, services, compute nodes.
  - Depends on: V2-041.

### WS6. Dashboard and Frontend Product UX v3

Goal: turn the dashboard into a product observability surface.

Tasks:

- V2-050: Define dashboard information architecture v3.
  - Scope: overview, network, business, compute, node detail, assumptions,
    diagnostics.
  - Output: frontend structure and CSS tests.
- V2-051: Add user detail drawer.
  - Scope: active service, selected satellite, route, queue, latency timeline.
  - Depends on: V2-023, V2-013.
- V2-052: Add satellite detail drawer.
  - Scope: served users, next hops, compute resource vector, task queue,
    network KPIs, coverage summary.
  - Depends on: V2-023, V2-032.
- V2-053: Add virtualized large tables.
  - Scope: avoid rendering hundreds/thousands of rows directly.
  - Depends on: V2-043.
- V2-054: Add model assumptions panel.
  - Scope: backend-derived model caveats, fidelity mode, KPI provenance.
  - Depends on: V2-003, V2-021.

### WS7. 3D Scene Productization v2

Goal: improve visual understanding without changing simulation physics.

Tasks:

- V2-060: Add 3D asset manifest.
  - Scope: Earth texture, satellite models/icons, license/source hashes.
- V2-061: Add Earth visual policy v2.
  - Scope: opaque default, country borders, day/night optional, no far-side
    satellites through globe unless explicitly enabled.
  - Depends on: V2-060.
- V2-062: Add selected-satellite coverage visualization v2.
  - Scope: deterministic footprint and honeycomb multi-beam visualization;
    no RF propagation.
  - Depends on: V2-061.
- V2-063: Add selected-satellite camera/detail mode v2.
  - Scope: follow camera, inset, local motion trail, resource overlay.
  - Depends on: V2-052, V2-062.

### WS8. Verification and Acceptance v2

Goal: make results reproducible and reviewable.

Tasks:

- V2-070: Define benchmark scenarios.
  - Scope: 72, 300, 1200 baseline configs with expected ranges.
- V2-071: Add model verification report template.
  - Scope: formulas, assumptions, boundary conditions, deterministic seed,
    expected outputs.
  - Depends on: V2-070.
- V2-072: Add benchmark acceptance tests.
  - Scope: deterministic summaries, KPI ranges, scale policy behavior.
  - Depends on: V2-070, V2-071.
- V2-073: Add result package export.
  - Scope: config snapshot, events, metrics, summary, model assumptions,
    runtime logs.
  - Depends on: V2-071.

### WS9. Delivery and Operations v2

Goal: make the system usable by non-developer operators.

Tasks:

- V2-080: Add version and build info endpoint.
  - Scope: git commit, branch, frontend build, backend version.
- V2-081: Add launcher health check v2.
  - Scope: port status, backend/frontend readiness, config path, log paths.
- V2-082: Add operator diagnostics bundle.
  - Scope: logs, runtime status, latest config, stream diagnostics.
  - Depends on: V2-080, V2-081.
- V2-083: Add user documentation v2.
  - Scope: quickstart, config guide, dashboard guide, troubleshooting.
  - Depends on: V2-001, V2-050, V2-081.

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
