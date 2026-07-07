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
  - Status: T166 implements the backend-owned user configuration schema v2 for
    the full `SEESConfig` surface, including deterministic field paths,
    defaults/current values, enum values, numeric constraints, key-control vs
    detailed-file edit surfaces, template references, accepted/rejected
    examples, and validation reporting. T320 adds backend-owned
    `USER_CONFIGURATION_REFERENCE_V1` through `GET
    /scenario/user-config/reference`. The reference binds schema v2, key UI
    fields, detailed file-only fields, template profiles, validation/apply
    workflow, and model boundaries into one stable configuration reference
    object for users and frontend surfaces.
    T321 binds that reference into the standalone dashboard configuration
    contract card so the frontend displays the backend-owned reference hash,
    file-only field count, and reference link rather than deriving the
    advanced configuration explanation locally.
    T322 adds a scrollable in-dashboard reference browser for the same backend
    object, covering sections, field rows, edit surfaces, current/default
    values, validation rules, model boundaries, and workflow notes. T371 adds
    backend-owned user configuration template validation evidence, so approved
    YAML templates are loaded through the same config loader and schema
    validation path used by runtime control and are reported with stable file
    hashes, normalized config hashes, scale summaries, and model-boundary
    declarations. T373 persists the same backend-owned template validation
    evidence into runtime result packages as
    `user_configuration_template_validation_v1.json`, so offline review uses
    the exported package as the source of truth and does not reload templates
    or apply a new config.
- V2-002: Add template catalog metadata.
  - Scope: scenario name, purpose, scale, expected KPI behavior, fidelity mode.
  - Output: backend template endpoint and frontend selector metadata.
  - Depends on: V2-001.
  - Status: T251 extends backend-approved user configuration template profiles
    with scale, expected KPI behavior, fidelity mode, and recommended-use
    metadata, exposes the fields through schema/templates/configuration-surface
    summaries, and displays them in the frontend template selector without
    local semantic inference. T371 adds the
    `/scenario/user-config/template-validation` read-only endpoint and embeds
    the same evidence in the template catalog/reference surfaces so operators
    can see how many approved templates are executable before applying one.
    T372 renders the backend evidence as a dashboard template-validation table
    with per-template status, scale/runtime summary, orbit/space-link mode,
    file hash, config hash, and error summary without revalidating templates in
    the browser. T373 adds compact export-review labels for the same evidence
    through review summary, diagnostics, scenario review, and audit index
    package surfaces. T374 connects the scenario-review workflow rows to the
    existing read-only package artifact inspector and defaults
    `user_configuration_template_validation_v1.json` to
    `/template_validation/templates`, so offline package review can inspect
    exported template rows without frontend validation or runtime mutation.
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
  - Status: T193 exposes read-only backend configuration contract endpoints
    for schema, template catalog, and current effective config export; T194
    binds the dashboard to those read-only schema/template/export links.
    Preflight validation API implemented in T198 as `POST
    /scenario/user-config/validate`; dashboard JSON preflight UI implemented
    in T199; guarded preflight-to-apply flow implemented in T200 by sending
    backend-normalized config through explicit `CONFIG_UPDATE`; backend
    preflight diff summary implemented in T201; dashboard diff rendering
    implemented in T202; backend/runtime apply readiness and dashboard
    readiness rendering implemented in T203; backend JSON/YAML text preflight
    endpoint implemented in T204; dashboard JSON/YAML text preflight mode
    implemented in T205. Direct file-picker upload remains a future UI
    hardening item; the current workflow supports text preflight and explicit
    apply.

### WS2. Business Demand Model v2

Goal: model user demand as traceable communication and compute services.

Tasks:

- V2-010: Define service request contract v2.
  - Scope: service id, user id, class, priority, destination policy, input size,
    output size, duration, deadline, retry policy, generated flow/task ids.
  - Output: schema/tests only.
  - Status: T252 adds `leo_twin.service_request_contract.v2` as a schema-level
    product contract. It defines supported service classes, required/reserved
    service request fields, deterministic generated flow/task/output id
    policies, current `TrafficDemandRecord` runtime mapping, and explicit
    exclusions for packet traffic, stochastic retry, deadline scheduling, and
    external simulators.
- V2-011: Add deterministic arrival profile model.
  - Scope: periodic, burst, diurnal, and region-weighted arrivals using seed.
  - Output: unit tests for identical seed and config.
  - Depends on: V2-010.
  - Status: T253 extends `TrafficDemandProfile` with
    `TrafficArrivalProfile` values `PERIODIC`, `BURST`, `DIURNAL`, and
    `REGION_WEIGHTED`. It preserves periodic defaults, adds deterministic burst
    grouping, diurnal inter-arrival variation, seeded weighted source/
    destination selection, and unit tests for deterministic replay.
- V2-012: Add service mix profiles.
  - Scope: telemetry, bulk downlink, data transfer, compute service, emergency.
  - Output: summary counts and per-user active service state.
  - Depends on: V2-010, V2-011.
  - Status: T254 adds `EMERGENCY` as a deterministic flow-level service class,
    propagates `emergency_weight` through user config, scenario builder,
    integration demo, backend-derived summaries, and service request contracts,
    and adds `TrafficDemandBatch.service_mix_summary()` with per-user active
    service state rows. T326 adds runtime
    `user_service_request_summary_v2` as a backend-owned per-user
    communication/compute request state summary. The dashboard now prefers the
    v2 runtime status object when no server-side user detail page is active,
    while retaining `user_request_summary_v1` compatibility. T327 extends the
    existing `/runtime/details/users` cursor endpoint with
    `summary_version=v2`, allowing the standalone dashboard to request
    server-side paginated v2 user service request pages while the default v1
    endpoint remains backward compatible. T328 adds
    `user_service_request_summary_v2.json` as a bounded runtime export artifact
    so offline result packages can review the same backend-owned per-user
    service request semantics without live runtime lookup or service
    recomputation. T329 binds that artifact evidence into the standalone
    dashboard export review surfaces: review summary, diagnostics, scenario
    review workflow, and audit-index sections now display backend-provided
    request counts, exported-window counts, hidden counts, and evidence hashes.
    T330 adds a read-only dashboard artifact view for
    `user_service_request_summary_v2.json`, loading the persisted package file
    and reusing the live v2 user-service table semantics for offline
    per-user request review. T331 adds the package-owned
    `/runtime/export/packages/{package_id}/user-service-requests` page endpoint
    and binds the dashboard export review drawer to backend cursor reads,
    service-class filtering, terminal-state filtering, and network-waiting
    filtering so large user-service artifacts are not loaded fully in the
    browser by default. T375 adds
    `leo_twin.traffic_demand_explanation.v1` on `TrafficDemandBatch`, a
    deterministic product-facing explanation of generated request counts,
    active traffic classes, data volumes, priority range, compute-service
    correlation completeness, arrival window, and per-user active service
    state without changing flow generation or event scheduling. T376 exposes
    that explanation as
    `backend_summary.traffic_demand_explanation_v1`, derived from backend
    traffic configuration and capped with explicit request/endpoint window
    policy for large payloads, so frontend surfaces can use backend-owned
    business semantics rather than recomputing demand meaning locally. T377
    persists the same backend-owned explanation into runtime result packages as
    `traffic_demand_explanation_v1.json` and binds its request counts,
    compute-service counts, frontend-inference flag, and evidence hash into
    review summary, diagnostics, scenario review, and audit index artifacts
    without traffic regeneration or event replay. T378 adds the dashboard
    scenario-review workflow entry for that artifact, opening
    `traffic_demand_explanation_v1.json` in the existing read-only JSON
    inspector at `/traffic_demand_explanation` and surfacing backend-owned
    request/evidence labels without browser-side demand recomputation. T379
    adds a compact dashboard artifact card for the same file, displaying
    configured/explained requests, input flows, tasks, output flows, class rows,
    per-user state count, compute-service correlation status, packet-level flag,
    frontend-inference flag, and evidence hash from the persisted artifact
    before the raw JSON preview. T380 extends that compact card with bounded
    per-user demand rows from exported `per_user_active_service_state` data and
    reuses the artifact filter for user-level inspection without frontend
    demand regeneration. T381 adds the package-owned
    `/runtime/export/packages/{package_id}/traffic-demand-users` cursor
    endpoint and frontend API contract so per-user traffic-demand rows can be
    paged and filtered by query/traffic class from persisted package evidence
    without traffic regeneration, event replay, or package mutation. T382 binds
    the dashboard compact traffic-demand card to that backend page, using the
    artifact filter as the page query and falling back to the bounded artifact
    preview only while the backend page is loading or unavailable. T383 adds
    previous/next controls for that backend page inside the compact card, so
    operators can inspect more than the first bounded traffic-demand user page
    without loading the full JSON artifact. T332 preserves
    backend-provided request/route/flow/task
    correlation ids in dashboard user-service rows and lets selected export
    package rows drive package route evidence, package service-trace filtering,
    and live runtime detail lookups without frontend business recomputation.
    T333 adds backend-owned `trace_id` correlation to user-service request rows,
    propagates it through runtime export package pages, and lets dashboard
    navigation open exact service lifecycle trace details when the current
    runtime exposes the matching trace. T334 adds the package-owned exact
    service trace endpoint
    `/runtime/export/packages/{package_id}/service-traces/{trace_id}` and binds
    dashboard package review selections to that artifact-owned item, so an
    exported user-service or service-trace row can open deterministic trace
    evidence without live runtime availability, event replay, service
    recomputation, or package mutation. T335 adds a field-level package-vs-live
    service trace comparison card for the same selected trace, separating
    artifact-owned evidence from optional current-runtime drift checks. T336
    persists selected service trace comparison outcomes as
    `service_trace_comparison_review_report_v1.json`, updates the export
    catalog/audit/handoff artifacts, and lets the dashboard save and reload the
    report without event replay or service recomputation. T337 adds a
    backend-generated `detail_hash` to live exact service trace details, so
    saved package-vs-live service trace reports can cite both the package item
    hash and the live detail hash. T338 adds a backend cursor page for saved
    service trace comparison review report records and binds the dashboard
    review card to that backend page, so large reports can be inspected without
    loading the whole JSON artifact for row navigation. T339 records saved
    service trace comparison review reports in the audit index, package review
    completion evidence, handoff Markdown report, and dashboard audit drawer.
    T340 adds the service lifecycle trace and saved service trace comparison
    review report to the backend-guided scenario review checklist flow, and the
    dashboard uses the audit-index report hash as the checklist evidence hash.
    T341 adds backend-owned checklist recommended-step completeness fields and
    makes handoff readiness require full recommended review coverage, not only
    all submitted records being marked reviewed. T342 adds the backend
    `scenario-review-checklist-template` endpoint and dashboard binding so all
    recommended review rows and evidence hashes are prefilled by backend output
    before the operator edits statuses and notes. T343 adds a read-only
    `scenario-review-checklist-template-comparison` endpoint and dashboard
    status display so saved operator checklists can be compared against the
    latest backend template for missing records, evidence-hash drift, operator
    attention, and extra stale records without replay or recomputation.
- V2-013: Add service lifecycle trace.
  - Scope: input flow, queue, compute, output flow, terminal state.
  - Output: timeline records for dashboard and result export.
  - Depends on: V2-012 and compute lifecycle work.
  - Status: T255 adds `leo_twin.service_lifecycle_trace_contract.v2` and
    exposes `service_lifecycle_trace_v2` from runtime observability. The trace
    is derived from `service_latency_history_v1` and reports input network,
    compute queue, compute execution, output network, and terminal state
    fields without changing Event Kernel, network routing, or compute
    scheduling. T256 adds `service_lifecycle_trace_v2.json` as a standalone
    runtime export artifact so offline result packages can inspect the same
    backend-owned lifecycle trace without parsing `config_snapshot.json`. T257
    binds `service_lifecycle_trace_v2` into the standalone dashboard service
    section as backend-owned trace rows and stage segments. T258 adds selectable
    service trace rows and a correlation inspector that links one trace to
    visible user, route, satellite, and compute-node context through backend
    flow ids, route ids, and compute node ids. T259 adds
    `/runtime/details/service-traces/{trace_id}` so a selected trace can fetch
    backend-owned exact context even when correlated rows are outside the
    current dashboard window. T260 binds the dashboard selection path to that
    exact-detail API and displays backend-owned correlation ids first, with the
    existing visible-window correlation retained as a loading/error fallback.
    T261 adds a service trace card to the dashboard detail drawer so the same
    backend exact detail can show lifecycle components, correlation ids,
    bounded route explanations, backend user/satellite cards, and compute-node
    resource context in scrollable sections. T262 adds local service trace
    browser filters for keyword, backend terminal state, and compute-node id so
    users can locate a communication-compute lifecycle without paging through
    unrelated trace rows. T263 adds the backend cursor endpoint
    `/runtime/details/service-traces` plus service-trace collection metadata in
    `leo_twin.large_detail_pagination_contract.v2`, allowing server-side
    filtering by query, raw terminal state, and compute-node id. T264 binds the
    dashboard service trace browser controls and pager to that server cursor
    endpoint while retaining local filtering as a temporary fallback. T265
    extends the same backend cursor endpoint with `stage_kind` and
    `terminal_reason` filters so lifecycle-stage and terminal-reason narrowing
    happens before cursor slicing. T266 binds those filters into the
    standalone dashboard service trace browser and preserves the existing
    server cursor reset behavior. T297 loads package-owned
    `service_lifecycle_trace_v2.json` in the dashboard export review area so
    offline result packages can inspect communication-compute service chain
    evidence without replaying the simulation. T298 adds local artifact
    filtering and deterministic local page controls to that export review card
    for trace text, terminal state, compute node, lifecycle stage, and terminal
    reason while keeping the exported package read-only. T299 adds
    `/runtime/export/packages/{package_id}/service-traces` so persisted result
    packages can serve deterministic backend pages over their exported
    `service_lifecycle_trace_v2.json` artifact window without current-runtime
    lookup, event replay, service recomputation, or package mutation. T300
    binds the dashboard export service trace review card to that backend page
    endpoint so filter and cursor actions no longer require loading the full
    service trace JSON artifact in the browser. T301 adds
    `runtime_export_service_trace_policy_v1` so result packages explicitly
    record the service trace export limit, exported trace count, hidden trace
    count, artifact-window-only boundary, and no-replay/no-recompute policy.
    T334 adds `RUNTIME_EXPORT_SERVICE_TRACE_ITEM_V1` and the package-owned
    exact trace item read path, allowing a selected exported trace to be opened
    as a deterministic package artifact detail while preserving the live exact
    trace API only as optional current-runtime comparison context. T335 renders
    that context as an explicit package/live service trace comparison with
    matched and different lifecycle fields, plus loading/error/mismatch status
    notes when one side of the evidence is unavailable. T336 adds the
    backend-served service trace comparison review report save path and binds
    the dashboard save action to the persisted package artifact, closing the
    review loop from trace evidence to saved operator report. T337 fills the
    remaining live evidence gap by carrying the live exact service trace
    `detail_hash` into saved review records. T338 adds the saved report records
    page endpoint and dashboard row browser for backend-driven review paging.
    T339 promotes the saved service trace report into backend audit/completion
    evidence while keeping missing reports optional for compatibility.

### WS3. Network Semantics and KPI Trust v2

Goal: make throughput, latency, loss, and jitter explainable.

Tasks:

- V2-020: Document layered network model contract.
  - Scope: application, transport, routing, data link, channel abstraction.
  - Output: docs and schema enums; no behavior rewrite.
  - Status: T167 implements `leo_twin.network_model_contract.v2` as a
    product-level layered network contract. It documents application,
    transport, network/routing, data-link, physical terminal, and channel
    abstraction boundaries, exposes deterministic KPI semantic contracts
    through `network_model_contract_v2_to_dict()`, publishes
    `docs/network_model_contract_v2.md`, and verifies the contract with
    `tests/unit/test_network_model_contract_v2.py` without changing Event
    Kernel behavior or runtime packet-level fidelity.
- V2-021: Add KPI provenance contract v2.
  - Scope: formula inputs for throughput, latency, loss proxy, jitter proxy.
  - Output: backend `network_kpi_provenance_v2`.
  - Depends on: V2-020.
  - Status: T168 implements `network_kpi_provenance_v2` in runtime status,
    binding existing `metrics_summary` values to
    `leo_twin.network_model_contract.v2` with current KPI values, runtime
    summary keys, layer ownership, formula summaries, source-field values,
    dominant observed source, zero reasons, and explicit non-packet semantics.
    Backend `network_kpi_credibility_v1` coverage/trust summary implemented in
    T206; standalone dashboard trust card bound to backend credibility fields in T207.
    T273 renders `network_kpi_provenance_v2.kpis` as a dashboard formula
    inspector with runtime value, layer, observed source, formula summary,
    source-field coverage, and zero-value semantics per KPI.
    T323 adds backend-owned `formula_inputs` and `formula_trace` to each KPI
    provenance item, and the dashboard displays the input audit and current
    selection trace so KPI movement can be explained from backend values.
    T369 adds backend-owned `network_kpi_formula_evidence_v1`, joining KPI
    provenance and KPI calibration into a compact formula/input/time-series
    evidence summary that the dashboard renders without local semantic
    inference. T370 exports the same formula evidence into
    `network_kpi_formula_evidence_v1.json` and surfaces compact status/hash
    labels in result-package review, diagnostics, scenario review, and audit
    sections. T384 adds backend-owned
    `network_kpi_variation_explanation_v1`, derived from KPI formula evidence
    and KPI calibration, so the dashboard can explain why each flow-level KPI
    moved or stayed flat without recomputing KPI semantics locally. T385
    exports the same variation explanation into
    `network_kpi_variation_explanation_v1.json` and surfaces compact
    status/hash labels in result-package review, diagnostics, scenario review,
    and audit sections.
- V2-022: Add time-varying flow-level network pressure.
  - Scope: deterministic demand/capacity pressure, route blocking, congestion
    proxy, loss proxy, delay variation proxy.
  - Output: tests proving KPI movement under stress and stability under low load.
  - Depends on: V2-021.
  - Status: deterministic simulation-time pressure factor and tail-sample
    decomposition implemented in T208.
    T324 adds backend-owned `network_kpi_benchmark_validation_v1`, derived from
    `metrics_summary` and `network_kpi_provenance_v2`, and binds the dashboard
    to the PASS/WARN/FAIL/INSUFFICIENT_DATA guardrail summary for demo
    acceptance. T325 exports the same guardrail evidence into
    `network_kpi_benchmark_validation_v1.json` and surfaces compact status/hash
    labels in result-package review, diagnostics, scenario review, and audit
    sections so offline packages preserve KPI validation evidence.
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
  - Status: T275 adds backend-owned `route_provenance_trust_summary_v1`, derived
    from `route_explanation_summary_v1`, and binds it into the dashboard model
    trust evidence workspace. It reports route explanation coverage, path and
    next-hop context coverage, bottleneck components, hidden route windows, and
    flow-level route proxy caveats without recomputing routes.
  - Status: T276 adds benchmark acceptance for route trust across the standard
    72/300/1200 scenarios and records the runtime status expectation in the
    benchmark matrix and model verification report template.
  - Status: T277 indexes the same route trust evidence into runtime export
    `review_summary_v1.json` and `diagnostics_bundle_v1.json`, so result
    packages can be reviewed without manually searching the full
    `config_snapshot.status` object.
  - Status: T278 adds `route_detail_index_v1.json` to runtime result packages.
    The artifact preserves the exported route explanation window,
    route-trust sample route ids, indexed route ids, and compact route evidence
    rows without recomputing paths or adding packet-level behavior.
  - Status: T279 loads `route_detail_index_v1.json` in the standalone
    dashboard export review surface and renders indexed route counts,
    route-trust sample coverage, model-boundary labels, and sample route rows.
  - Status: T280 adds route evidence search and row actions that request the
    existing live route detail endpoint for the selected route id, without
    recomputing paths or mutating exported packages.
  - Status: T281 adds package-owned route evidence query endpoints for
    persisted result packages. `/runtime/export/packages/{package_id}/routes`
    and `/runtime/export/packages/{package_id}/routes/{route_id}` read
    `route_detail_index_v1.json` directly and return deterministic package
    review JSON without depending on the current runtime session.
  - Status: T282 rebuilds the package route evidence window during runtime
    export with the existing detail endpoint max limit of 5000 rows. The export
    policy is recorded in `runtime_export_route_detail_policy_v1` and
    `route_detail_index_v1.json`, while `/runtime/status` remains lightweight.
  - Status: T283 changes the standalone dashboard route evidence drawer to load
    `/runtime/export/packages/{package_id}/routes` pages by default. Search
    requests now use backend package filters, and the full
    `route_detail_index_v1.json` artifact remains a direct review link rather
    than a default frontend payload.
  - Status: T284 adds cursor previous/next controls and availability, business,
    and bottleneck filters to the dashboard package route evidence drawer. The
    controls call the package-owned route page endpoint instead of filtering
    locally.
  - Status: T285 adds package-owned exact route detail rendering to the
    dashboard export review drawer. Selected package route rows now load
    `/runtime/export/packages/{package_id}/routes/{route_id}` and display the
    exported route evidence separately from live runtime route-detail
    comparison.
  - Status: T286 adds a package-vs-live route comparison card in the dashboard
    export review drawer. When the selected package route detail and live
    runtime route detail share the same route id, the frontend compares
    availability, business, path, next hop, KPI proxy, pressure, and bottleneck
    fields without recomputing routes.
  - Status: T287 adds a `compare with live` row action to package route
    evidence. The action loads package-owned route detail and live runtime
    route detail for the selected route id together, then lets the T286
    comparison card render the field-level result.
  - Status: T288 adds package-vs-live comparison status diagnostics. When the
    comparison card is not available, the dashboard explains whether it is
    waiting on package detail, waiting on live detail, blocked by an error, or
    comparing mismatched route ids.
  - Status: T289 adds backend-owned `route_comparison_review` metadata to
    review summaries, diagnostics bundles, route detail indexes, route pages,
    and exact package route detail items. The metadata records comparison
    endpoints, compared fields, live-runtime requirements, status reasons, and
    no-recompute/no-replay boundaries.
  - Status: T290 adds the backend-declared
    `RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1` report template and
    deterministic record builder for selected package-vs-live route comparison
    outcomes. The dashboard consumes the backend report template label; it does
    not infer report schema locally.
  - Status: T291 adds the package-level
    `POST /runtime/export/packages/{package_id}/route-comparison-review-report`
    save path. The backend persists
    `route_comparison_review_report_v1.json`, updates the export catalog, and
    the frontend API layer can post selected review records without changing
    dashboard layout.
  - Status: T292 adds a dashboard save action on the package-vs-live route
    comparison card. The action converts the visible comparison rows into the
    backend report record schema and posts them to the T291 save endpoint,
    preserving backend ownership of the artifact.
  - Status: T293 adds backend-generated `detail_hash` to live route detail
    rows. Dashboard-saved route comparison review reports now include both the
    package route detail hash and live route detail hash.
  - Status: T294 surfaces the saved
    `route_comparison_review_report_v1.json` artifact in the dashboard package
    review area from the backend export catalog, including the direct JSON link,
    file hash, and latest saved report hash.
  - Status: T295 loads the saved route comparison review report artifact as a
    read-only dashboard drawer and summarizes record counts, status totals,
    route detail hash pairs, and operator notes without route recomputation.
  - Status: T296 adds local status filtering, text search, and offset
    pagination to the saved route comparison review report drawer so large
    report artifacts can be inspected without opening raw JSON.
  - Status: T306 records backend restore-preflight boundary alignment evidence
    in `route_comparison_review_report_v1.json`, including alignment hash,
    status, warnings, and runtime export boundary hash. The dashboard summary
    shows these fields so archived operator route reviews can cite the exact
    compare/preflight boundary evidence used during save.
  - Status: T307 adds `export_package_audit_index_v1.json` as a backend-owned
    long-term audit index. It summarizes manifest hash, runtime export boundary
    hash, boundary alignment hash/status, review summary hash, diagnostics
    hash, optional route review report hash, and package artifact file hashes.
    The index is regenerated after route review report save and is surfaced in
    the dashboard package review area through the export catalog.
  - Status: T308 loads `export_package_audit_index_v1.json` into the dashboard
    package review area as a dedicated audit drawer. The drawer groups manifest,
    boundary alignment, diagnostics, route review report, and artifact hash
    evidence and refreshes after route comparison review report save.
  - Status: T309 binds backend user configuration export evidence into
    `export_package_audit_index_v1.json`. The audit index now records the user
    configuration schema id, config hash, export hash, validation status, and
    deterministic binding hash. The dashboard audit drawer displays these
    fields as a Configuration evidence section without deriving configuration
    semantics locally.

### WS4. Compute Network Model v2

Goal: represent satellites as product-grade compute nodes and resource pools.

Tasks:

- V2-030: Stabilize compute resource vector v2.
  - Scope: FP32, FP64, FP16, INT8, memory, storage, compatibility rules.
  - Output: schema docs and unit tests.
  - Status: T169 implements `leo_twin.compute_resource_contract.v2`,
    formalizing satellite-hosted `ComputeResourceVector` lanes, task demand
    lanes, legacy scalar compatibility, deterministic bottleneck service-time
    estimation, memory/storage capacity-limit semantics, excluded
    real-execution semantics, and configured per-node resource profiles in
    backend-derived summaries. T213 adds backend-owned bottleneck resource,
    utilization, available/used/total, and pressure status fields to runtime
    metrics, with the standalone dashboard consuming those fields instead of
    inferring bottlenecks locally.
- V2-031: Add service placement model.
  - Scope: deterministic service-to-satellite placement, capacity check,
    queue state, rejection reason.
  - Depends on: V2-030.
  - Status: T170 adds the deterministic service placement contract and pure
    model for selecting satellite-hosted compute nodes by minimum estimated
    finish time with deterministic tie-breaks, explicit queue state, queue and
    execution delay, and canonical rejection reasons. T171 connects the
    route-aware compute runtime to that placement model and carries placement
    metadata into service latency history and user request summaries. T214 adds
    a bounded backend-owned candidate queue observability label to service
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
  - Status: T245 adds backend detail-by-id support for selected users. The
    dashboard now requests `GET /runtime/details/users/<user_id>` on row
    selection and prefers that exact backend-owned detail card over bounded
    window summaries or frontend fallback rows.
- V2-052: Add satellite detail drawer.
  - Scope: served users, next hops, compute resource vector, task queue,
    network KPIs, coverage summary.
  - Depends on: V2-023, V2-032.
  - Status: T227 adds a deterministic satellite detail drawer v1 fallback view
    model from satellite resource rows. It groups selected-satellite details
    into service/routing, compute resource pool, and network/task sections
    while still preferring backend `node_detail_summary_v1` cards when
    available.
  - Status: T245 adds backend detail-by-id support for selected satellites.
    The dashboard now requests `GET /runtime/details/satellites/<satellite_id>`
    on row selection and prefers that exact backend-owned detail card over
    bounded window summaries or frontend fallback rows.
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
  - Status: T244 extends filter-aware backend cursor requests to service
    lifecycle and compute-node resource detail pages. The dashboard now has
    backend text filters for all five visible detail collections, with filters
    applied before cursor pagination.
  - Status: T246 adds backend detail-by-id endpoints and frontend API loaders
    for routes, service lifecycle rows, and compute-node resource rows:
    `/runtime/details/routes/<route_id>`,
    `/runtime/details/services/<service_id>`, and
    `/runtime/details/compute-nodes/<node_id>`. The exact detail response
    reuses the same backend-owned row shape as the corresponding cursor page
    and preserves existing dashboard layout and cursor endpoints.
  - Status: T247 binds those exact detail APIs into the standalone dashboard.
    Route, service lifecycle, and compute-node detail rows are now selectable;
    the dashboard requests the backend exact row on selection and prefers it
    over the current cursor-window fallback in small exact-detail inspector
    cards.
  - Status: T248 adds visible exact-detail request status for users,
    satellites, routes, services, and compute nodes. The dashboard now shows
    backend exact-detail loading, synchronized, and error states from App-owned
    request state while ignoring stale status for previously selected entities.
  - Status: T389 adds a compact node evidence workspace in the same standalone
    dashboard detail section. It joins backend detail-page coverage, selected
    table-row presence, and exact-detail request status for users, satellites,
    routes, services, service traces, and compute nodes without adding new
    backend semantics or frontend-local business inference.
  - Status: T390 adds an exact-detail review workspace above the large detail
    tables. It reuses the existing exact-detail inspectors to show, per detail
    family, backend exact-detail sync state, visible-window fallback state,
    request loading/error state, reviewable field counts, warning-field counts,
    and resource/synchronization field counts without changing backend
    protocols.
  - Status: T391 adds a read-only raw JSON inspector for synchronized
    exact-detail payloads. The dashboard combines currently selected backend
    payloads into a bounded JSON pointer view using the existing deterministic
    JSON artifact scanner, so operators can audit source fields without
    payload editing, protocol changes, or frontend business recomputation.
  - Status: T392 adds a local path/field filter to that exact-detail raw JSON
    inspector. The filter reuses the same deterministic scanner matching over
    pointer labels, value types, depth labels, and value previews, preserving
    parent context rows while avoiding backend payload mutation or protocol
    changes.
- V2-054: Add model assumptions panel.
  - Scope: backend-derived model caveats, fidelity mode, KPI provenance.
  - Depends on: V2-003, V2-021.
  - Status: T229 adds a standalone dashboard model assumptions panel v1 that
    combines backend `model_assumptions`, runtime fidelity warnings, network
    KPI credibility, and configuration boundary labels without adding frontend
    model inference.
  - Status: T274 adds a neighboring dashboard model trust evidence workspace
    that summarizes configuration semantics, fidelity policy, KPI credibility,
    KPI formula provenance, reproducibility/export diagnostics, and runtime
    state into deterministic evidence rows. Missing proof is shown as pending
    evidence rather than inferred locally.

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
    contract. T267 adds `review_summary_v1.json` and
    `leo_twin.runtime_export_review_summary.v1` so every new runtime export
    package has a deterministic user-readable review entry point with scenario
    scale, runtime progress, manifest/config hashes, artifact coverage, and
    review readiness. The demo backend serves it at
    `/runtime/export/packages/{package_id}/review-summary`. T268 binds the
    selected package's review summary into the standalone dashboard as a
    read-only card next to compare and restore-preflight context. T270 adds
    `diagnostics_bundle_v1.json` and
    `leo_twin.runtime_export_diagnostics_bundle.v1` so each result package also
    has deterministic artifact-health findings, model-boundary declarations,
    and operator next actions. T271 renders the selected package diagnostics
    bundle in the standalone dashboard as a read-only diagnostics drawer next
    to artifact health, compare, and restore-preflight context. T272 renders
    the selected package `manifest.json` as a manifest inspector with stable
    hash rows, catalog file-hash cross-links, diagnostics manifest-hash
    agreement, and artifact source/status rows. T277 adds route trust evidence
    to both review summary and diagnostics bundle, including a compatibility
    warning for older packages that lack
    `route_provenance_trust_summary_v1`. T278 adds
    `route_detail_index_v1.json` as a package artifact so route trust samples
    can be reviewed against exported route explanation rows. T279 renders the
    selected package's route detail index in the dashboard as a read-only route
    evidence drawer. T302 adds
    `leo_twin.runtime_export_reproducibility_boundary.v1` to result package
    manifests, config snapshots, review summaries, and diagnostics bundles so
    users can verify config-only restore, persisted-artifact reads, and
    no-replay/no-recompute/no-mutation/no-packet/no-external-simulator
    boundaries from a single backend-owned object. T303 renders that same
    backend-owned boundary in the standalone dashboard export review area as a
    read-only card with hash agreement, restore/read/compare scope, export
    windows, and boundary conditions before the manifest inspector. T304 adds a
    neighboring compare/restore boundary alignment card so package compare and
    restore-preflight evidence are checked against the same backend boundary
    before users make restore decisions. T305 moves the same boundary-alignment
    evidence into backend compare and restore-preflight summaries as
    `runtime_export_boundary_alignment_v1`, allowing API consumers and the
    dashboard to read alignment status, warnings, and alignment hash directly
    from the compare/preflight responses. T310 adds
    `scenario_review_bundle_v1.json` as a deterministic operator entry point
    for each runtime export package. It binds user configuration evidence,
    scenario scale, runtime progress, manifest/boundary hashes, review summary
    hash, diagnostics hash, audit-index filename, model boundaries, and
    recommended review order without replaying events or recomputing model
    state. T311 binds that artifact into the standalone dashboard package
    review area as a Scenario Review Bundle card with scenario scale, user
    configuration binding, reproducibility evidence, diagnostics evidence,
    audit-index link, and explicit no-replay/no-recompute/no-packet boundary
    labels. T312 expands that card into a guided review workflow with ordered
    artifact rows for scenario entry, audit index, review summary, diagnostics,
    manifest, configuration, route evidence, service trace, event evidence,
    metrics, and summary outputs, using backend package evidence to mark
    available and missing review steps. T313 adds
    `scenario_review_checklist_v1.json` as the deterministic operator decision
    record for that guided workflow. The backend persists reviewed/skipped/
    follow-up/error status and operator notes through
    `POST /runtime/export/packages/{package_id}/scenario-review-checklist`,
    updates the export catalog, and regenerates the package audit index with
    checklist presence, hash, status, and record count. T314 binds that
    checklist contract into the standalone dashboard guided review workflow:
    every review row can be marked reviewed, skipped, follow-up, or error with
    an operator note, saved through the backend endpoint, and reflected back
    through refreshed catalog/audit-index evidence. T315 adds a dashboard
    package-review completion summary that aggregates backend-owned audit
    readiness, saved route comparison report presence, scenario review bundle
    readiness, and checklist completion into one operator-facing handoff
    signal. T316 moves that handoff readiness semantics into the backend audit
    index as `package_review_completion_v1`, allowing dashboard and offline
    consumers to read the same deterministic completion status and hash without
    re-deriving the rules locally. T317 exposes the same object through
    `GET /runtime/export/packages/{package_id}/review-completion`, so tools can
    read handoff readiness without loading the full audit index. T318 adds the
    backend-generated `package_handoff_report_v1.md` artifact and
    `/runtime/export/packages/{package_id}/handoff-report` route so operators
    can download a deterministic human-readable package handoff summary
    derived from the same completion evidence. T319 adds the corresponding
    dashboard package-review entry and frontend API helper, so selected export
    packages expose the handoff Markdown link next to backend completion
    evidence without local handoff-rule inference. T325 adds
    `network_kpi_benchmark_validation_v1.json` as a runtime export artifact,
    binds it into `review_summary_v1.json`, `diagnostics_bundle_v1.json`,
    `scenario_review_bundle_v1.json`, `export_package_audit_index_v1.json`, and
    `package_handoff_report_v1.md`, and lets the dashboard show backend-owned
    KPI benchmark status/hash labels without recomputing KPI values. T370 adds
    `network_kpi_formula_evidence_v1.json` to the same result-package review
    path, preserving backend formula/input/time-series evidence offline without
    metric recomputation. T373 adds
    `user_configuration_template_validation_v1.json` to the same review path,
    preserving approved user configuration template validation evidence
    offline without template reloads, config application, event replay, or
    frontend-side validation. T377 adds `traffic_demand_explanation_v1.json`
    to the same review path, preserving backend-owned business-demand
    explanation evidence offline without traffic regeneration, event replay,
    packet-level simulation, or frontend-side inference. T344 adds
    `GET /runtime/export/packages/{package_id}/acceptance-report`, a
    backend-owned pass/warn/fail acceptance summary that binds audit evidence,
    handoff completion, route review, service-trace review, scenario review,
    network KPI benchmark status, model-boundary exclusions, user configuration
    validation, and forbidden-integration declarations into one dashboard and
    API signal for the industrial v2 demo closed loop. T345 binds that
    acceptance report to the shipped 72/300/1200 benchmark scenario matrix by
    adding `benchmark_acceptance_binding_v1` to the audit index and a
    `benchmark_scenario_gate` acceptance check. Standard benchmark packages now
    report exact-range, fidelity, route-trust, and KPI-gate evidence; custom
    packages remain usable but show a benchmark-gate warning. T346 exposes that
    backend-owned benchmark gate as a dedicated dashboard section inside the
    package acceptance card, including matched scenario, benchmark matrix,
    config path, identity-match count, expected-range/fidelity/runtime-status
    pass-warn-fail summaries, issue labels, and evidence hashes without
    locally re-deriving product acceptance semantics. T347 expands that section
    with per-check detail rows for expected-range, fidelity, and runtime-status
    results, showing status, expected value or range, observed value, issue
    label, and result hash as read-only projections of backend package
    evidence. T348 adds direct evidence links to those benchmark rows, mapping
    expected-range checks to the audit index, fidelity checks to
    `config_snapshot.json`, route/trust checks to `route_detail_index_v1.json`,
    KPI checks to `network_kpi_benchmark_validation_v1.json`, and scenario
    checks to `scenario_review_bundle_v1.json`. T349 moves that artifact-map
    semantic into the backend `benchmark_acceptance_binding_v1` result rows via
    `evidence_artifact_filename` and `evidence_artifact_role`; the dashboard
    now consumes those backend fields first and only falls back to the local
    mapping for older packages. T350 adds backend-owned
    `evidence_context_id` and `evidence_context_label` to the same benchmark
    rows, so dashboard rows can show the artifact-local context for a selected
    check without inventing that context in the browser. T351 adds backend
    `evidence_json_pointer` fields to those rows, giving operators an
    artifact-local JSON path hint for expected-range, fidelity, route-trust,
    and KPI benchmark checks without browser-side recomputation. T352 adds a
    local dashboard review-focus state for benchmark rows, so selecting a row
    displays the current artifact, context, JSON pointer, expected value, and
    observed value together while preserving read-only package artifact links.
    T353 carries that same selected focus into the package artifact health
    grid, marking the backend-named evidence file so an operator can trace a
    benchmark row to a concrete package artifact without browser-side package
    parsing or acceptance recomputation. T354 adds a read-only artifact
    pointer preview for selected JSON evidence files: the dashboard loads the
    backend-named package artifact, resolves `evidence_json_pointer`, and shows
    the target JSON value without mutating packages or recomputing acceptance.
    T355 expands that preview into a bounded read-only JSON artifact inspector
    with deterministic pointer rows, selected evidence pointer highlighting,
    and local text filtering over pointer/key/value previews. T356 adds a
    package artifact health entry point for the same inspector, so any
    registered JSON result artifact can be inspected from its health row at the
    JSON root while retaining the original package-file link. T357 adds route
    and service-trace evidence cross-links into that inspector, carrying
    route ids or trace ids as default filters and preselecting backend-derived
    JSON pointer context where available. T359 extends the same inspector
    cross-link pattern to `user_service_request_summary_v2.json` rows so
    exported user-service requests can open package-owned JSON context without
    event replay, service recomputation, or frontend business inference.

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
  - Status: T360 adds browser-rendered acceptance smoke for real console
    initialize/start clicks, dashboard visibility, browser page-error checks,
    and browser-side stop/reset cleanup. It also adds frontend `POST /control`
    command transport for browser buttons while preserving the `/control`
    WebSocket path used by backend control-cycle smoke.
- V2-084: Add surface notice persistence.
  - Scope: operator-facing runtime notice dismissal across page refreshes.
  - Status: T249 persists dismissed simulation-completed notice keys in
    browser session storage, restores the dismissal after refresh, clears the
    persisted key when a new runtime becomes active, and keeps storage failures
    non-fatal.
  - Status: T250 persists dismissed runtime backpressure notice keys in browser
    session storage, restores the dismissal after refresh for the same stable
    pressure identity, clears it once the warning condition disappears, and
    keeps storage failures non-fatal.

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

Current Phase 3 progress:

- V2-073 has been extended from backend package export into dashboard review
  surfaces. The dashboard now links persisted package artifacts, renders the
  selected `review_summary_v1.json`, and exposes backend-catalog artifact
  health rows for required-file coverage and direct file inspection.
- V2-072/V2-083 now include a disposable local acceptance harness that can
  restart services, apply the standard 72 / 300 / 1200 benchmark YAMLs through
  backend `/control`, reuse the product acceptance script, and restore local
  runtime config drift files after the run.
- V2-021/V2-072 now include backend KPI calibration evidence. Runtime status
  exposes `network_kpi_calibration_v1` so benchmark and dashboard layers can
  distinguish time-varying KPI movement from flat-but-explained flow-level
  proxy values.
- T363 completes the first dashboard binding for that evidence: the standalone
  dashboard renders the backend calibration summary in the network KPI panel
  and model-trust evidence workspace instead of deriving movement semantics
  locally.
- T369 adds backend formula evidence for network KPIs and binds it into the
  same dashboard network KPI panel and model-trust evidence workspace, closing
  the gap between formula provenance, selected runtime inputs, and observed KPI
  movement.
- T384 adds backend KPI variation explanation evidence in runtime status and
  binds it to the dashboard network KPI panel, making flat or time-varying
  throughput, latency, loss-proxy, and jitter-proxy behavior explicit from
  backend-owned fields.
- T385 exports the same KPI variation explanation as
  `network_kpi_variation_explanation_v1.json` and binds it into package
  review summary, diagnostics, scenario review, audit index, and dashboard
  export-review labels for offline reproducibility.
- T386 adds backend-owned `artifact_browser_index_v1` to
  `diagnostics_bundle_v1.json`. The index groups result-package artifacts by
  review category, records present/missing/required/recommended state, and
  carries default JSON pointer/filter hints. The dashboard artifact-health card
  and diagnostics drawer consume this backend index so offline package browsing
  does not depend on frontend-local artifact semantics.
- T387 renders the backend artifact browser index as a compact dashboard
  workspace in the artifact-health card. Each category row shows
  present/missing counts, representative filenames, a default JSON evidence
  target, and a direct read-only inspector action, making exported result
  packages easier to review without adding browser-side artifact semantics.
- T388 adds local artifact-browser filters for backend category, missing state,
  inspectable JSON artifacts, and text query. The full artifact set stays
  backend-owned while the dashboard can focus large result packages during
  operator review.
- T364 adds a dashboard detail-coverage status card for backend detail
  families, cursor windows, hidden rows, exact node cards, and pagination
  contract status. This improves the node-detail workstream without changing
  backend protocols.
- T365 adds selected-detail evidence status for user, satellite, route,
  service, service trace, and compute-node selections so the dashboard can show
  whether the current selection is backed by a table row, backend exact detail,
  a loading request, or an exact-detail error.
- T366 adds a service-trace closed-loop correlation note to the dashboard
  detail evidence row. It makes the selected service trace's flow, route, user,
  satellite, compute-node, stage, and latency evidence explicit and prefers
  backend exact detail over visible-window fallback.
- T367 adds one-click service-trace focus filters. A selected service trace can
  now drive correlated user/satellite, route, service, service-trace, and
  compute-node filters, again preferring backend exact detail over visible
  window fallback.
- T368 adds a wide service-trace browser to the dashboard node-detail
  workspace. The selected trace is expanded into lifecycle, correlation, route,
  user, satellite, and compute-node sections so the communication-compute chain
  is readable without manually stitching small cards together.

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
