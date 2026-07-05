# LEO-Twin Development Log

This file records completed development tasks, committed changes, validation
results, and issues encountered during implementation. Every future completed
task must update this log in the same commit as the code or documentation
change.

## 2026-07-06 - Backpressure Notice Dismissal v1

- Branch: `feature/T250-backpressure-notice-dismissal-v1`
- Commit: pending in this commit
- Scope: make runtime pressure warnings dismissible across page refreshes for
  the same stable backend pressure identity. The frontend now persists the
  dismissed backpressure notice key in browser session storage, restores it on
  App initialization, clears it once the pressure warning is no longer visible,
  and handles storage failures without breaking the UI.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `docs/backpressure_notice_dismissal_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- appSurface.test.ts`
    - Result: passed, 26 test files / 352 tests.
  - `pnpm --dir frontend build`
    - Result: passed. The command includes TypeScript checking; Vite reported
      the existing `DataPanel` chunk size warning after minification.
- Problems encountered and handling:
  - Backpressure notices already had a stable dismiss key, but the dismissal was
    React-state-only. Refreshing the page discarded that state. The fix reuses
    the same stable key in `sessionStorage` while preserving existing behavior
    that clears the dismissal when the warning condition disappears.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Notice persistence remains browser-session scoped. Cross-browser or
    user-account-level notice preferences would require a separate product
    preference contract.

## 2026-07-06 - Completion Notice Dismissal v1

- Branch: `feature/T249-completion-notice-refresh-v1`
- Commit: pending in this commit
- Scope: fix the page-refresh bug where the simulation-completed notice could
  reappear after the user had dismissed it. The frontend now persists the
  dismissed completion notice key in browser session storage, restores it on
  App initialization, and clears it when a new runtime becomes active.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `docs/completion_notice_dismissal_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- appSurface.test.ts`
    - Result: passed, 26 test files / 350 tests.
  - `pnpm --dir frontend build`
    - Result: passed. The command includes TypeScript checking; Vite reported
      the existing `DataPanel` chunk size warning after minification.
- Problems encountered and handling:
  - The App already prevented completed notices unless the page session had
    observed an active runtime, but the dismissal key itself was held only in
    React state. A page refresh discarded that state. The fix keeps the
    dismissal key in `sessionStorage` for the current browser session and
    handles storage exceptions without failing the UI.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Backpressure notices remain session-local in React state. If users want
    identical refresh behavior for those notices, handle it as a separate
    notice-policy task.

## 2026-07-06 - Dashboard Exact Detail Request Status v1

- Branch: `feature/T248-exact-detail-request-status-v1`
- Commit: pending in this commit
- Scope: add visible loading, synchronized, and error status for exact-detail
  requests in the standalone dashboard. App now tracks request state for user,
  satellite, route, service, and compute-node exact-detail endpoints, and
  DataPanel prepends the matching status to the currently selected inspector
  only when the request entity id matches the active selection.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/dashboard_exact_detail_request_status_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- dataPanel.test.ts api.test.ts appSurface.test.ts`
    - Result: passed, 26 test files / 348 tests.
  - `pnpm --dir frontend build`
    - Result: passed. The command includes TypeScript checking; Vite reported
      the existing `DataPanel` chunk size warning after minification.
- Problems encountered and handling:
  - Exact-detail payloads and request lifecycle were previously stored as one
    implicit success state, so slow or failed detail calls looked identical to
    the local cursor-window fallback. The fix keeps request status separate from
    payload state and scopes status by selected entity id to avoid stale status
    bleed-through.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - The dashboard still uses full DataPanel chunk loading. Bundle splitting
    remains a dedicated frontend performance task.

## 2026-07-06 - Dashboard Exact Detail Binding v1

- Branch: `feature/T247-route-service-compute-exact-inspector-v1`
- Commit: pending in this commit
- Scope: bind route, service lifecycle, and compute-node exact detail APIs into
  the standalone dashboard. The three backend cursor tables now support
  selectable rows, trigger exact-detail API requests through App state, and
  render backend-preferred exact detail cards with local cursor-window rows as
  immediate fallback.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/dashboard_exact_detail_binding_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- dataPanel.test.ts api.test.ts appSurface.test.ts`
    - Result: passed, 26 test files / 347 tests.
  - `pnpm --dir frontend build`
    - Result: passed. The command includes TypeScript checking; Vite reported
      the existing `DataPanel` chunk size warning after minification.
- Problems encountered and handling:
  - Route, service, and compute-node rows previously rendered as static divs.
    They were changed to `button type="button"` rows with matching grid styles
    and selected-row styling to preserve layout while adding interaction.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Add loading/error affordances for exact detail requests if backend latency
    becomes visible at larger scale.
  - Split the large DataPanel bundle into smaller chunks in a dedicated
    frontend performance task.

## 2026-07-06 - Route, Service, and Compute Detail-by-ID v1

- Branch: `feature/T246-route-service-compute-detail-by-id-v1`
- Commit: pending in this commit
- Scope: extend exact detail retrieval beyond users and satellites. The demo
  backend now exposes `GET /runtime/details/routes/<route_id>`,
  `GET /runtime/details/services/<service_id>`, and
  `GET /runtime/details/compute-nodes/<node_id>`. The exact response reuses
  the same backend-owned row shapes as the existing cursor pages. The frontend
  adds typed API loaders for these endpoints without changing dashboard layout.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/app/api.ts`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/tests/api.test.ts`
  - `tests/unit/test_runtime_observability.py`
  - `tests/integration/test_live_runtime_streaming.py`
  - `docs/route_service_compute_detail_by_id_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_live_runtime_streaming.py -q`
    - Result: passed, 17 tests.
  - `pnpm --dir frontend test -- api.test.ts`
    - Result: passed, 26 test files / 346 tests.
  - `pnpm --dir frontend build`
    - Result: passed. The command includes TypeScript checking; Vite reported
      the existing `DataPanel` chunk size warning after minification.
- Problems encountered and handling:
  - The live runtime integration fixture can have empty route, service, or
    compute-node cursor windows at the sampled runtime moment. Exact lookup
    construction is therefore covered with deterministic unit fixtures, while
    the integration test checks envelope compatibility when rows are present.
  - Extending `RuntimeEntityDetailEnvelopeV1` to non-node row summaries required
    explicit return narrowing for existing user/satellite detail loaders.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Bind route, service, and compute-node row selections in the dashboard to
    these exact detail endpoints.
  - Add visible loading/error affordances once exact inspectors are wired into
    the dashboard UI.

## 2026-07-06 - User and Satellite Detail-by-ID v1

- Branch: `feature/T245-user-satellite-detail-by-id-v1`
- Commit: pending in this commit
- Scope: make selected dashboard user and satellite inspectors request
  backend-owned exact detail cards by entity id. The demo backend now exposes
  `GET /runtime/details/users/<user_id>` and
  `GET /runtime/details/satellites/<satellite_id>` while preserving the
  existing cursor endpoints. The dashboard still renders local/window fallback
  details immediately, then prefers the exact backend detail card when it
  arrives.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/app/api.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/api.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/unit/test_runtime_observability.py`
  - `tests/integration/test_live_runtime_streaming.py`
  - `docs/user_satellite_detail_by_id_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_live_runtime_streaming.py -q`
    - Result: passed, 17 tests.
  - `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts`
    - Result: passed, 26 test files / 345 tests.
  - `pnpm --dir frontend build`
    - Result: passed. The command includes TypeScript checking; Vite reported
      the existing `DataPanel` chunk size warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - One backend assertion initially used terminal mojibake text for the
    Chinese `平台` field. The assertion was corrected to the actual field
    value.
  - The local shell did not have `node` on `PATH`; frontend validation used the
    bundled Codex workspace Node/Pnpm paths.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Add detail-by-id endpoints for routes, service lifecycle rows, and compute
    nodes if users need exact inspectors for those table selections.
  - Add visible loading/error affordances for exact detail requests if backend
    latency becomes noticeable in larger scenarios.

## 2026-07-06 - Service and Compute Detail Filters v1

- Branch: `feature/T244-service-compute-detail-filters-v1`
- Commit: pending in this commit
- Scope: complete the first filter-aware cursor pass across all visible
  dashboard detail collections. Service lifecycle and compute-node detail pages
  now accept backend text `query`, apply filtering before cursor pagination, and
  report filter metadata when active. The dashboard adds backend text filters
  for the service and compute-node tables and sends those queries during
  refresh and page-turn actions.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/app/api.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/api.test.ts`
  - `tests/unit/test_runtime_observability.py`
  - `docs/service_compute_detail_filters_v1.md`
  - `docs/filter_aware_detail_cursors_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_runtime_session_control.py tests/integration/test_live_runtime_streaming.py tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 49 tests.
  - `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 26 test files / 343 tests.
  - `pnpm --dir frontend build`
    - Result: passed. The command includes TypeScript checking; Vite reported
      the existing `DataPanel` chunk size warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Service and compute-node unfiltered response shapes remain unchanged.
    Filter metadata is emitted only when a text query is active.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Add detail-by-id endpoints for selected entities.
  - Add backend filter metadata to a future large detail pagination contract
    version.
  - Split large dashboard sections into smaller lazy chunks.

## 2026-07-06 - Filter-Aware Detail Cursors v1

- Branch: `feature/T243-filter-aware-detail-cursors-v1`
- Commit: pending in this commit
- Scope: make selected backend detail cursor endpoints filter-aware. User and
  satellite detail pages now accept text `query`; route detail pages accept
  text `query`, `availability`, `business_type`, and `bottleneck_component`.
  The backend applies filters before cursor pagination and the frontend sends
  the active dashboard filters during refresh and page-turn actions.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/app/api.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/api.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/unit/test_runtime_observability.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/filter_aware_detail_cursors_v1.md`
  - `docs/dashboard_filter_scope_notice_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_runtime_session_control.py tests/integration/test_live_runtime_streaming.py tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 48 tests.
  - `pnpm --dir frontend test -- dataPanel.test.ts api.test.ts appSurface.test.ts`
    - Result: passed, 26 test files / 343 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed using the Codex bundled Node.js runtime.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing `DataPanel` chunk size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing runtime observability tests assert exact unfiltered summary
    objects. Filter metadata is emitted only when a filter is active, preserving
    the legacy unfiltered response shape.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Add service lifecycle and compute-node filter controls.
  - Add detail-by-id endpoints for selected entities.
  - Add backend filter metadata to a future large detail pagination contract
    version.

## 2026-07-06 - Dashboard Filter Scope Notice v1

- Branch: `feature/T242-dashboard-filter-scope-notice-v1`
- Commit: pending in this commit
- Scope: make dashboard filtering scope explicit after the backend cursor
  controls were added. The detail observability notes now include a
  backend-cursor-derived filter scope notice for user, satellite, and route
  pages, explaining that current filters apply only to the loaded backend page
  and local render window until filter-aware backend cursor requests exist.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/dashboard_filter_scope_notice_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 26 test files / 343 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed using the Codex bundled Node.js runtime.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing `DataPanel` chunk size
      warning after minification.
  - `python -m pytest tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 9 tests.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Current filters are frontend-local and do not search unloaded backend pages.
    This task intentionally adds product transparency first and leaves backend
    filter-aware cursor queries as a separate task.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Implement filter-aware backend cursor requests.
  - Add detail-by-id endpoints for selected entities.
  - Split large dashboard sections into smaller lazy chunks.

## 2026-07-06 - Dashboard Core Detail Cursor Controls v1

- Branch: `feature/T241-dashboard-core-detail-cursors-v1`
- Commit: pending in this commit
- Scope: complete the first visible backend cursor-control pass for the
  standalone dashboard detail collections. User, satellite, route, service,
  and compute-node pages now have active cursor state in `App.tsx`; the detail
  refresh loop preserves those cursors; and the dashboard shows backend page
  range plus previous/next/refresh actions where cursor metadata is available.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `docs/dashboard_core_detail_cursor_controls_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 26 test files / 341 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed using the Codex bundled Node.js runtime.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing `DataPanel` chunk size
      warning after minification.
  - `python -m pytest tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 9 tests.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - User, satellite, and route runtime status summaries keep cursor metadata
    optional for compatibility. The dashboard hides backend cursor controls
    when those fields are absent, avoiding fake pagination for legacy data.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Add filter-aware backend cursor requests so searches can span beyond the
    active backend page.
  - Add detail-by-id endpoints for selected entities.
  - Split DataPanel into smaller lazy sections to address the current chunk
    warning.

## 2026-07-06 - Dashboard Service and Compute Cursor Controls v1

- Branch: `feature/T240-dashboard-service-compute-cursors-v1`
- Commit: pending in this commit
- Scope: advance V2-053 by adding visible backend cursor controls to the
  standalone dashboard service lifecycle and compute-node resource tables. The
  App runtime detail refresh now preserves active cursors for those pages, and
  each table exposes current row range, previous/next cursor actions, refresh,
  and local loading/error text.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/dashboard_service_compute_cursor_controls_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 26 test files / 341 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed using the Codex bundled Node.js runtime.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing `DataPanel` chunk size
      warning after minification.
  - `python -m pytest tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 9 tests.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - The existing periodic dashboard detail refresh always fetched service and
    compute-node pages from cursor zero. This task changes only those two
    collections to use active cursor state, preserving compatibility for the
    other detail pages.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Add backend cursor controls for user, satellite, and route pages.
  - Add detail-by-id endpoints for selected service and selected compute node.
  - Split or lazy-load DataPanel sections to reduce the current production
    bundle chunk warning.

## 2026-07-06 - Dashboard Service and Compute Detail Tables v1

- Branch: `feature/T239-dashboard-service-compute-detail-tables-v1`
- Commit: pending in this commit
- Scope: complete the visible dashboard binding for backend cursor pages added
  by the large detail pagination contract. The standalone dashboard now renders
  dedicated service lifecycle rows from `runtimeDetailPages.services` and
  compute-node resource rows from `runtimeDetailPages.computeNodes`, using
  backend-recommended detail page sizes where available.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/dashboard_service_compute_detail_tables_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 26 test files / 339 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed using the Codex bundled Node.js runtime.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing `DataPanel` chunk size
      warning after minification.
  - `python -m pytest tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 9 tests.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Service and compute-node cursor pages were already fetched and typed, but
    were not visible as dedicated dashboard tables. This task keeps the current
    dashboard structure and adds only the missing render surfaces and formatter
    tests.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Add UI controls for cursor navigation beyond the first backend page.
  - Add detail-by-id endpoints for selected service and selected compute node.
  - Add column-level filtering after backend cursor navigation is available.

## 2026-07-06 - Dashboard Cursor Contract Binding v1

- Branch: `feature/T238-dashboard-cursor-contract-binding-v1`
- Commit: pending in this commit
- Scope: advance V2-053 by binding the standalone dashboard and App runtime
  detail refresh path to `leo_twin.large_detail_pagination_contract.v2`.
  The frontend now uses backend contract endpoints and recommended limits for
  users, satellites, routes, services, and compute nodes, requests all six
  detail pages where available, prefers route cursor pages over bounded runtime
  status route summaries, and displays the backend pagination contract as the
  source of detail table budgets.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/api.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/api.test.ts`
  - `frontend/tests/appSurface.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/dashboard_cursor_contract_binding_v1.md`
  - `docs/dashboard_detail_window_policy_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- dataPanel.test.ts api.test.ts appSurface.test.ts`
    - Result: passed, 26 test files / 335 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed using the Codex bundled Node.js runtime.
  - `python -m pytest tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 9 tests.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing dashboard tables were already paged, but their render budgets were
    frontend constants. This task preserves the current layout and binds the
    budgets to backend contract fields where available.
  - Service and compute-node pages are fetched and typed, but dedicated
    service/compute-node dashboard tables remain follow-up work to avoid a
    larger layout rewrite in this task.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Add UI controls for cursor navigation beyond the first backend page.
  - Bind service and compute-node detail pages to dedicated dashboard tables.
  - Add single-entity detail-by-id requests for user and satellite drawers.

## 2026-07-06 - Large Detail Pagination Contract v2

- Branch: `feature/T237-large-detail-pagination-contract-v2`
- Commit: pending in this commit
- Scope: advance V2-043 by adding backend-owned
  `leo_twin.large_detail_pagination_contract.v2`. The contract derives from
  `scale_policy_v2` and `lod_snapshot_policy_v2` and covers cursor metadata for
  ground users, satellites, routes, services, and compute nodes. The integration
  demo backend now exposes read-only cursor endpoints for route, service, and
  compute-node detail pages in addition to the existing user, satellite, and
  combined node detail endpoints.
- Changed files/modules:
  - `src/leo_twin/services/detail_pagination_contract.py`
  - `src/leo_twin/services/derived_summary.py`
  - `src/leo_twin/services/runtime_observability.py`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/core/event_types/index.ts`
  - `tests/unit/test_large_detail_pagination_contract_v2.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `tests/unit/test_runtime_observability.py`
  - `tests/integration/test_live_runtime_streaming.py`
  - `docs/large_detail_pagination_contract_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_large_detail_pagination_contract_v2.py tests/unit/test_backend_derived_summary.py tests/unit/test_runtime_observability.py -q`
    - Result: passed, 19 tests.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py::test_runtime_detail_pages_return_deterministic_windows -q`
    - Result: passed, 1 test.
  - `python -m pytest tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 9 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed using the Codex bundled Node.js runtime.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing runtime observability already had user, satellite, and combined
    node cursor pages. This task kept those paths compatible and added the
    missing route, service, and compute-node read-only pages instead of
    rewriting dashboard architecture.
  - Route, service, and compute-node pages reuse existing snapshot, route
    explanation, service latency history, and KPI slice data. No traffic,
    network, compute, or Event Kernel behavior was changed.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - V2-053 should connect standalone dashboard large tables to these cursor
    contracts and avoid local hardcoded table budgets.
  - Single-entity full detail by id remains future work.
  - Result exports should include this contract metadata for replay packages.

## 2026-07-06 - Runtime Guardrails v2

- Branch: `feature/T236-runtime-guardrails-v2`
- Commit: pending in this commit
- Scope: advance V2-042 by adding backend-owned
  `leo_twin.runtime_guardrails.v2`. The policy derives from
  `scale_policy_v2`, `lod_snapshot_policy_v2`, and existing scale safety
  estimates to report event volume, memory use, stream backlog risk,
  `ALLOW` / `DEGRADE` / `REFUSE` decisions, refusal/degrade reasons, and
  runtime actions.
- Changed files/modules:
  - `src/leo_twin/services/runtime_guardrails_v2.py`
  - `src/leo_twin/services/derived_summary.py`
  - `tests/unit/test_runtime_guardrails_v2.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `frontend/src/core/event_types/index.ts`
  - `docs/runtime_guardrails_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_guardrails_v2.py tests/unit/test_lod_snapshot_policy_v2.py tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 25 tests.
  - `python -m pytest tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 9 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed using the Codex bundled Node.js runtime after the user
      shell PATH did not expose `node`.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - This task intentionally exposes runtime guardrails as a backend-derived
    policy contract without changing the Event Kernel, live session loop, or
    stream buffer behavior.
  - Frontend protocol types were extended so later dashboard work can consume
    `runtime_guardrails_v2` instead of inferring runtime safety locally.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - V2-043 should add backend cursor/detail contracts for hidden users,
    satellites, routes, services, and compute nodes.
  - A later runtime-control task should apply guardrail `REFUSE` decisions to
    start-time control paths where appropriate.
  - Dashboard v3 should display `decision`, `degrade_reasons`, and
    `refusal_reasons` from this backend summary.

## 2026-07-06 - LOD Snapshot Policy v2

- Branch: `feature/T235-lod-snapshot-policy-v2`
- Commit: pending in this commit
- Scope: advance V2-041 by adding backend-owned
  `leo_twin.lod_snapshot_policy.v2`. The policy derives from
  `scale_policy_v2` and defines raw count fields, bounded detail windows,
  Top-K summary limits, sampled history lengths, cursor requirements, and
  hidden-row explanations for scale-aware observation surfaces.
- Changed files/modules:
  - `src/leo_twin/services/lod_snapshot_policy.py`
  - `src/leo_twin/services/derived_summary.py`
  - `tests/unit/test_lod_snapshot_policy_v2.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `frontend/src/core/event_types/index.ts`
  - `docs/lod_snapshot_policy_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_lod_snapshot_policy_v2.py tests/unit/test_scale_policy_v2.py tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 29 tests.
  - `python -m pytest tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 9 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - This task intentionally defines the LOD snapshot contract without changing
    live snapshot publication or Event Kernel behavior. Runtime enforcement
    belongs to V2-042/V2-043.
  - Frontend protocol types were updated so later dashboard work can consume
    `scale_policy_v2` and `lod_snapshot_policy_v2` without inventing local LOD
    semantics.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - V2-042 should enforce event, memory, stream backlog, and degrade/refusal
    guardrails from the active profile.
  - V2-043 should add backend cursor/detail APIs for hidden users, satellites,
    routes, services, and compute nodes.
  - Dashboard v3 should display hidden-row explanations and raw counts from
    this backend policy.

## 2026-07-06 - Scale Policy v2

- Branch: `feature/T234-scale-policy-v2`
- Commit: pending in this commit
- Scope: advance V2-040 by adding backend-owned
  `leo_twin.scale_policy.v2`. The policy defines six product scale profiles
  for 72, 300, 1200, 3000, 6000, and 12000 satellites and exposes the active
  profile through backend derived summaries.
- Changed files/modules:
  - `src/leo_twin/services/scale_policy_v2.py`
  - `src/leo_twin/services/derived_summary.py`
  - `tests/unit/test_scale_policy_v2.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `docs/scale_policy_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_scale_policy_v2.py tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 22 tests.
  - `python -m pytest tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 9 tests.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing scale fidelity services already selected the active runtime modes,
    so this task keeps behavior unchanged and adds the product profile matrix as
    a deterministic explanation contract.
  - The 3000, 6000, and 12000 profiles are explicit guardrail profiles, not
    claims of full-detail interactive fidelity.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - V2-041 should bind snapshot LOD behavior to these profile names.
  - V2-042 should attach event, memory, stream backlog, and refusal/degrade
    guardrails to the active profile.
  - V2-043 should add backend cursor/detail contracts for large user,
    satellite, route, service, and compute-node tables.

## 2026-07-06 - Satellite Camera Detail Policy v2

- Branch: `feature/T233-satellite-camera-detail-policy-v2`
- Commit: pending in this commit
- Scope: advance V2-063 by formalizing the 3D Earth/satellite camera toggle and
  selected-satellite inset as `leo_twin.satellite_camera_detail_policy.v2`.
  The summary reports active camera mode, selectable target count, selected
  satellite, inset state, bounded local trail, coverage overlay state, and
  compute-resource overlay availability.
- Changed files/modules:
  - `frontend/src/3d/cesium/satelliteFollow.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/satellite_camera_detail_policy_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- satelliteVisuals.test.ts visualLayerLimits.test.ts globeVisualPolicy.test.ts sceneAssetManifest.test.ts countryOverlays.test.ts`
    - Result: passed, 26 test files / 331 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing large `DataPanel` chunk
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing follow camera, selected-satellite inset, local trail, coverage
    summary, and resource overlay already existed. This task adds a stable
    policy summary and UI explanation rather than changing Cesium camera
    behavior.
  - The policy falls back to Earth overview when no selectable satellite exists,
    which keeps the summary consistent with the disabled follow button.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Add screenshot regression for the follow camera and local inset.
  - Add richer selected-satellite detail inspection once backend cursor/detail
    APIs are available for large scenarios.
  - Camera transition diagnostics are still limited to existing Cesium render
    errors.

## 2026-07-06 - Selected Coverage Visual Policy v2

- Branch: `feature/T232-selected-coverage-visual-policy-v2`
- Commit: pending in this commit
- Scope: advance V2-062 by formalizing the selected-satellite coverage display
  as `leo_twin.selected_coverage_visual_policy.v2`. The frontend now exposes a
  deterministic policy summary derived from backend `coverage_beam_summary`,
  including selected-satellite-only detail mode, bounded honeycomb beam count,
  footprint radius/length, RF exclusions, local layer visibility, and
  no-access-semantics boundaries.
- Changed files/modules:
  - `frontend/src/3d/beam_renderer/beamEntities.ts`
  - `frontend/src/3d/cesium/renderLimits.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `frontend/tests/visualLayerLimits.test.ts`
  - `docs/selected_coverage_visual_policy_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- satelliteVisuals.test.ts visualLayerLimits.test.ts globeVisualPolicy.test.ts sceneAssetManifest.test.ts countryOverlays.test.ts`
    - Result: passed, 26 test files / 329 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing large `DataPanel` chunk
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing selected-satellite footprint and honeycomb-cell rendering already
    existed, so this task intentionally productizes and tests the policy
    boundary instead of rewriting the renderer.
  - The policy remains visual-only and explicitly excludes RF propagation,
    antenna-pattern simulation, link-budget calculation, interference modeling,
    and access-decision semantics.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Add screenshot regression for selected-satellite footprint and beam cells.
  - Bind richer per-beam inspection to a selected-satellite detail surface after
    the V2-063 camera/detail mode work.
  - Coverage display still uses deterministic geometric containment, not a
    physical communication coverage model.

## 2026-07-06 - Earth Visual Policy v2

- Branch: `feature/T231-earth-visual-policy-v2`
- Commit: pending in this commit
- Scope: advance V2-061 by adding a deterministic Earth visual policy summary
  for the Cesium 3D scene. The policy binds the active opaque/transparent globe
  mode to the 3D asset manifest, country-border visibility, far-side occlusion
  behavior, disabled day/night mode, and visual-only semantics.
- Changed files/modules:
  - `frontend/src/3d/cesium/globeVisualPolicy.ts`
  - `frontend/src/3d/cesium/renderLimits.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/tests/globeVisualPolicy.test.ts`
  - `frontend/tests/visualLayerLimits.test.ts`
  - `docs/earth_visual_policy_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- globeVisualPolicy.test.ts visualLayerLimits.test.ts sceneAssetManifest.test.ts satelliteVisuals.test.ts countryOverlays.test.ts`
    - Result: passed, 26 test files / 327 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing large `DataPanel` chunk
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - The task intentionally keeps the policy in the observation layer. It does
    not add lighting, terrain, RF, orbit, link, or backend runtime behavior.
  - The `TRANSLUCENT` globe mode remains available only as an explicit operator
    observation mode; the default product policy remains opaque with far-side
    occlusion enabled.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Add selected-satellite coverage visualization v2 with deterministic
    footprint and multi-beam display.
  - Add screenshot-based visual regression for default opaque Earth and
    transparent observation mode.
  - Higher-resolution Earth imagery should only be introduced through the asset
    manifest license/hash gate.

## 2026-07-06 - 3D Asset Manifest v1

- Branch: `feature/T230-3d-asset-manifest-v1`
- Commit: pending in this commit
- Scope: advance V2-060 by adding a Cesium 3D scene asset manifest. The
  manifest records the package-managed NaturalEarthII Earth texture,
  SHA-verified Natural Earth country boundary GeoJSON, SHA-verified NASA
  Satellite Kit GLB parts, and the project-generated satellite SVG icon. The
  Cesium layer summary now exposes the active asset manifest version and asset
  counts.
- Changed files/modules:
  - `frontend/src/3d/assets/assetManifest.ts`
  - `frontend/src/3d/cesium/renderLimits.ts`
  - `frontend/tests/sceneAssetManifest.test.ts`
  - `frontend/tests/visualLayerLimits.test.ts`
  - `tests/unit/test_scene_3d_asset_manifest_v1.py`
  - `docs/scene_3d_asset_manifest_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_scene_3d_asset_manifest_v1.py -q`
    - Result: passed, 2 tests.
  - `pnpm --dir frontend test -- sceneAssetManifest.test.ts visualLayerLimits.test.ts satelliteVisuals.test.ts countryOverlays.test.ts`
    - Result: passed, 26 test files / 324 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing large `DataPanel` chunk
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - This task intentionally does not download new external assets. It registers
    and verifies the current bundled assets first so future replacements have a
    stable license/hash gate.
  - The Cesium NaturalEarthII texture is package-managed rather than a single
    project-owned file, so the manifest marks it as package-lock managed while
    SHA-verifying the project-bundled GLB and GeoJSON assets.
  - The first Python hash test expected NASA GLB hashes to appear literally in
    the new manifest file. The manifest imports the existing
    `NASA_SATELLITE_KIT_MODEL_PARTS` constants, so the test was corrected to
    verify both the manifest dependency and the source constant file.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - V2-061 should bind the manifest to the Earth visual policy and opaque globe
    rendering checks.
  - A future task should add or replace a higher-resolution Earth texture only
    after source, license, SHA, and screenshot checks are in place.
  - A future task should add selected-satellite visual regression checks for
    the GLB model in browser rendering.

## 2026-07-06 - Dashboard Model Assumptions Panel v1

- Branch: `feature/T229-dashboard-model-assumptions-panel-v1`
- Commit: pending in this commit
- Scope: advance V2-054 by adding a standalone dashboard model assumptions
  panel v1. The panel combines backend `model_assumptions`, runtime fidelity
  warnings, network KPI credibility, and backend configuration boundary labels
  without introducing frontend model inference.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/dashboard_model_assumptions_panel_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 test files / 320 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing large `DataPanel` chunk
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing model caveats were spread across KPI credibility, fidelity, and
    configuration explanation surfaces. This task consolidates them into a
    single panel while preserving backend fields as the source of truth.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - Result packages should later include a copy of the model assumption panel
    content.
  - Model verification reports should link individual assumptions to benchmark
    evidence.
  - DataPanel remains a large frontend chunk and should be split after the
    dashboard layout stabilizes.

## 2026-07-06 - Dashboard Detail Window Policy v1

- Branch: `feature/T228-dashboard-detail-window-policy-v1`
- Commit: pending in this commit
- Scope: advance V2-053 by making large detail table windowing explicit in the
  standalone dashboard. The dashboard now reports the active rendered rows,
  total rows, user/satellite table windows, render budget, and hidden rows
  waiting for pagination.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/dashboard_detail_window_policy_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 test files / 318 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing large `DataPanel` chunk
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing tables already used deterministic pagination. This task avoids a
    broad table rewrite and instead makes the active render budget visible and
    testable.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - True continuous virtual scrolling is still future work.
  - Backend cursor APIs should eventually replace large frontend fallback row
    merges for very large scenarios.
  - DataPanel remains a large frontend chunk and should be split after the
    dashboard layout stabilizes.

## 2026-07-06 - Dashboard Satellite Detail Drawer v1

- Branch: `feature/T227-dashboard-satellite-detail-drawer-v1`
- Commit: pending in this commit
- Scope: advance V2-052 by adding a deterministic fallback view model for the
  selected-satellite detail drawer. The dashboard still prefers backend
  `node_detail_summary_v1` cards, but when they are unavailable it now groups
  satellite resource rows into service/routing, compute resource pool, and
  network/task sections.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/dashboard_satellite_detail_drawer_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 test files / 316 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing large `DataPanel` chunk
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing satellite resource rows already combine backend service summaries,
    KPI slices, and snapshot fallbacks. This task reuses those rows instead of
    introducing new network or compute semantics.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - V2-053 should add virtualization or backend paging for large detail tables.
  - Backend `node_detail_summary_v1` should eventually expose selected
    satellite coverage, beam, and resource timeline sections directly.
  - DataPanel remains a large chunk; future frontend architecture work should
    split large dashboard panels without changing runtime semantics.

## 2026-07-06 - Dashboard User Detail Drawer v1

- Branch: `feature/T226-dashboard-user-detail-drawer-v1`
- Commit: pending in this commit
- Scope: advance V2-051 by adding a deterministic fallback view model for the
  selected-user detail drawer. The dashboard still prefers backend
  `node_detail_summary_v1` cards, but when they are unavailable it now groups
  `user_request_summary_v1` rows into business request, network/path/queue, and
  compute service sections.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/dashboard_user_detail_drawer_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 test files / 315 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing large `DataPanel` chunk
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing backend `node_detail_summary_v1` is already preferred when
    available. This task therefore avoids duplicating backend semantics and only
    improves the fallback drawer structure.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - V2-052 should add the equivalent satellite detail drawer v1.
  - V2-053 should add virtualization or backend paging for large detail tables.
  - Backend node detail cards should eventually carry richer latency timelines,
    reducing the need for frontend fallback grouping.

## 2026-07-06 - Dashboard Information Architecture v3

- Branch: `feature/T225-dashboard-information-architecture-v3`
- Commit: pending in this commit
- Scope: advance V2-050 by adding a backend-owned dashboard information
  architecture v3 contract to `backend_summary`. The standalone dashboard now
  consumes the backend field through typed frontend contracts and renders a
  compact IA card before the existing auxiliary model panels.
- Changed files/modules:
  - `src/leo_twin/services/dashboard_information_architecture.py`
  - `src/leo_twin/services/derived_summary.py`
  - `tests/unit/test_dashboard_information_architecture_v3.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `tests/unit/test_dashboard_information_architecture_styles.py`
  - `docs/dashboard_information_architecture_v3.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m py_compile src/leo_twin/services/dashboard_information_architecture.py src/leo_twin/services/derived_summary.py`
    - Result: passed.
  - `python -m pytest tests/unit/test_dashboard_information_architecture_v3.py tests/unit/test_dashboard_information_architecture_styles.py tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 14 tests.
  - `pnpm --dir frontend test -- dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 test files / 314 tests.
  - `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `pnpm --dir frontend build`
    - Result: passed. Vite reported the existing large `DataPanel` chunk
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing dashboard panels were already feature-heavy, so this task defines
    and exposes the information architecture contract without performing a
    broad dashboard layout rewrite.
  - A Vitest CSS raw-import attempt returned an empty CSS string in the current
    frontend test setup. The CSS hook check was moved to a Python file-read
    contract test to avoid depending on bundler-specific CSS transforms.
  - Existing local runtime/generated config files remain dirty and are
    intentionally not included in this task.
- Known remaining issues / follow-up:
  - V2-051/V2-052 should add dedicated user and satellite detail drawers based
    on this IA contract.
  - V2-053 should replace large detail sections with virtualized or backend
    paginated tables.
  - V2-054 should split model assumptions, KPI credibility, and fidelity
    notices into a clearer product-grade assumptions panel.

## 2026-07-06 - User Documentation v2

- Branch: `feature/T224-user-documentation-v2`
- Commit: pending in this commit
- Scope: advance V2-083 by adding a consolidated user-facing guide for startup,
  health checks, configuration, console/dashboard usage, result export,
  operator diagnostics, benchmark acceptance, and current model boundaries.
  README and current product status now point users to the guide.
- Changed files/modules:
  - `docs/user_guide_v2.md`
  - `tests/unit/test_user_guide_v2_docs.py`
  - `README.md`
  - `docs/current_product_status.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_user_guide_v2_docs.py -q`
    - Result: passed, 2 tests.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing documentation was accurate but scattered. This task adds a stable
    user entry point instead of moving or deleting existing specialized docs.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - A future documentation task should add screenshots or short videos after
    the dashboard and 3D scene layout stabilizes further.
  - Browser-rendered documentation links are not yet checked in CI.

## 2026-07-06 - Operator Diagnostics Bundle v1

- Branch: `feature/T223-operator-diagnostics-bundle-v1`
- Commit: pending in this commit
- Scope: advance V2-082 by adding an operator diagnostics bundle contract and a
  local collection script. The bundle captures launcher health, runtime status,
  version info, user config export, runtime export catalog, diagnostics
  manifest, and copied launcher logs under `artifacts\operator_diagnostics`.
  A `diagnostics_leo_twin.bat` shortcut gives non-developer users a direct
  collection entry point.
- Changed files/modules:
  - `src/leo_twin/services/operator_diagnostics.py`
  - `tests/unit/test_operator_diagnostics_bundle_v1.py`
  - `scripts/collect_operator_diagnostics.ps1`
  - `diagnostics_leo_twin.bat`
  - `leo_twin_launcher.bat`
  - `docs/operator_diagnostics_bundle_v1.md`
  - `docs/integration_demo.md`
  - `docs/current_product_status.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m py_compile src/leo_twin/services/operator_diagnostics.py`
    - Result: passed.
  - `python -m pytest tests/unit/test_operator_diagnostics_bundle_v1.py -q`
    - Result: passed, 3 tests.
  - `python -m pytest tests/unit/test_operator_diagnostics_bundle_v1.py tests/unit/test_launcher_health_v2.py tests/unit/test_build_info_v1.py -q`
    - Result: passed, 8 tests.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\collect_operator_diagnostics.ps1 -JsonSummary`
    - Result: passed. The local run produced a `PARTIAL` diagnostics bundle
      because the currently running backend process predates newer diagnostic
      endpoints, while launcher health and runtime status were collected and
      launcher logs were copied successfully.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - The collector is intentionally tolerant of unavailable backend endpoints:
    it writes per-section error payloads instead of failing before creating a
    bundle.
  - The collection script writes runtime artifacts under `artifacts\`, which
    are not committed.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - Stream diagnostics are included through runtime status when the backend is
    reachable. A future task can add explicit stream cursor/backpressure files
    to the bundle.
  - V2-083 should turn the current scattered docs into a user-facing quickstart,
    configuration guide, dashboard guide, and troubleshooting guide.

## 2026-07-06 - Launcher Health Check v2

- Branch: `feature/T222-launcher-health-check-v2`
- Commit: pending in this commit
- Scope: advance V2-081 by adding a launcher health summary contract and
  machine-readable launcher health output. The health summary reports
  backend/frontend port readiness, HTTP readiness, process ids, process names,
  latest stdout/stderr log paths, repository/config/generated-config paths, and
  recommended diagnostic actions. `scripts/sees_launcher.ps1` now supports
  `status -JsonSummary` and `health -JsonSummary` in addition to the existing
  human-readable status path.
- Changed files/modules:
  - `src/leo_twin/services/launcher_health.py`
  - `tests/unit/test_launcher_health_v2.py`
  - `scripts/sees_launcher.ps1`
  - `docs/launcher_health_check_v2.md`
  - `docs/integration_demo.md`
  - `docs/current_product_status.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m py_compile src/leo_twin/services/launcher_health.py`
    - Result: passed.
  - `python -m pytest tests/unit/test_launcher_health_v2.py -q`
    - Result: passed, 3 tests.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sees_launcher.ps1 status -JsonSummary`
    - Result: passed. The local backend and frontend were both reported as
      `HEALTHY`.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sees_launcher.ps1 health -JsonSummary | ConvertFrom-Json | ConvertTo-Json -Depth 8`
    - Result: passed.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - The launcher already had start/stop/status and basic HTTP waits. This task
    keeps that flow and adds a structured health summary rather than replacing
    the launcher.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - V2-082 should bundle launcher health, runtime status, latest config, stream
    diagnostics, and selected logs into an operator diagnostics package.
  - The JSON summary reports current local process state; tests validate the
    stable contract separately from live port occupancy.

## 2026-07-06 - Version Build Info Endpoint v1

- Branch: `feature/T221-version-build-info-endpoint-v1`
- Commit: pending in this commit
- Scope: advance V2-080 by adding a backend-owned version/build information
  payload and exposing it through `DemoControlPlane.version_info()`,
  `GET /runtime/version`, and `GET /version`. The payload reports backend and
  frontend versions, git commit/branch/dirty state, Python runtime diagnostics,
  diagnostic endpoint list, and hard project constraints.
- Changed files/modules:
  - `src/leo_twin/services/build_info.py`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `tests/unit/test_build_info_v1.py`
  - `tests/integration/test_version_info_endpoint.py`
  - `docs/version_info_endpoint_v1.md`
  - `docs/integration_demo.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m py_compile src/leo_twin/services/build_info.py examples/integration_demo/control_plane.py examples/integration_demo/server.py`
    - Result: passed.
  - `python -m pytest tests/unit/test_build_info_v1.py tests/integration/test_version_info_endpoint.py -q`
    - Result: passed, 3 tests.
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 1 test.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - The working tree intentionally still contains local runtime/generated config
    changes, so the live endpoint may report `git.dirty=true` in this local
    environment. Tests pass explicit git values where deterministic output is
    required.
  - This endpoint is read-only and does not mutate runtime state.
- Known remaining issues / follow-up:
  - V2-081 should add launcher health checks for backend/frontend readiness,
    ports, config path, and log paths.
  - Future packaged builds can replace `0.0.0` versions with release metadata.

## 2026-07-06 - Result Package Export Contract v1

- Branch: `feature/T220-result-package-export-v1`
- Commit: pending in this commit
- Scope: advance V2-073 by adding a product-level result package contract over
  the existing runtime export implementation. The contract defines required
  files, endpoint shape, manifest id, hash policy, archive policy, restore
  scope, benchmark evidence binding, and excluded semantics. A summary helper
  checks whether a runtime export package record satisfies the contract, and a
  real integration export test verifies the current DemoControlPlane export
  package.
- Changed files/modules:
  - `src/leo_twin/services/result_package_contract.py`
  - `tests/unit/test_result_package_contract_v1.py`
  - `tests/integration/test_result_package_export_v1.py`
  - `docs/result_package_contract_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m py_compile src/leo_twin/services/result_package_contract.py`
    - Result: passed.
  - `python -m pytest tests/unit/test_result_package_contract_v1.py tests/integration/test_result_package_export_v1.py -q`
    - Result: passed, 4 tests.
  - `python -m pytest tests/unit/test_runtime_reproducibility.py tests/integration/test_result_package_export_v1.py -q`
    - Result: passed, 3 tests.
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_adapter_persists_runtime_export_catalog -q`
    - Result: passed, 1 test.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Runtime export routes and catalog/restore behavior already existed. This
    task therefore formalizes the product contract and adds validation over the
    current export package instead of rewriting control-plane export code.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - Future benchmark runners should attach result package ids and contract
    summaries to completed model verification reports.
  - Runtime logs are represented by export/catalog metadata in v1; a later
    operations task should add a dedicated operator diagnostics log bundle.

## 2026-07-06 - Benchmark Acceptance Tests v1

- Branch: `feature/T219-benchmark-acceptance-tests-v1`
- Commit: pending in this commit
- Scope: advance V2-072 by adding benchmark acceptance tests over the scenario
  matrix and model verification report template. The tests verify matrix/report
  alignment, deterministic backend summaries for 72/300/1200 baselines, scale
  policy fidelity expectations, small-baseline runtime KPI safety ranges, and
  exact expected-range binding back to config source fields.
- Changed files/modules:
  - `tests/integration/test_benchmark_acceptance_v1.py`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 9 tests.
  - `python -m pytest tests/unit/test_benchmark_scenario_matrix_v1.py tests/unit/test_model_verification_report_template_v1.py tests/integration/test_benchmark_acceptance_v1.py -q`
    - Result: passed, 23 tests.
  - `python -m pytest tests/integration/test_product_acceptance_scenarios.py::test_acceptance_scenarios_leave_event_kernel_unchanged -q`
    - Result: passed, 1 test.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - To avoid duplicating the existing heavier 1200 runtime smoke, the new KPI
    range runtime check runs only the 72-satellite baseline. The 300/1200
    scenarios are still covered for deterministic summaries, config ranges, and
    scale/fidelity policy expectations.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - V2-073 should export completed benchmark evidence into a result package.
  - Later KPI acceptance can add scenario-specific nonzero ranges once the
    benchmark expected outputs are calibrated from repeated deterministic runs.

## 2026-07-06 - Model Verification Report Template v1

- Branch: `feature/T218-model-verification-report-template-v1`
- Commit: pending in this commit
- Scope: advance V2-071 by adding a deterministic model verification report
  template service. The template consumes the benchmark scenario matrix plus
  existing network and compute contracts to produce per-scenario boundary
  conditions, determinism plans, network KPI formula checks, compute
  service-time checks, expected outputs, evidence checklists, known
  limitations, and review decision values.
- Changed files/modules:
  - `src/leo_twin/services/model_verification_report.py`
  - `tests/unit/test_model_verification_report_template_v1.py`
  - `docs/model_verification_report_template_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m py_compile src/leo_twin/services/model_verification_report.py`
    - Result: passed.
  - `python -m pytest tests/unit/test_model_verification_report_template_v1.py -q`
    - Result: passed, 6 tests.
  - `python -m pytest tests/unit/test_benchmark_scenario_matrix_v1.py tests/unit/test_model_verification_report_template_v1.py -q`
    - Result: passed, 14 tests.
  - `python -m pytest tests/integration/test_product_acceptance_scenarios.py::test_acceptance_scenarios_leave_event_kernel_unchanged -q`
    - Result: passed, 1 test.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - This task intentionally creates a report template and evidence checklist
    only. It does not run simulations, generate result packages, or change
    model behavior.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - V2-072 should use this template to add benchmark acceptance tests for
    deterministic summaries, KPI ranges, and scale policy behavior.
  - V2-073 should connect completed benchmark runs to exportable result
    packages with config snapshot, events, metrics, summary, and runtime logs.

## 2026-07-06 - Benchmark Scenario Matrix v1

- Branch: `feature/T217-benchmark-scenario-matrix-v1`
- Commit: pending in this commit
- Scope: advance V2-070 by adding a backend-owned benchmark scenario matrix for
  the shipped 72, 300, and 1200 satellite acceptance configurations. The matrix
  resolves existing YAML through the SEES config loader, records expected
  fidelity modes, compact backend-derived summaries, exact numeric guardrails,
  acceptance command shapes, result artifact expectations, and explicit
  forbidden integration boundaries.
- Changed files/modules:
  - `src/leo_twin/services/benchmark_scenarios.py`
  - `tests/unit/test_benchmark_scenario_matrix_v1.py`
  - `docs/benchmark_scenario_matrix_v1.md`
  - `docs/product_acceptance_scenarios.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m py_compile src/leo_twin/services/benchmark_scenarios.py`
    - Result: passed.
  - `python -m pytest tests/unit/test_benchmark_scenario_matrix_v1.py -q`
    - Result: passed, 8 tests.
  - `python -m pytest tests/integration/test_product_acceptance_scenarios.py::test_acceptance_scenarios_leave_event_kernel_unchanged -q`
    - Result: passed, 1 test.
  - `python -m pytest tests/integration/test_product_acceptance_scenarios.py -q`
    - Result: passed, 5 tests.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - This task intentionally does not add new simulation behavior. It creates a
    reusable acceptance matrix over existing shipped configs to avoid another
    hand-maintained tuple/table drift source.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - V2-071 should add a model verification report template that consumes this
    matrix and records formulas, assumptions, boundary conditions, and expected
    outputs per benchmark.
  - V2-072 should extend acceptance tests from structural guardrails to
    deterministic summary and KPI range checks.

## 2026-07-06 - Cache Offload Migration Contracts v1

- Branch: `feature/T216-cache-offload-migration-contracts-v1`
- Commit: pending in this commit
- Scope: advance V2-033 with a product-level
  `cache_offload_migration_contract_v1`. The contract defines deterministic
  action families for cache lookup, cache fill, task offload, and service
  migration, including eligibility fields, decision fields, runtime
  observability fields, statuses, deterministic inputs, and excluded semantics.
  The backend-derived summary now exposes the contract with behavior flags set
  to disabled, so the frontend can explain the roadmap vocabulary without
  implying active runtime behavior.
- Changed files/modules:
  - `src/leo_twin/schema/cache_offload_migration_contract.py`
  - `src/leo_twin/schema/__init__.py`
  - `src/leo_twin/services/derived_summary.py`
  - `tests/unit/test_cache_offload_migration_contract_v1.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `frontend/src/core/event_types/index.ts`
  - `docs/cache_offload_migration_contract_v1.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m py_compile src/leo_twin/schema/cache_offload_migration_contract.py src/leo_twin/services/derived_summary.py`
    - Result: passed.
  - `python -m pytest tests/unit/test_cache_offload_migration_contract_v1.py tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 12 tests.
  - `python -m pytest tests/unit/test_compute_resource_contract_v2.py::test_backend_summary_exposes_compute_resource_contract_v2 -q`
    - Result: passed, 1 test.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - This task intentionally does not implement cache, offload, or migration
    behavior. It adds a contract and a backend-derived explanation surface only,
    matching V2-033 scope.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - Future tasks should emit runtime observability fields when cache/offload/
    migration decisions become active.
  - A dashboard model assumptions panel should display this contract alongside
    compute resource and service placement contracts.

## 2026-07-06 - Compute Task Timeline Summary v1

- Branch: `feature/T215-compute-task-timeline-summary-v1`
- Commit: pending in this commit
- Scope: advance V2-032 by adding a backend-owned
  `compute_task_timeline_summary_v1` to runtime status. The summary is derived
  from existing `service_latency_history_v1` and exposes task count, complete
  task count, queued task count, aggregate queue delay, aggregate execution
  delay, averages, and bounded recent task stage rows. The standalone dashboard
  consumes this backend summary in the compute resource panel instead of
  deriving task-level queue/execution totals locally.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `tests/unit/test_runtime_observability.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m py_compile src/leo_twin/services/runtime_observability.py`
    - Result: passed.
  - `python -m pytest tests/unit/test_runtime_observability.py -q`
    - Result: passed, 3 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 313 tests. The project script currently runs
      the full frontend Vitest suite for this invocation.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 1 test.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing service latency history already had component timelines, so the
    new summary is deliberately a backend-owned aggregation/explanation layer
    rather than a duplicate per-service trace.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - The summary is still derived from recent service latency history. It is not
    yet a full task queue ledger with per-node queue depth samples, deadlines,
    preemption, migration, or cache/offload state.
  - A later V2-032/V2-033 task should add a dedicated queue ledger contract and
    selected-task detail drawer once the runtime emits richer task queue events.

## 2026-07-06 - Service Placement Observability v1

- Branch: `feature/T214-service-placement-observability-v1`
- Commit: pending in this commit
- Scope: enrich the existing Service Placement Model v2 runtime observability
  without changing placement decisions. Route-aware compute decisions now carry
  a bounded, deterministic `service_placement_candidate_queue_label` that
  summarizes up to five candidate nodes by node id, placement status,
  `available_at`, queued task count, and finish/rejection detail. Metrics
  service latency history, runtime user summaries, node detail cards, frontend
  runtime contract types, and dashboard placement labels consume the backend
  field directly.
- Changed files/modules:
  - `src/leo_twin/models/compute/network_aware.py`
  - `src/leo_twin/services/metrics/collector.py`
  - `src/leo_twin/services/runtime_observability.py`
  - `tests/unit/test_network_aware_compute.py`
  - `tests/unit/test_metrics_module.py`
  - `tests/unit/test_runtime_observability.py`
  - `tests/integration/test_compute_service_lifecycle.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `docs/service_placement_model_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m py_compile src/leo_twin/models/compute/network_aware.py src/leo_twin/services/metrics/collector.py src/leo_twin/services/runtime_observability.py`
    - Result: passed.
  - `python -m pytest tests/unit/test_network_aware_compute.py tests/unit/test_metrics_module.py::test_service_latency_history_includes_placement_candidate_queue_label tests/unit/test_runtime_observability.py tests/integration/test_compute_service_lifecycle.py -q`
    - Result: passed, 14 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 312 tests. The project script currently runs
      the full frontend Vitest suite for this invocation.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Service placement contract and runtime behavior already existed in the
    current codebase, so this task was narrowed from a duplicate contract task
    to a bounded observability task.
  - Candidate queue details can be large in high-scale scenarios; the emitted
    label is capped to five normalized candidates and appends `+N more`.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - The label is a compact text summary, not a full candidate table or paged
    placement-detail endpoint. A later dashboard task should add a dedicated
    selected-request placement drawer with candidate rows and queue history.
  - This task does not change placement policy, task queue discipline,
    preemption, migration, cache/offload, or packet-level network behavior.

## 2026-07-06 - Compute Resource Bottleneck v1

- Branch: `feature/T213-compute-resource-bottleneck-v1`
- Commit: pending in this commit
- Scope: add a backend-owned compute resource bottleneck summary to runtime
  metrics and display it in the standalone data dashboard. The summary selects
  the most constrained resource vector dimension deterministically across CPU
  FP32/FP64, GPU FP32/FP16, NPU INT8, memory, and storage, and exposes resource,
  label, utilization, used/total/available, and pressure status fields. The
  dashboard consumes those fields directly instead of deriving product semantics
  locally.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `tests/unit/test_metrics_module.py`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `python -m py_compile src/leo_twin/services/metrics/collector.py`
    - Result: passed.
  - `python -m pytest tests/unit/test_metrics_module.py::test_metrics_collector_reports_compute_resource_pool_proxy tests/unit/test_metrics_module.py::test_metrics_collector_reports_estimated_vector_resource_usage -q`
    - Result: passed, 2 tests.
  - `python -m pytest tests/unit/test_metrics_module.py -q`
    - Result: passed, 22 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 312 tests. The project script currently runs
      the full frontend Vitest suite for this invocation.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
- Problems encountered and handling:
  - Frontend tests initially failed because `metricString()` already existed in
    `DataPanel.tsx`; the duplicate helper was removed and the existing trimmed
    helper is reused.
  - A metrics regression test caught that legacy scalar nodes expose default
    zero-valued CPU vector usage fields. Bottleneck CPU FP32 usage now uses
    explicit vector usage only for `RESOURCE_VECTOR_ESTIMATED` nodes and falls
    back to `capacity - available_capacity` for scalar compatibility nodes.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - This task reports resource bottlenecks from current aggregate usage only. It
    does not add service placement, task queueing, offload, cache, or migration
    behavior; those remain planned V2-031/V2-032 follow-up tasks.

## 2026-07-06 - Dashboard Route Explanation Facets v1

- Branch: `feature/T212-dashboard-route-explanation-facets-v1`
- Commit: pending in this commit
- Scope: upgrade the dashboard route explanation filters from a single text
  search to structured controls. The table now preserves backend route
  availability, business type, and bottleneck component fields in its display
  model and supports combined filtering by text, availability, business type,
  and bottleneck type. This keeps the dashboard aligned with backend-owned
  route semantics rather than deriving product meaning locally.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 310 tests. The project script currently runs
      the full frontend Vitest suite for this invocation.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - None in implementation. The text filter remains backward compatible through
    `filterRouteExplanationRows(rows, string)` while structured criteria use a
    typed filter object.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - Filter options are currently fixed to the known route explanation enums. A
    later backend/frontend contract can expose enum catalogs if product variants
    expand.

## 2026-07-06 - Dashboard Route Explanation Filters v1

- Branch: `feature/T211-dashboard-route-explanation-filters-v1`
- Commit: pending in this commit
- Scope: add a dedicated dashboard filter for backend-owned
  `route_explanation_summary_v1` rows. The filter searches route id, flow id,
  business label, next hop, capacity/demand label, route pressure, bottleneck
  label, explanation label, and path label. This keeps route explanation
  filtering separate from the existing user/satellite node detail filter.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 310 tests. The project script currently runs
      the full frontend Vitest suite for this invocation.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - None in implementation. Empty states distinguish between waiting for
    backend route explanations and a filter that matches zero rows.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - The filter is still a single text search. A later dashboard pass should add
    structured chips/dropdowns for bottleneck component, business type, and
    availability.

## 2026-07-06 - Dashboard Route Explanations v1

- Branch: `feature/T210-dashboard-route-explanations-v1`
- Commit: pending in this commit
- Scope: render backend-owned `route_explanation_summary_v1` records in the
  standalone dashboard network KPI section. The dashboard now shows a route
  explanation table with route id, business type, next hop, capacity/demand,
  route pressure, bottleneck reason, explanation label, and path tooltip. The
  display is derived from runtime status and keeps the existing layout and
  route-constraint table.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 309 tests. The project script currently runs
      the full frontend Vitest suite for this invocation.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - None in implementation. The table reuses existing route-table styling to
    avoid broad dashboard layout changes.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - The table is read-only and limited to the backend status window. A later
    dashboard pass should add filters for bottleneck, user, satellite, and
    business type.

## 2026-07-06 - Route Explanation Records v1

- Branch: `feature/T209-route-explanation-records-v1`
- Commit: pending in this commit
- Scope: add backend-owned route explanation records to runtime status as
  `route_explanation_summary_v1`. The summary is derived from the visible
  runtime snapshot and service history and reports route/flow/user ids, source
  and destination, selected satellite, primary next hop, path, route pressure,
  capacity/demand/latency/loss, business type, bottleneck component, bottleneck
  reason, and compact explanation label. This does not change routing behavior,
  network algorithms, frontend architecture, or Event Kernel behavior.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `frontend/src/core/event_types/index.ts`
  - `tests/unit/test_runtime_observability.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/integration_demo.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `$env:PYTHONPATH='.'; python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 3 tests.
  - `python -m py_compile src/leo_twin/services/runtime_observability.py examples/integration_demo/control_plane.py`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Existing user and satellite runtime rows already carried partial route
    context. T209 keeps those fields intact and adds a separate summary object
    so consumers can use one backend-owned explanation contract instead of
    reverse-engineering rows.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - The summary explains selected runtime routes; it does not enumerate
    discarded route alternatives yet.
  - A follow-up dashboard task should render the route explanation table with
    filtering by user, satellite, bottleneck, and business type.

## 2026-07-06 - Network Pressure Dynamics v1

- Branch: `feature/T208-network-pressure-dynamics-v1`
- Commit: pending in this commit
- Scope: add deterministic simulation-time pressure dynamics to flow-level
  network KPI proxies. `MetricsCollector.kpi_time_series(sim_time=...)` now
  uses the provided runtime simulation time for the current tail sample and
  exposes time-window pressure factor, phase, pressure loss proxy,
  pressure delay-variation proxy, and time-adjusted delivered throughput. The
  Network Model Contract v2 source fields and dashboard tail decomposition were
  updated so frontend explanations are backend-owned. This remains a
  flow-level proxy model and does not introduce packet-level simulation or Event
  Kernel changes.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `src/leo_twin/schema/network_model_contract.py`
  - `tests/unit/test_metrics_module.py`
  - `tests/unit/test_network_model_contract_v2.py`
  - `tests/unit/test_network_kpi_provenance_v2.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/network_kpi_provenance_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `$env:PYTHONPATH='.'; python -m pytest tests/unit/test_metrics_module.py tests/unit/test_network_model_contract_v2.py tests/unit/test_network_kpi_provenance_v2.py -q`
    - Result: passed, 28 tests.
  - `$env:PYTHONPATH='.'; python -m pytest tests/integration/test_runtime_session_control.py::test_runtime_kpi_series_changes_with_configured_flow_demand tests/integration/test_runtime_session_control.py::test_runtime_kpi_series_exposes_initial_baseline_for_single_live_sample tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer tests/integration/test_config_control.py::test_network_stress_template_exposes_nonzero_time_varying_network_kpis -q`
    - Result: passed, 4 tests.
  - `python -m py_compile src/leo_twin/services/metrics/collector.py src/leo_twin/schema/network_model_contract.py`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 307 tests. The project script currently runs
      the full frontend Vitest suite for this invocation.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - The first time-pressure formula allowed a single completed flow to create
    positive delay variation in an existing low-scope unit fixture. The formula
    now requires demand pressure, link congestion, or more than one successful
    flow before completed-flow throughput pressure contributes to time pressure.
  - The initial dynamic test used unequal flow latencies, so normal
    flow-latency variation masked the time-pressure variation. The test now uses
    equal flow latencies to isolate the time-window pressure term.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - The dynamic pressure is still a deterministic product proxy, not a validated
    RF or packet network model.
  - V2-023 should add route explanation records so users can see which route,
    bottleneck, and next-hop choices produced each KPI trend.

## 2026-07-06 - Dashboard Network KPI Credibility v1

- Branch: `feature/T207-dashboard-network-kpi-credibility-v1`
- Commit: pending in this commit
- Scope: render the backend-owned `network_kpi_credibility_v1` summary in the
  standalone dashboard network KPI section. The UI now shows trusted,
  partial, missing, and invalid packet-level states from backend status fields,
  including KPI coverage, source-field coverage, flow-level proxy count,
  packet-level guard count, zero-value explanation coverage, missing metrics,
  and backend caveats. This does not change frontend architecture, KPI formulas,
  runtime control, or Event Kernel behavior.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/network_kpi_provenance_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 306 tests. The project script currently runs
      the full frontend Vitest suite for this invocation.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
- Problems encountered and handling:
  - The user shell did not have `node` on `PATH`, so the first `pnpm` attempt
    failed before tests started. Re-ran with the bundled Codex Node/Pnpm runtime
    and validation passed.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - V2-022 should make the network pressure inputs more time-varying so the
    now-visible credibility card is paired with richer KPI dynamics.
  - A future dashboard pass can render the full `network_kpi_provenance_v2.kpis`
    table instead of only the compact trust summary.

## 2026-07-06 - Network KPI Credibility v1

- Branch: `feature/T206-network-kpi-credibility-v1`
- Commit: pending in this commit
- Scope: add backend-owned network KPI trust/coverage reporting. Runtime
  status now exposes `network_kpi_credibility_v1`, derived from
  `network_kpi_provenance_v2`, with observed/missing KPI counts,
  packet-level metric guard status, flow-level proxy count, zero-value
  explanation coverage, source-field coverage, missing metric names, and
  user-facing caveats. This does not change KPI formulas or Event Kernel
  behavior.
- Changed files/modules:
  - `src/leo_twin/services/network_kpi_provenance.py`
  - `examples/integration_demo/control_plane.py`
  - `tests/unit/test_network_kpi_provenance_v2.py`
  - `tests/integration/test_runtime_session_control.py`
  - `frontend/src/core/event_types/index.ts`
  - `docs/network_kpi_provenance_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `$env:PYTHONPATH='.'; python -m pytest tests/unit/test_network_kpi_provenance_v2.py tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 3 tests.
  - `python -m py_compile src/leo_twin/services/network_kpi_provenance.py examples/integration_demo/control_plane.py`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - The first unit test expected a zero-valued KPI but the fixture had all KPI
    runtime values positive. The fixture now sets route blocking ratio to zero
    so the zero-value explanation path is covered deterministically.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - The dashboard type contract is ready, but the UI still needs a visible
    `network_kpi_credibility_v1` trust badge/card.
  - V2-022 time-varying network pressure remains the next model-fidelity step.

## 2026-07-06 - Dashboard User Config Text Preflight v1

- Branch: `feature/T205-dashboard-user-config-text-preflight-v1`
- Commit: pending in this commit
- Scope: connect the standalone dashboard configuration preflight panel to the
  backend JSON/YAML text validation endpoint introduced in T204. The dashboard
  now keeps the original JSON mapping mode and adds auto text, YAML text, and
  JSON text modes. Text modes call
  `POST /scenario/user-config/validate-text?format=...`; the preflight result
  displays backend `text_parse` metadata and still applies only the normalized
  config returned by the backend.
- Changed files/modules:
  - `frontend/src/app/api.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/api.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/integration_demo.md`
  - `docs/user_configuration_schema_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts`
    - Result: passed, 25 files / 302 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - No implementation blocker. The task deliberately avoids adding file-system
    upload or changing the apply command path; it only adds text validation
    modes to the existing preflight card.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - A later task can add a richer file picker and full diff confirmation modal.
  - Text mode uses the backend's deterministic simplified YAML parser, matching
    the current config loader limitations.

## 2026-07-06 - User Config Text Preflight v1

- Branch: `feature/T204-user-config-text-preflight-v1`
- Commit: pending in this commit
- Scope: add a backend validate-only text preflight path for user configuration
  files. `DemoControlPlane.user_configuration_validate_text()` accepts raw
  UTF-8 JSON or simplified YAML text with `format=auto|json|yaml`, parses it
  into the existing user configuration mapping contract, and returns the same
  `USER_CONFIGURATION_VALIDATION_REPORT` plus `text_parse`. The integration
  server exposes `POST /scenario/user-config/validate-text`, while the existing
  JSON mapping endpoint remains unchanged.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `tests/integration/test_config_control.py`
  - `frontend/src/core/event_types/index.ts`
  - `docs/integration_demo.md`
  - `docs/user_configuration_schema_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `$env:PYTHONPATH='.'; python -m pytest tests/integration/test_config_control.py::test_control_plane_validates_user_configuration_text_without_applying tests/integration/test_config_control.py::test_control_plane_validates_user_configuration_without_applying -q`
    - Result: passed, 2 tests.
  - `python -m py_compile examples/integration_demo/control_plane.py examples/integration_demo/server.py`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Initial implementation returned the validation response before attaching
    `text_parse`; the text preflight test caught it and the response builder
    now assigns the payload before returning.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - The dashboard still uses the JSON editor; a later frontend task should add
    upload/paste mode selection for YAML/JSON text and call the new endpoint.
  - The YAML parser is the existing deterministic simplified project parser,
    not a general YAML 1.2 implementation.

## 2026-07-06 - User Config Apply Readiness v1

- Branch: `feature/T203-user-config-apply-readiness-v1`
- Commit: pending in this commit
- Scope: add backend-owned runtime readiness semantics to user configuration
  preflight reports and render them in the dashboard. Accepted
  `USER_CONFIGURATION_VALIDATION_REPORT` payloads now include
  `apply_readiness`, which records whether applying is allowed, current
  controller/session lifecycle, confirmation recommendation, operator action,
  and session/stream side effects. The dashboard renders those fields in the
  preflight card before `CONFIG_UPDATE` can be sent.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `tests/integration/test_config_control.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/integration_demo.md`
  - `docs/user_configuration_schema_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `$env:PYTHONPATH='.'; python -m pytest tests/integration/test_config_control.py::test_control_plane_validates_user_configuration_without_applying tests/integration/test_config_control.py::test_control_plane_applies_preflight_normalized_user_configuration tests/integration/test_config_control.py::test_control_plane_reports_running_apply_readiness -q`
    - Result: passed, 3 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 300 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - A test exposed that small demo sessions can already be in
    `lifecycle_state=INITIALIZED` while the control-plane `initialized` flag is
    false. The readiness logic was adjusted to report based on the actual
    session lifecycle as well as the control-plane flag.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - The readiness display is informational; a later task can add a dedicated
    confirmation modal for running-session reinitialization.
  - YAML/file upload and full diff filtering remain future configuration
    workflow work.

## 2026-07-06 - Dashboard User Config Diff v1

- Branch: `feature/T202-dashboard-user-config-diff-v1`
- Commit: pending in this commit
- Scope: render the backend-owned user configuration `change_summary` inside
  the dashboard preflight result card. The UI now shows total changed field
  count, preview coverage, section counts, hidden preview count when present,
  and bounded changed field rows before the user sends `CONFIG_UPDATE`. The
  rendering remains driven by the backend report rather than local frontend
  inference.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/integration_demo.md`
  - `docs/user_configuration_schema_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 300 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - No implementation blocker. The row preview is intentionally bounded to keep
    the existing dashboard layout stable.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - A richer diff confirmation modal, YAML upload, and full diff search/filter
    remain future configuration workflow work.

## 2026-07-06 - User Config Preflight Diff v1

- Branch: `feature/T201-user-config-preflight-diff-v1`
- Commit: pending in this commit
- Scope: enrich backend user configuration preflight with a deterministic
  `change_summary`. Accepted validation reports now compare the current
  effective `SEESConfig` with the backend-normalized candidate and report
  changed field count, root-section counts, sorted bounded preview rows,
  current/candidate values, change type, and hidden preview count. Rejected
  validation reports return `change_summary: null`. Frontend event types were
  extended so a later dashboard task can render the backend-owned diff without
  inferring it locally.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `tests/integration/test_config_control.py`
  - `frontend/src/core/event_types/index.ts`
  - `docs/integration_demo.md`
  - `docs/user_configuration_schema_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `$env:PYTHONPATH='.'; python -m pytest tests/integration/test_config_control.py::test_control_plane_validates_user_configuration_without_applying tests/integration/test_config_control.py::test_control_plane_applies_preflight_normalized_user_configuration -q`
    - Result: passed, 2 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - Candidate configs are normalized against backend defaults, so omitted fields
    can intentionally appear as changes relative to the currently loaded demo
    config. Tests assert deterministic ordering and key changed paths instead of
    assuming an exact total change count.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - Dashboard rendering of `change_summary` should be implemented as the next
    frontend slice.
  - The diff is a bounded leaf-field preview, not a full interactive diff UI.

## 2026-07-06 - Dashboard User Config Apply v1

- Branch: `feature/T200-dashboard-user-config-apply-v1`
- Commit: pending in this commit
- Scope: add the guarded apply step after dashboard user configuration
  preflight. The backend validation report now declares the exact
  `CONFIG_UPDATE` apply command, including `normalized_config` as the payload
  source, payload format, explicit user-action requirement, preflight
  requirement, and runtime/session side effect. The dashboard still never
  auto-applies editor text: it enables "应用配置" only after a successful
  backend preflight and sends the backend-normalized mapping through the
  existing control channel.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `tests/integration/test_config_control.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/api.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/integration_demo.md`
  - `docs/user_configuration_schema_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `$env:PYTHONPATH='.'; python -m pytest tests/integration/test_config_control.py::test_control_plane_validates_user_configuration_without_applying tests/integration/test_config_control.py::test_control_plane_applies_preflight_normalized_user_configuration -q`
    - Result: passed, 2 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts`
    - Result: passed, 25 files / 299 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - `$env:PYTHONPATH='.'; python -m pytest tests/unit/test_user_configuration_schema_v2.py tests/integration/test_config_control.py::test_control_plane_validates_user_configuration_without_applying tests/integration/test_config_control.py::test_control_plane_applies_preflight_normalized_user_configuration -q`
    - Result: passed, 8 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check -- <task files>`
    - Result: passed.
- Problems encountered and handling:
  - The shell environment did not have `node` on PATH, so the first frontend
    pnpm commands failed before running tests. The commands were rerun with the
    bundled Codex Node/Pnpm paths.
  - The first TypeScript check found `controlClient` used before declaration in
    the new apply callback. The callback was moved after `controlClient`
    creation and TypeScript passed.
  - Local runtime/generated config files remain dirty and are intentionally not
    included in this task.
- Known remaining issues / follow-up:
  - YAML/file upload and rich config diff review are still future work.
  - Applying config reinitializes the runtime session through the current
    `CONFIG_UPDATE` path; a later task can add a dedicated apply preflight
    confirmation panel with runtime stopped/running warnings.

## 2026-07-06 - Dashboard User Config Preflight v1

- Branch: `feature/T199-dashboard-user-config-preflight-v1`
- Commit: pending in this commit
- Scope: connect the dashboard user configuration panel to the backend
  validate-only endpoint introduced in T198. The frontend now exposes
  `validateUserConfigurationCandidate()` for
  `POST /scenario/user-config/validate`, renders a JSON mapping preflight box
  in the standalone dashboard, and displays accepted/rejected
  `USER_CONFIGURATION_VALIDATION_REPORT` results including mutation policy,
  normalized config hash, backend validation errors, and unknown/defaulting
  policy. The UI is validate-only: it parses JSON and calls the preflight API,
  but it does not send `CONFIG_UPDATE`, load templates, restore packages, write
  files, initialize runtime, or apply candidate configuration.
- Changed files/modules:
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/app/api.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/api.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/integration_demo.md`
  - `docs/user_configuration_schema_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts appCssLayout.test.js`
    - Result: passed, 25 files / 298 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `$env:PYTHONPATH='.'; python -m pytest tests/integration/test_config_control.py::test_control_plane_validates_user_configuration_without_applying -q`
    - Result: passed.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - None in implementation. The task intentionally keeps apply/import out of
    scope so invalid configs cannot silently mutate runtime state.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files are intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - The preflight box currently accepts JSON mappings. A later task should add
    file upload/YAML parsing and a guarded apply workflow that requires an
    accepted preflight result.
  - A future UI task should separate DataPanel into smaller lazy chunks; Vite
    still reports the existing DataPanel chunk-size warning.

## 2026-07-06 - User Config Validation API v1

- Branch: `feature/T198-user-config-validate-api-v1`
- Commit: pending in this commit
- Scope: add a validate-only backend preflight endpoint for user-provided
  configuration mappings. The integration demo now exposes
  `POST /scenario/user-config/validate`, which returns
  `USER_CONFIGURATION_VALIDATION_REPORT` with schema id, validation scope,
  mutation policy, normalized config/hash for accepted mappings, and validation
  errors for rejected mappings. The endpoint does not write files, initialize
  runtime state, or apply `CONFIG_UPDATE`; applying a config remains an explicit
  future control action. This task also fixes the T196 scenario-builder summary
  regression by passing only the actual builder seed into runtime explanation
  fields instead of referencing a nonexistent runtime object. Event Kernel and
  simulation models are unchanged.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `src/leo_twin/services/scenario_builder.py`
  - `tests/integration/test_config_control.py`
  - `docs/integration_demo.md`
  - `docs/user_configuration_schema_v2.md`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `$env:PYTHONPATH='.'; python -m pytest tests/integration/test_config_control.py::test_control_plane_validates_user_configuration_without_applying tests/integration/test_config_control.py::test_control_plane_exposes_user_configuration_contract_api tests/unit/test_user_configuration_schema_v2.py tests/unit/test_scenario_builder.py::test_scenario_builder_config_from_sees_config_maps_control_plane_fields -q`
    - Result: passed, 9 tests.
  - `$env:PYTHONPATH='.'; python -m pytest tests/integration/test_config_control.py::test_control_plane_validates_user_configuration_without_applying tests/integration/test_config_control.py::test_control_plane_exposes_user_configuration_contract_api tests/integration/test_config_control.py::test_frontend_control_messages_are_processed tests/unit/test_user_configuration_schema_v2.py tests/unit/test_scenario_builder.py::test_scenario_builder_config_from_sees_config_maps_control_plane_fields tests/unit/test_backend_derived_summary.py::test_configuration_explanation_v2_binds_config_to_backend_semantics -q`
    - Result: passed, 11 tests.
  - `python -m py_compile examples/integration_demo/server.py examples/integration_demo/control_plane.py src/leo_twin/services/scenario_builder.py`
    - Result: passed.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - Targeted tests exposed a T196 regression:
    `scenario_builder_backend_summary()` referenced `config.runtime`, but
    `FullSystemScenarioBuilderConfig` stores only builder-level fields. The
    summary now passes `runtime_seed=config.seed` and leaves unavailable
    runtime mode/speed/duration fields absent.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files are intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - The frontend does not yet provide YAML/JSON upload, validation display, or
    a guarded apply button.
  - The validation endpoint currently accepts JSON mappings; YAML file parsing
    can be added in the frontend/upload workflow or a later backend endpoint.

## 2026-07-06 - Dashboard Configuration Explanation v1

- Branch: `feature/T197-dashboard-configuration-explanation-v1`
- Commit: pending in this commit
- Scope: render the backend-owned `backend_summary.configuration_explanation_v2`
  in the standalone dashboard's auxiliary model analysis area. The new compact
  panel shows the explanation source/schema, configuration surfaces,
  deterministic config policy, forbidden integration boundary, packet-level
  simulation boundary, and per-section current values/excluded semantics. This
  keeps configuration/model explanations backend-owned and avoids frontend
  semantic inference. The task does not change backend model behavior, runtime
  control, Event Kernel behavior, config upload/apply workflows, or dashboard
  architecture.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/user_configuration_schema_v2.md`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 295 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts appCssLayout.test.js`
    - Result: passed, 25 files / 295 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - TypeScript initially kept readonly string-array current values in the
    generic display value union after `Array.isArray`; the formatter now
    explicitly handles object/readonly-array values and returns a string.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files are intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - The panel is compact. A later dashboard task can add a full model
    assumptions/detail drawer that expands every backend section and source
    field.
  - User-provided YAML/JSON validation and guarded apply remain future work.

## 2026-07-06 - Configuration Explanation Summary v2

- Branch: `feature/T196-config-explanation-summary-v2`
- Commit: pending in this commit
- Scope: implement V2-003 by adding backend-owned
  `backend_summary.configuration_explanation_v2`. The new read-only summary
  maps accepted configuration surfaces and sections (`scenario`, `traffic`,
  `network`, `compute`, `runtime`, and `ui`) to current backend model
  semantics, current available values, deterministic/reproducibility policy,
  and explicit excluded capabilities. Runtime values are passed from the
  integration demo and scenario builder where available. Frontend runtime
  contract types and the runtime status contract fixture now include the new
  field. This task does not mutate configuration, add upload/apply behavior,
  change Event Kernel behavior, or alter simulation model execution.
- Changed files/modules:
  - `src/leo_twin/services/derived_summary.py`
  - `src/leo_twin/services/scenario_builder.py`
  - `examples/integration_demo/scenario.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `tests/unit/test_backend_derived_summary.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `docs/system_v2_upgrade_plan.md`
  - `docs/user_configuration_schema_v2.md`
  - `docs/development_log.md`
- Validation:
  - `$env:PYTHONPATH='.'; python -m pytest tests/unit/test_backend_derived_summary.py tests/unit/test_integration_demo_scenario.py::test_demo_scenario_auto_allocates_starlink_like_planes_when_not_explicit tests/unit/test_scenario_builder.py::test_scenario_builder_config_from_sees_config_maps_control_plane_fields -q`
    - Result: passed, 12 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 293 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - `build_backend_derived_summary` previously did not receive runtime fields.
    The new parameters are optional for compatibility, and the demo/scenario
    builder paths now pass current runtime mode, speed, duration, and seed.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files are intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - The dashboard types can now consume `configuration_explanation_v2`, but no
    dedicated UI panel renders the full explanation yet.
  - A later guarded config import task should use the same schema/explanation
    contracts to validate user YAML/JSON before applying changes.

## 2026-07-06 - Dashboard Config Field Browser v1

- Branch: `feature/T195-dashboard-config-field-browser-v1`
- Commit: pending in this commit
- Scope: extend the standalone dashboard's read-only user configuration
  contract panel with a backend-schema field browser. The dashboard now groups
  `UserConfigurationSchemaV2.fields` by backend section, displays each
  section's purpose, total field count, control-panel key field count, detailed
  file-only field count, and representative field paths/labels. This keeps the
  backend user configuration schema as the source of truth and helps users
  distinguish key UI controls from the full YAML/JSON configuration surface.
  The task does not add config upload/apply, does not mutate runtime
  configuration, does not modify simulation models, and does not touch Event
  Kernel behavior.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/user_configuration_schema_v2.md`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 293 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - Windows PowerShell's default console decoding can display UTF-8 Chinese UI
    text as mojibake. File reads and patches used UTF-8-aware contexts where
    needed, and the source files remain UTF-8.
  - The first type-check run exposed a TypeScript narrowing issue around
    `map(...).filter(...)` on readonly display rows. The helper now builds an
    explicitly typed deterministic array instead.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files are intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - The dashboard now explains the schema field surface, but it still does not
    provide a guarded validate/upload/apply workflow for user-provided
    YAML/JSON configs.
  - The field browser shows representative fields per section; a later task can
    add expandable full-field inspection and filtering without changing the
    backend contract.

## 2026-07-06 - Dashboard User Config Contract v1

- Branch: `feature/T194-dashboard-user-config-contract-v1`
- Commit: pending in this commit
- Scope: surface the backend-owned user configuration contract API in the
  standalone dashboard. The frontend now loads
  `/scenario/user-config/schema`, `/scenario/user-config/templates`, and
  `/scenario/user-config/export`, displays schema field counts, key-field
  counts, template count, current config hash, validation status, and exposes
  read-only JSON links/download for schema, templates, and current effective
  config export. This task is read-only from the UI perspective: it does not
  introduce config upload, apply user files, mutate runtime config, modify
  Event Kernel behavior, or change simulation/model logic.
- Changed files/modules:
  - `frontend/src/app/api.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/api.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 292 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - The dashboard already had backend-derived configuration summaries in
    generated config, but those were indirect. This task uses the direct
    read-only contract endpoints added by T193, keeping backend semantics as
    the source of truth.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - Users can inspect and download the current full config, but there is still
    no guarded upload/validate/apply workflow for user-provided YAML/JSON.
  - The dashboard only shows a compact contract summary; a later task should
    add an expandable field browser grouped by schema section.

## 2026-07-06 - User Config Contract API v1

- Branch: `feature/T193-user-config-contract-api-v1`
- Commit: pending in this commit
- Scope: expose the existing backend-owned user configuration schema v2 as
  stable read-only integration demo API endpoints. The demo control plane now
  serves the current schema, approved executable template catalog, and current
  effective SEES config export with a stable config hash and validation status.
  New endpoints are `/scenario/user-config/schema`,
  `/scenario/user-config/templates`, and `/scenario/user-config/export`.
  Configuration import remains explicit through existing control-plane commands
  (`CONFIG_UPDATE`, `LOAD_TEMPLATE`, and `RESTORE_EXPORT_PACKAGE`). This task
  does not modify Event Kernel behavior, model fidelity, frontend rendering, or
  runtime session advancement.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `tests/integration/test_config_control.py`
  - `docs/user_configuration_schema_v2.md`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - `$env:PYTHONPATH='.'; pytest tests/integration/test_config_control.py::test_control_plane_exposes_user_configuration_contract_api tests/unit/test_user_configuration_schema_v2.py tests/unit/test_configuration_view.py -q`
    - Result: passed, 14 tests.
  - `$env:PYTHONPATH='.'; pytest tests/integration/test_config_control.py -q`
    - Result: failed only in `test_config_loads_correctly` because the
      pre-existing local runtime config drift in `configs/sees_control.yaml`
      has `scenario.compute_nodes: 72` while the committed test baseline expects
      `10`. This file is explicitly excluded from task commits and was not
      reset.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - The full config-control integration file depends on the mutable local
    `configs/sees_control.yaml`. The task-specific test uses a temporary config
    output path and passes, so the new API contract is verified without
    touching local runtime state.
  - The API is intentionally read-only. Validation and import semantics are
    surfaced through the schema/export payloads, but mutation remains limited to
    explicit control-plane commands.
- Known remaining issues / follow-up:
  - The frontend does not yet display a dedicated user configuration API panel
    or download button for `/scenario/user-config/export`.
  - A later task should add a guarded upload/validate flow for user-provided
    YAML/JSON before applying it through `CONFIG_UPDATE`.

## 2026-07-06 - Dashboard Restore Command v1

- Branch: `feature/T192-dashboard-restore-command-v1`
- Commit: pending in this commit
- Scope: connect the dashboard runtime export catalog to the backend restore
  control command introduced in T191. The standalone dashboard now shows a
  guarded two-click restore action for a selected export package, sends
  `RESTORE_EXPORT_PACKAGE` over the existing `/control` WebSocket with
  `confirm_restore: true`, tracks pending/error/success restore state, displays
  rollback package feedback from the backend `restore_result`, and reloads the
  runtime state/catalog after a successful restore. Read-only package, compare,
  and preflight links remain non-mutating. This task does not modify Event
  Kernel behavior, backend simulation models, packet/network fidelity, or the
  overall frontend architecture.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/src/config_panel/controlClient.ts`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/controlClient.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- controlClient.test.ts dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 288 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - Running `pnpm --dir frontend test ...` with the ambient PATH failed because
    `node` was not available. The validation was rerun with the bundled Codex
    Node/Pnpm paths and passed.
  - The dashboard restore control needs to remain a write action, not a link.
    The UI now uses a two-click button that dispatches the existing control
    WebSocket command; the GET artifact and preflight routes stay read-only.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - The restore command restores configuration and reinitializes the live
    runtime; it still does not replay archived event/metric timelines.
  - A later task should add a compact post-restore audit card and optional
    rollback command using the generated rollback package id.

## 2026-07-06 - Runtime Export Restore Command v1

- Branch: `feature/T191-runtime-export-restore-command-v1`
- Commit: pending in this commit
- Scope: add an explicit control-plane restore command for persisted runtime
  export packages. `RESTORE_EXPORT_PACKAGE` is accepted only through the
  existing runtime control message path, requires `confirm_restore: true`, runs
  the existing restore preflight, writes a rollback export package for the
  current runtime configuration before mutation, then restores
  `config_snapshot.config` through deterministic SEES config validation,
  config-file write, generated-config write, and clean runtime session
  reinstallation. GET artifact and preflight routes remain read-only. This task
  does not modify Event Kernel behavior, frontend rendering, simulation models,
  or packet/network fidelity.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - `$env:PYTHONPATH='.'; pytest tests/integration/test_runtime_session_control.py -q`
    - Result: passed, 23 tests.
  - `$env:PYTHONPATH='.'; pytest tests/integration/test_live_runtime_streaming.py -q`
    - Result: passed, 12 tests.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - Running `pytest tests/integration/test_runtime_session_control.py -q`
    directly with the system Python environment failed during collection because
    `examples` was not on `PYTHONPATH`. The validation was rerun with
    `PYTHONPATH=.` and passed.
  - The new restore assertion initially compared an empty JSON list to an empty
    tuple. The test was corrected to assert empty-batch semantics instead of a
    Python container type.
  - The restore implementation was tightened to apply the fully validated and
    default-filled `SEESConfig` mapping rather than merging a raw package dict
    over the current config.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - The dashboard can inspect restore preflight results, but it still does not
    expose a guarded restore confirmation button. A future frontend task should
    invoke `RESTORE_EXPORT_PACKAGE` through the control WebSocket and present
    the rollback package id after success.
  - Runtime export restore currently restores configuration and restarts the
    session; it does not replay exported event/metric timelines into the live
    runtime.

## 2026-07-06 - Dashboard Restore Preflight Summary v1

- Branch: `feature/T190-dashboard-restore-preflight-summary-v1`
- Commit: pending in this commit
- Scope: render runtime export restore preflight results directly in the
  standalone dashboard for the selected catalog package. The app now loads
  `/runtime/export/packages/{package_id}/restore-preflight` alongside the
  existing compare preview, keeps compare and preflight failures isolated, and
  the data panel displays restore readiness, confirmation requirement, config
  write/reset impact, current lifecycle state, preflight hash, warnings, and
  blocked reasons. This is frontend-only on top of the existing read-only
  preflight endpoint; it does not restore packages, write config files, stop
  sessions, mutate runtime state, modify Event Kernel behavior, or change
  simulation/model logic.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 286 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - The preflight preview is related to compare but should not be blocked by a
    compare request failure. The app now loads compare and preflight with
    `Promise.allSettled()` and reports independent error states.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - The UI still does not execute restore. A future task should introduce a
    guarded confirmation flow with rollback package creation and control-plane
    reinitialization through existing configuration services.

## 2026-07-06 - Runtime Export Restore Preflight v1

- Branch: `feature/T189-runtime-export-restore-preflight-v1`
- Commit: pending in this commit
- Scope: add a deterministic, read-only restore preflight for persisted runtime
  export packages. The backend now exposes
  `/runtime/export/packages/{package_id}/restore-preflight`, validates the
  package `config_snapshot.json` as a potential restore source, compares package
  config against current runtime config, and reports readiness (`NO_CHANGE`,
  `READY`, or `BLOCKED`), confirmation requirements, config hashes, diff counts,
  warnings, next action, and a stable preflight hash. Frontend contracts, API
  helper, and dashboard catalog row links were added so users can inspect the
  preflight result. This task does not restore packages, write config files,
  stop sessions, mutate runtime state, modify Event Kernel behavior, or change
  simulation/model logic.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/app/api.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/api.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_adapter_serves_persisted_runtime_export_artifacts tests/integration/test_runtime_session_control.py::test_demo_server_stream_query_parses_cursor_options -q`
    - Result: passed, 2 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 283 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - Restore semantics must not be hidden behind a link that mutates state. The
    endpoint was therefore kept strictly read-only and returns
    `would_mutate_current_runtime: false` plus explicit warnings/next action
    instead of performing any restore.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - A future restore flow should require an explicit confirmation command,
    preserve a rollback package, and reinitialize runtime services through the
    existing control-plane configuration path.

## 2026-07-06 - Dashboard Selected Export Compare v1

- Branch: `feature/T188-dashboard-selected-export-compare-v1`
- Commit: pending in this commit
- Scope: make the standalone dashboard compare any catalog-listed runtime export
  package, not only the latest package. The app keeps a selected package id,
  preserves it across catalog refreshes when the package still exists, loads
  `/runtime/export/packages/{package_id}/compare` on demand, and reports
  loading/error states in the data panel. Catalog rows now provide a `对比`
  button for the inline summary plus a `JSON` link for the raw preview. This is
  frontend-only, read-only observation behavior; it does not restore packages,
  mutate configuration, modify Event Kernel behavior, or change model logic.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- appSurface.test.ts dataPanel.test.ts api.test.ts`
    - Result: passed, 25 files / 282 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - Catalog refresh can otherwise overwrite a user's selected compare target
    with the latest package. A pure selection helper now preserves the selected
    package when it still appears in the catalog and falls back to the latest
    package only when necessary.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - The compare summary is still embedded above the catalog. A follow-up can
    move it into a dedicated selected-package drawer with a guarded restore
    preflight once the restore flow is designed.

## 2026-07-06 - Dashboard Export Compare Summary v1

- Branch: `feature/T187-dashboard-export-compare-summary-v1`
- Commit: pending in this commit
- Scope: render the latest persisted runtime export package compare preview
  directly in the standalone dashboard. The app now loads
  `/runtime/export/packages/{package_id}/compare` for the latest catalog record
  as an optional observation-plane source, and the data panel displays whether
  the package config matches the current runtime config, section-level match
  labels, compare hash, diff count, and a bounded set of changed JSON paths.
  This is frontend-only on top of the existing read-only compare endpoint; it
  does not restore packages, mutate configuration, modify Event Kernel
  behavior, or change simulation/model logic.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 278 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - The first helper draft could have displayed the backend `diff_limit` rather
    than the number of rows actually rendered by the dashboard. The display was
    corrected to report the visible diff row count when the frontend applies a
    tighter display limit.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - The compare summary is read-only and only tracks the latest catalog record.
    Recommended next task: add a selected-package compare drawer and then a
    guarded restore preflight that remains explicit and reversible.

## 2026-07-06 - Runtime Export Compare Preview v1

- Branch: `feature/T186-runtime-export-compare-preview-v1`
- Commit: pending in this commit
- Scope: add a deterministic read-only compare preview for persisted runtime
  export packages. The demo backend now serves
  `/runtime/export/packages/{package_id}/compare`, reads the package
  `config_snapshot.json`, and compares its `config` and `generated_config`
  sections with the current backend runtime configuration. The response reports
  compatibility, section-level match flags, manifest hash equality, diff counts,
  a bounded list of changed JSON paths, and a stable compare hash. The dashboard
  catalog row exposes a `对比` link to this preview. This task does not restore
  scenarios, mutate configuration, modify Event Kernel behavior, or change
  runtime progression/model logic.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/app/api.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/api.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_adapter_serves_persisted_runtime_export_artifacts tests/integration/test_runtime_session_control.py::test_demo_adapter_persists_runtime_export_catalog tests/integration/test_runtime_session_control.py::test_demo_server_stream_query_parses_cursor_options -q`
    - Result: passed, 3 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 275 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - The compare endpoint must not trigger package regeneration or restore. It
    was implemented as a pure read of catalog-registered `config_snapshot.json`
    plus the current controller/generated config, with a bounded diff list to
    avoid large responses for future full user configurations.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - The dashboard currently opens the compare preview JSON. A follow-up
    dashboard task should render the compare summary inline and add a guarded
    "restore from package" preflight flow that remains read-only until the user
    explicitly confirms configuration replacement.

## 2026-07-06 - Runtime Export Artifact Routes v1

- Branch: `feature/T185-runtime-export-artifact-routes-v1`
- Commit: pending in this commit
- Scope: add read-only persisted export artifact routes so dashboard catalog
  rows can open deterministic replay package records, manifests, registered
  files, and already-created archives without creating a new export. The demo
  server now serves `/runtime/export/packages/{package_id}`,
  `/runtime/export/packages/{package_id}/manifest`,
  `/runtime/export/packages/{package_id}/archive`, and
  `/runtime/export/packages/{package_id}/files/{filename}` from the persisted
  catalog with export-root path safety checks. The standalone dashboard catalog
  rows now expose record, manifest, and archive actions. Event Kernel behavior,
  runtime session progression, export package generation, and model logic are
  unchanged.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/app/api.ts`
  - `frontend/src/app/App.css`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/api.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_adapter_serves_persisted_runtime_export_artifacts tests/integration/test_runtime_session_control.py::test_demo_adapter_persists_runtime_export_catalog tests/integration/test_runtime_session_control.py::test_demo_server_stream_query_parses_cursor_options -q`
    - Result: passed, 3 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 274 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
- Problems encountered:
  - The existing catalog contains both `PACKAGE` and `ARCHIVE` records for the
    same `package_id`; artifact lookup now deterministically prefers the
    `ARCHIVE` record when present so archive metadata is available while still
    serving the registered package files.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - Artifact routes are read-only downloads/openable JSON endpoints. A future
    replay-browser task should add a scenario restore flow that loads a package
    manifest and compares it with the current runtime configuration before
    replay.

## 2026-07-05 - Dashboard Export Catalog View v1

- Branch: `feature/T184-dashboard-export-catalog-view-v1`
- Commit: pending in this commit
- Scope: add a dashboard view for the backend-persisted runtime export catalog.
  The standalone data panel now loads `/runtime/export/catalog` as an optional
  observation-plane source and renders a compact replay-package catalog with
  export type, package id, simulation time, event count, archive name, and
  short hash. This task is frontend-only and does not change Event Kernel,
  runtime export semantics, models, or control protocol behavior.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `git diff --check`
    - Result: passed. Git still reported the pre-existing CRLF warning for
      local runtime/config drift in `configs/generated_full_system_demo.json`
      and `configs/sees_control.yaml`.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts api.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 273 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning after minification.
- Problems encountered:
  - PowerShell `Get-Content` displayed UTF-8 Chinese text as mojibake in the
    terminal, so patches were applied using stable English identifiers and
    verified with `rg`, which displayed the source text correctly.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - The catalog view is read-only and displays the latest persisted records.
    Recommended next task: add explicit package-open/download actions per row
    once the backend exposes stable per-package artifact routes.

## 2026-07-05 - Compute Resource Contract v2

- Branch: `feature/T169-compute-resource-contract-v2`
- Commit: pending in this commit
- Scope: implement V2-030 by adding a product-level
  `leo_twin.compute_resource_contract.v2` contract. The contract formalizes
  satellite-hosted `ComputeResourceVector` lanes, task demand lanes, legacy
  `compute_capacity` / `compute_demand` compatibility, deterministic
  bottleneck service-time estimation, memory/storage capacity-limit semantics,
  excluded real-execution semantics, and the configured per-node resource
  profile in backend-derived summaries. Event Kernel behavior, compute
  scheduling behavior, and service-time formulas are unchanged.
- Changed files/modules:
  - `src/leo_twin/schema/compute_resource_contract.py`
  - `src/leo_twin/schema/__init__.py`
  - `src/leo_twin/services/derived_summary.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `tests/unit/test_compute_resource_contract_v2.py`
  - `docs/compute_resource_contract_v2.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_compute_resource_contract_v2.py tests/unit/test_compute_resource_model.py tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 24 tests after aligning the CPU fallback wording in the
      contract.
  - `python -m pytest tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 2 tests.
  - Combined backend target:
    `python -m pytest tests/unit/test_compute_resource_contract_v2.py tests/unit/test_compute_resource_model.py tests/unit/test_backend_derived_summary.py tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 26 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 261 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
  - `python -m pytest tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 2 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning at about 502 kB after minification.
  - `git diff --check src/leo_twin/schema/compute_resource_contract.py src/leo_twin/schema/__init__.py src/leo_twin/services/derived_summary.py frontend/src/core/event_types/index.ts frontend/tests/fixtures/runtimeStatus.contract.json frontend/tests/runtimeContractFixture.test.ts tests/unit/test_compute_resource_contract_v2.py docs/compute_resource_contract_v2.md docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - Initial test wording expected the phrase `fallback to CPU_FP64`, while the
    contract text used `fall back to CPU_FP64`. The contract was normalized to
    the shorter product term so future docs/tests use one phrase.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    these files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - V2-030 stabilizes the resource contract but does not add placement policy or
    queue timeline semantics. Recommended next tasks: V2-031 service placement
    model and V2-032 task queue/execution timeline v2.

## 2026-07-05 - Network KPI Provenance Contract v2

- Branch: `feature/T168-kpi-provenance-contract-v2`
- Commit: pending in this commit
- Scope: implement V2-021 by adding `network_kpi_provenance_v2` to runtime
  status. The v2 provenance binds existing runtime `metrics_summary` values to
  `leo_twin.network_model_contract.v2`, including current KPI values, runtime
  summary keys, layer ownership, formula summaries, source-field values,
  dominant observed source, zero reasons, and explicit non-packet-level
  semantics. Existing `network_quality_provenance_v1` remains for compatibility.
  Event Kernel behavior, routing/link behavior, and KPI formulas are unchanged.
- Changed files/modules:
  - `src/leo_twin/services/network_kpi_provenance.py`
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `tests/unit/test_network_kpi_provenance_v2.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/network_kpi_provenance_v2.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_network_kpi_provenance_v2.py tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 3 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 261 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning at about 502 kB after minification.
  - `git diff --check src/leo_twin/services/network_kpi_provenance.py examples/integration_demo/control_plane.py frontend/src/core/event_types/index.ts frontend/tests/fixtures/runtimeStatus.contract.json frontend/tests/runtimeContractFixture.test.ts tests/unit/test_network_kpi_provenance_v2.py tests/integration/test_runtime_session_control.py docs/network_kpi_provenance_v2.md docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - No implementation blocker. The working tree still contains unrelated local
    runtime/config drift in `configs/generated_full_system_demo.json` and
    `configs/sees_control.yaml`; these files were intentionally left unstaged
    and unchanged by this task.
- Known remaining issues / follow-up:
  - The dashboard still primarily consumes v1 provenance helper labels. A
    follow-up dashboard task can render `network_kpi_provenance_v2.kpis`
    directly. V2-022 should improve the time-varying pressure inputs while
    preserving this contract.

## 2026-07-05 - Network Model Contract v2

- Branch: `feature/T167-network-model-contract-v2`
- Commit: pending in this commit
- Scope: implement V2-020 by adding a product-level network model contract v2.
  The contract defines canonical application, transport, network/routing,
  data-link, physical, and channel layer boundaries; user-facing KPI provenance
  semantics for throughput, latency, loss proxy, delay-variation proxy, route
  blocking, and congestion pressure; explicit excluded capabilities; and the
  configured protocol profile inside backend-derived summaries. This is a
  schema/documentation/summary contract change only. Event Kernel behavior,
  route computation, link updates, and metric formulas are unchanged.
- Changed files/modules:
  - `src/leo_twin/schema/network_model_contract.py`
  - `src/leo_twin/schema/__init__.py`
  - `src/leo_twin/services/derived_summary.py`
  - `src/leo_twin/services/scenario_builder.py`
  - `examples/integration_demo/scenario.py`
  - `frontend/src/core/event_types/index.ts`
  - `tests/unit/test_network_model_contract_v2.py`
  - `docs/network_model_contract_v2.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_network_model_contract_v2.py tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 13 tests.
  - `python -m pytest tests/unit/test_network_stack_runtime.py tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 10 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning at about 502 kB after minification.
  - `git diff --check examples/integration_demo/scenario.py frontend/src/core/event_types/index.ts src/leo_twin/schema/__init__.py src/leo_twin/schema/network_model_contract.py src/leo_twin/services/derived_summary.py src/leo_twin/services/scenario_builder.py tests/unit/test_network_model_contract_v2.py docs/network_model_contract_v2.md docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - No behavior blocker. The working tree still contains unrelated local
    runtime/config drift in `configs/generated_full_system_demo.json` and
    `configs/sees_control.yaml`; these files were intentionally left unstaged
    and unchanged by this task.
- Known remaining issues / follow-up:
  - V2-020 defines the network semantics. V2-021 should bind runtime KPI
    provenance directly to this contract so dashboard explanations and status
    fields reference the same backend source of truth.

## 2026-07-05 - Product Configuration Schema v2

- Branch: `feature/T166-product-config-schema-v2`
- Commit: pending in this commit
- Scope: implement V2-001 by adding a backend-owned, machine-readable user
  configuration schema v2 for the full `SEESConfig` surface. The schema now
  exposes deterministic field paths, defaults, current values, enum values,
  numeric constraints, key-control vs detailed-file edit surfaces, template
  references, accepted/rejected examples, and validation reporting. Existing
  `configuration_surface_summary.version` remains `v1` for compatibility while
  carrying `schema_version: v2` and `user_config_schema_v2`. Event Kernel and
  runtime model behavior are unchanged.
- Changed files/modules:
  - `src/leo_twin/services/configuration_schema.py`
  - `src/leo_twin/services/configuration_view.py`
  - `frontend/src/core/event_types/index.ts`
  - `tests/unit/test_user_configuration_schema_v2.py`
  - `docs/user_configuration_schema_v2.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_user_configuration_schema_v2.py tests/unit/test_configuration_view.py -q`
    - Result: passed, 13 tests.
  - `python -m pytest tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 2 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 25 files / 261 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning at about 502 kB after minification.
  - `git diff --check src/leo_twin/services/configuration_schema.py src/leo_twin/services/configuration_view.py frontend/src/core/event_types/index.ts tests/unit/test_user_configuration_schema_v2.py docs/user_configuration_schema_v2.md docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - Direct `pnpm --dir frontend test -- configPanel.test.ts` failed in the
    default PowerShell environment because `node` was not on `PATH`. The same
    command passed after using the bundled Codex Node/Pnpm paths.
  - The working tree still contains unrelated local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`.
    These files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - V2-001 defines and exposes the schema contract; the next task should add
    V2-003/V2-004 style import/export UX or proceed to V2-020 Network Model
    Contract v2 so KPI provenance can reference stable network semantics.

## 2026-07-05 - System v2 Upgrade Roadmap v1

- Branch: `feature/T165-system-v2-roadmap`
- Commit: pending in this commit
- Scope: establish the system v2 upgrade baseline around configuration-driven
  scenarios, backend-owned model semantics, KPI provenance, runtime scale
  policy, dashboard information architecture, 3D scene productization,
  verification, result export, and operator delivery. This is a planning and
  task sequencing change only; Event Kernel, runtime behavior, backend models,
  and frontend rendering are unchanged.
- Changed files/modules:
  - `docs/system_v2_upgrade_plan.md`
  - `docs/development_log.md`
- Validation:
  - `git diff --check docs/system_v2_upgrade_plan.md docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - The working tree already contained local runtime/config drift in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`.
    These files were intentionally left unstaged and unchanged by this task.
- Known remaining issues / follow-up:
  - This task defines the v2 execution order but does not implement the first
    behavior change. Recommended next commit: V2-001 Product Configuration
    Schema v2, followed by V2-020, V2-030, and V2-070.

## 2026-07-05 - Dashboard Terminal Completion Notice Gate v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: prevent the simulation-completed notice from reappearing after a page
  refresh when the backend runtime is already in a terminal `COMPLETED` state.
  The frontend now arms the completion banner only after the current page
  session has observed `RUNNING` or `PAUSED`; attaching to an already completed
  backend session still shows completed status in normal runtime fields, but no
  transient completion pop-up/banner. Event Kernel, runtime protocol, and
  backend simulation behavior are unchanged.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- appSurface.test.ts`
    - Result: passed, 25 files / 261 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning at about 502 kB after minification.
  - `git diff --check frontend/src/app/App.tsx frontend/tests/appSurface.test.ts docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - The previous completion banner was purely derived from backend terminal
    status, so a browser refresh looked like a fresh notification even though
    the completion had already happened before page load.
- Known remaining issues / follow-up:
  - Completion notice dismissal remains in-memory while a run is active. This
    task intentionally solves the terminal refresh case without adding
    persistent browser storage.

## 2026-07-05 - Dashboard Terminal Backpressure Suppression v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: prevent stale runtime backpressure notices from reappearing on page
  refresh after the simulation has completed or stopped. The backend may keep
  the last `backpressure_summary` in runtime status for diagnostics, but the
  frontend now treats pressure notices as active runtime warnings only and
  suppresses them for terminal `COMPLETED` / `STOPPED` states. Event Kernel,
  runtime protocol, and backend simulation behavior are unchanged.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- appSurface.test.ts`
    - Result: passed, 25 files / 260 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning at about 502 kB after minification.
  - `git diff --check frontend/src/app/App.tsx frontend/tests/appSurface.test.ts docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - The issue was caused by frontend state resetting on page refresh while the
    runtime status still contained the previous backpressure summary. The fix
    gates rendering by runtime lifecycle instead of relying only on in-memory
    dismissal state.
- Known remaining issues / follow-up:
  - Backpressure dismissal is still in-memory during active runs. If users need
    dismissal persistence across refresh while a run is still active, add a
    small `sessionStorage`-backed dismissal key in a separate frontend task.

## 2026-07-05 - Dashboard Layout Rebalance v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: fix the standalone dashboard completion-state notice that could expand
  into large dark blocks above the data panel, then rebalance the data panel
  layout by information importance. Completion notices are now compact,
  dismissible dashboard/control banners. The dashboard now keeps the core KPI
  summary first, uses a two-column primary trend area, moves user/satellite
  detail tables ahead of auxiliary model panels, and compresses auxiliary
  cross-domain cards into a denser grid. This is a frontend layout task only;
  Event Kernel behavior, runtime protocol, and backend simulation models are
  unchanged.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `frontend/tests/appCssLayout.test.js`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- appSurface.test.ts appCssLayout.test.js dataPanel.test.ts`
    - Result: passed, 25 files / 259 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing `DataPanel` chunk-size
      warning at about 502 kB after minification.
  - `git diff --check frontend/src/app/App.tsx frontend/src/app/App.css frontend/src/dashboard/data_panel/DataPanel.tsx frontend/tests/appSurface.test.ts frontend/tests/appCssLayout.test.js`
    - Result: passed.
- Problems encountered:
  - Browser inspection identified `.fidelity-notice completion dashboard` as the
    oversized dark block source before code changes. After changes, two
    follow-up in-app browser layout probes timed out while reading the local
    page, so final verification relied on targeted frontend tests, CSS source
    assertions, and production build.
- Known remaining issues / follow-up:
  - `DataPanel` remains slightly above Vite's 500 kB chunk warning threshold.
    A later task should split dashboard subpanels with dynamic imports.
  - This task rebalances layout only. It does not add new backend KPI semantics
    or packet-level network behavior.

## 2026-07-05 - Satellite Route KPI Detail v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: expose satellite-level route KPI fields in backend-owned satellite
  detail rows and render them in the standalone dashboard network column.
  Satellite detail rows now include route capacity, route demand, average route
  latency, route delay-variation proxy, and route loss proxy from existing
  `satellite_kpi_slices_v1` data. No new network model or packet-level
  simulation was introduced. Event Kernel behavior is unchanged.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `tests/unit/test_runtime_observability.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py -q`
    - Result: passed, 2 tests.
  - Bundled Node/Pnpm: `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 256 tests.
  - Bundled Node/Pnpm: `pnpm --dir frontend build`
    - Result: passed with the existing Vite warning that `DataPanel` is larger
      than 500 kB after minification.
  - `git diff --check -- src/leo_twin/services/runtime_observability.py tests/unit/test_runtime_observability.py frontend/src/core/event_types/index.ts frontend/src/dashboard/data_panel/DataPanel.tsx frontend/tests/dataPanel.test.ts`
    - Result: passed.
- Problems encountered:
  - None beyond the existing DataPanel chunk-size warning.
- Known remaining issues / follow-up:
  - Satellite route KPI fields are current-snapshot aggregates. A later task
    should add satellite route KPI history if users need per-satellite network
    trend curves instead of current detail rows.

## 2026-07-05 - User Service Latency Detail v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: expose structured communication-compute service latency components
  in backend-owned user detail rows and render them in the standalone
  dashboard service column. User details now include service task id,
  completion flag, total latency, input-network latency, compute queue delay,
  compute execution delay, output-network latency, and input/output route ids
  when `service_latency_history_v1` contains them. Event Kernel behavior is
  unchanged.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `tests/unit/test_runtime_observability.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py -q`
    - Result: passed, 2 tests.
  - Bundled Node/Pnpm: `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 256 tests.
  - Bundled Node/Pnpm: `pnpm --dir frontend build`
    - Result: passed with the existing Vite warning that `DataPanel` is larger
      than 500 kB after minification.
  - `git diff --check -- src/leo_twin/services/runtime_observability.py tests/unit/test_runtime_observability.py frontend/src/core/event_types/index.ts frontend/src/dashboard/data_panel/DataPanel.tsx frontend/tests/dataPanel.test.ts`
    - Result: passed.
- Problems encountered:
  - Frontend build initially failed because the new helper referenced
    `RuntimeUserRequestItemV1` without importing the type. The import was added
    and the build passed.
- Known remaining issues / follow-up:
  - Service latency details are still rendered in one compact table cell. A
    later dashboard task should add expandable per-user service traces or a
    side panel for full component timelines.

## 2026-07-05 - Runtime Detail Semantics v2

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: enrich backend-owned user and satellite runtime detail rows for the
  standalone dashboard. User rows now include platform labels, request-state
  labels, network queue reasons, selected next hop, route hop count, and a
  route path label. Satellite rows now include resource role labels, primary
  route/flow ids, queued route counts, and route-mix labels. The frontend
  detail tables consume these backend fields before falling back to local
  derivation. Event Kernel behavior is unchanged.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `tests/unit/test_runtime_observability.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_live_runtime_streaming.py::test_runtime_detail_pages_return_deterministic_windows -q`
    - Result: passed, 3 tests.
  - Bundled Node/Pnpm: `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 256 tests.
  - Bundled Node/Pnpm: `pnpm --dir frontend build`
    - Result: passed with the existing Vite warning that `DataPanel` is larger
      than 500 kB after minification.
  - `git diff --check -- src/leo_twin/services/runtime_observability.py tests/unit/test_runtime_observability.py frontend/src/core/event_types/index.ts frontend/src/dashboard/data_panel/DataPanel.tsx frontend/tests/dataPanel.test.ts`
    - Result: passed.
- Problems encountered:
  - The frontend test file contains historical mojibake text in several
    Chinese strings. The implementation avoided broad text rewrites and only
    changed the assertions needed for the new backend-provided labels.
- Known remaining issues / follow-up:
  - `service_latency_history_v1` is still consumed as compact service-state
    text in user rows. A follow-up should expose structured per-service
    latency components directly in each user detail row.

## 2026-07-05 - Network Stress KPI Movement v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: retune the 120-satellite network stress observability template so it
  produces deterministic, time-varying flow-level KPI samples instead of an
  early all-routes-blocked profile. The preset now uses an 80 Mbps per-flow
  demand and a 30s mixed-service task interval, which keeps the live run
  responsive while preserving visible partial route blocking, non-zero
  throughput, latency, loss proxy, and delay-variation proxy. Event Kernel
  behavior is unchanged.
- Changed files/modules:
  - `configs/templates/sees_user_network_stress_120.example.yaml`
  - `tests/unit/test_configuration_view.py`
  - `tests/integration/test_config_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_configuration_view.py tests/integration/test_config_control.py::test_control_plane_loads_user_config_template_before_initialization tests/integration/test_config_control.py::test_network_stress_template_status_polling_stays_stable tests/integration/test_config_control.py::test_network_stress_template_exposes_nonzero_time_varying_network_kpis -q`
    - Result: passed, 10 tests.
  - `git diff --check -- configs/templates/sees_user_network_stress_120.example.yaml tests/unit/test_configuration_view.py tests/integration/test_config_control.py docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - A local probe showed the previous 320 Mbps demand profile kept the stress
    scenario in complete effective route loss for early dashboard windows. The
    fix stays in scenario configuration and regression coverage rather than
    changing route ordering, Event Kernel behavior, or adding packet-level
    simulation.
- Known remaining issues / follow-up:
  - The network KPI model remains a flow-level proxy. A later network-fidelity
    task should add clearer per-user request state, queue attribution, and
    route/load explanations for the standalone dashboard.

## 2026-07-05 - Runtime Metrics Status Polling Stability v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: make runtime status polling stable while the server-side advance loop
  is running. `MetricsCollector` now uses a lightweight re-entrant lock around
  public write/read entry points so status summaries, KPI series, satellite
  KPI slices, histories, and output formatting cannot iterate internal
  dictionaries while the live loop is mutating them. The 120-satellite network
  stress template was also reduced from 900 to 240 users and from 900s to
  600s so it remains an interactive pressure scenario rather than a heavy
  startup load. Event Kernel behavior is unchanged.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `configs/templates/sees_user_network_stress_120.example.yaml`
  - `tests/unit/test_configuration_view.py`
  - `tests/integration/test_config_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py::test_metrics_collector_publishes_satellite_kpi_slices tests/unit/test_metrics_module.py::test_metrics_outputs_are_deterministic_and_have_expected_format tests/unit/test_configuration_view.py tests/integration/test_config_control.py::test_control_plane_loads_user_config_template_before_initialization tests/integration/test_config_control.py::test_network_stress_template_status_polling_stays_stable -q`
    - Result: passed, 11 tests.
  - `git diff --check -- src/leo_twin/services/metrics/collector.py configs/templates/sees_user_network_stress_120.example.yaml tests/unit/test_configuration_view.py tests/integration/test_config_control.py docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - A live probe of the network stress template reproduced
    `RuntimeError: dictionary changed size during iteration` from
    `MetricsCollector.satellite_kpi_slices()` while runtime status polling
    overlapped with backend advancement. The fix was scoped to the metrics
    observation layer.
- Known remaining issues / follow-up:
  - The stress template is now responsive, but early samples can still show
    complete route blocking depending on current flow-level routing pressure.
    The next task should tune the demand/routing profile or improve route
    availability semantics so dashboard throughput, latency, loss proxy, and
    delay-variation curves all show useful movement without packet-level
    simulation.

## 2026-07-05 - User Config Template Loader v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: add a backend-approved template loading workflow for the integration
  demo control plane and frontend control panel. The backend exposes a
  deterministic `LOAD_TEMPLATE` runtime control action that accepts a
  whitelisted `template_id`, loads the corresponding detailed YAML template,
  writes the runtime config/generated scenario files, rebuilds a clean
  uninitialized session, and returns the usual config/generated_config ACK.
  The frontend renders backend template profiles with a "加载模板" action while
  keeping full template loading locked after initialization. Event Kernel
  behavior is unchanged.
- Changed files/modules:
  - `src/leo_twin/services/configuration_view.py`
  - `src/leo_twin/runtime/control_protocol.py`
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/config_panel/controlClient.ts`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/app/App.css`
  - `tests/unit/test_configuration_view.py`
  - `tests/integration/test_config_control.py`
  - `frontend/tests/configPanel.test.ts`
  - `frontend/tests/controlClient.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_configuration_view.py tests/integration/test_config_control.py::test_control_plane_loads_user_config_template_before_initialization tests/integration/test_config_control.py::test_control_plane_rejects_template_load_after_initialization -q`
    - Result: passed, 9 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- configPanel.test.ts controlClient.test.ts`
    - Result: passed, 25 files / 256 tests.
  - `python -m pytest tests/unit/test_configuration_view.py tests/integration/test_config_control.py -k "template or frontend_control_messages_are_processed or initialize_writes_config_and_start_gates_streams or system_remains_deterministic_under_config_changes" -q`
    - Result: passed, 11 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed with the existing Vite warning that `DataPanel` is larger
      than 500 kB after minification.
  - `git diff --check -- src/leo_twin/services/configuration_view.py src/leo_twin/runtime/control_protocol.py examples/integration_demo/control_plane.py tests/unit/test_configuration_view.py tests/integration/test_config_control.py frontend/src/config_panel/controlClient.ts frontend/src/config_panel/ConfigPanel.tsx frontend/src/app/App.css frontend/tests/configPanel.test.ts frontend/tests/controlClient.test.ts docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - None so far.
- Known remaining issues / follow-up:
  - Template loading is intentionally available only before initialization.
    Users must reset before replacing the full detailed configuration.
  - The workflow still uses deterministic flow-level models; it does not add
    packet-level simulation, RF propagation, or external simulators.

## 2026-07-05 - Network Stress User Config Template v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: add a deterministic 120-satellite user configuration template for
  dashboard network-stress observability. The template increases flow-level
  demand, configured transport loss, rain attenuation inputs, and routing
  pressure so throughput, latency, loss proxy, jitter proxy, route pressure,
  and compute load curves are easier to validate. It remains configuration
  only: no Event Kernel changes, no packet-level simulation, no RF propagation
  model, and no STK/EXATA/AFSIM/DDS integration.
- Changed files/modules:
  - `configs/templates/sees_user_network_stress_120.example.yaml`
  - `src/leo_twin/services/configuration_view.py`
  - `tests/unit/test_configuration_view.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_configuration_view.py -q`
    - Result: passed, 5 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 25 files / 256 tests.
  - `git diff --check -- configs/templates/sees_user_network_stress_120.example.yaml src/leo_twin/services/configuration_view.py tests/unit/test_configuration_view.py docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - The first backend template test run failed because the new template
    described loss/jitter proxy fields but did not include the exact
    user-facing phrase `flow-level proxy`; the template purpose text was
    clarified and the test was rerun.
- Known remaining issues / follow-up:
  - The frontend currently lists backend template profiles but does not yet
    provide a one-click "load this template" workflow. Loading templates into
    the active control config should be a separate endpoint/UI task.

## 2026-07-05 - Runtime Heartbeat Diagnostics v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: expose the backend advance-loop heartbeat that already exists in
  `stream_diagnostics_v1.tick_count` on the frontend connection diagnostics.
  The control channel now shows cumulative server-side advance ticks and the
  hover text clarifies that event count is a discrete simulation event counter,
  while tick count is the live backend progression heartbeat. This addresses
  the user-facing confusion where event count can stay flat during quiet
  periods even though the live runtime loop is still active.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- appSurface.test.ts`
    - Result: passed, 25 files / 256 tests.
  - `git diff --check -- frontend/src/app/App.tsx frontend/tests/appSurface.test.ts docs/development_log.md`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed with the existing Vite warning that `DataPanel` is larger
      than 500 kB after minification.
- Problems encountered:
  - None so far.
- Known remaining issues / follow-up:
  - This does not create synthetic simulation events. KPI and event dynamics
    still depend on configured flow-level demand, orbit/network state changes,
    and compute workload events.

## 2026-07-05 - Large-Scale User Config Template v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: add a user-facing 1200-satellite detailed YAML template that keeps
  the frontend focused on key controls while advanced users can edit the full
  backend contract. The template uses BATCH orbit updates, bounded ISL
  candidates, workload smoothing, mixed flow-level traffic, and per-satellite
  compute resource vectors.
- Changed files/modules:
  - `configs/templates/sees_user_large_scale_1200.example.yaml`
  - `src/leo_twin/services/configuration_view.py`
  - `tests/unit/test_configuration_view.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_configuration_view.py -q`
    - Result: passed, 4 tests.
  - `python -m pytest tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 2 tests.
  - `git diff --check -- configs/templates/sees_user_large_scale_1200.example.yaml src/leo_twin/services/configuration_view.py tests/unit/test_configuration_view.py`
    - Result: passed.
- Problems encountered:
  - The first template text assertion expected the forbidden external-simulator
    list on one line; the template comment was adjusted so the user-facing
    warning is explicit and testable.
- Known remaining issues / follow-up:
  - The frontend lists backend template profiles, but it still does not load a
    selected template into the running config. That should be a separate
    backend endpoint plus UI workflow.

## 2026-07-05 - Continuous Access Link Refresh v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: refresh continuing satellite-ground access link latency/capacity when
  orbit updates move an already-connected satellite-user pair, emitting a
  deterministic `LINK_UPDATE` without a duplicate `ACCESS_START`. This gives
  route latency and jitter proxies real time-varying input while preserving the
  existing event-driven network model.
- Changed files/modules:
  - `src/leo_twin/models/network/position_engine.py`
  - `tests/unit/test_position_driven_network_engine.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_position_driven_network_engine.py -q`
    - Result: passed, 31 tests.
  - `python -m pytest tests/unit/test_metrics_module.py::test_metrics_collector_reports_dynamic_network_quality_proxy tests/unit/test_metrics_module.py::test_metrics_collector_publishes_backend_kpi_time_series tests/unit/test_metrics_module.py::test_metrics_collector_kpi_time_series_refreshes_current_tail_sample -q`
    - Result: passed, 3 tests.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py::test_http_cursor_batches_return_incremental_events tests/integration/test_orbit_batch_scale.py -q`
    - Result: passed, 8 tests.
  - `python -m pytest tests/scale/test_position_network_scale_smoke.py -q`
    - Result: passed, 1 test.
  - `git diff --check -- src/leo_twin/models/network/position_engine.py tests/unit/test_position_driven_network_engine.py`
    - Result: passed.
- Problems encountered:
  - Two initially selected metrics test node IDs did not exist; validation was
    rerun with the actual dynamic network quality and KPI time-series tests.
- Known remaining issues / follow-up:
  - This is still a flow-level proxy, not packet-level network simulation.
    Large-scale scenarios should continue using batched orbit updates and
    bounded ISL candidates.

## 2026-07-05 - Dashboard Recent KPI Empty-Window Fallback v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: prevent empty recent-flow KPI windows from overriding backend
  effective network KPIs in the standalone dashboard charts. Recent
  throughput, latency, loss proxy, and jitter proxy now take precedence only
  when the backend reports `network_recent_flow_count > 0`.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `pnpm --dir frontend test -- dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 256 tests.
  - `git diff --check -- frontend/src/dashboard/data_panel/DataPanel.tsx frontend/tests/dataPanel.test.ts`
    - Result: passed.
- Problems encountered:
  - A read-only subagent review confirmed the symptom was not only refresh
    cadence; the frontend was also allowing zero-sample recent-window values
    to flatten otherwise valid backend effective KPIs.
- Known remaining issues / follow-up:
  - Backend network links still need a bounded continuous refresh path so
    route latency and jitter proxies can change during long stretches without
    access start/end events.

## 2026-07-05 - Dashboard Detail Window Visibility v2

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: make the standalone dashboard request a full 5,000-row backend
  detail window for users and satellites, and show the backend cursor window
  range inside each detail pager so 120/1200-node scenarios are visibly
  complete when they fit in the current backend page.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `pnpm --dir frontend test -- dataPanel.test.ts api.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 255 tests.
  - `git diff --check -- frontend/src/app/App.tsx frontend/src/dashboard/data_panel/DataPanel.tsx frontend/src/app/App.css frontend/tests/dataPanel.test.ts`
    - Result: passed.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed; Vite reported the existing large `DataPanel` chunk
      warning.
- Problems encountered:
  - The shell PATH `pnpm` invocation could not find `node`; validation was
    rerun with the Codex bundled Node and pnpm paths prepended.
- Known remaining issues / follow-up:
  - The dashboard now covers current 120/1200-node detail windows in one
    backend page. A later task should add explicit remote cursor next-window
    controls for scenarios above 5,000 detail rows.

## 2026-07-05 - Runtime Detail Pagination API v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: add deterministic server-side detail page APIs for user request and
  satellite service rows, then let the standalone dashboard consume those
  pages as an optional enhancement over `/runtime/status`.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/app/api.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/unit/test_runtime_observability.py`
  - `tests/integration/test_live_runtime_streaming.py`
  - `frontend/tests/api.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_live_runtime_streaming.py -q`
    - Result: passed, 14 tests.
  - Bundled Node:
    `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 252 tests.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The first integration test expectation assumed `user-000` IDs, but the
    real deterministic demo order starts with `ground-station-00` followed by
    zero-padded `user-0000`; the test was corrected to match the actual product
    contract.
- Known remaining issues:
  - The dashboard currently refreshes the first user/satellite detail pages and
    still uses local pagination plus snapshot fallback. True remote page
    controls for arbitrary cursors remain a follow-up.
- Recommended follow-up:
  - Wire the table pager controls directly to `/runtime/details/users` and
    `/runtime/details/satellites` cursors so large deployments can browse
    beyond the first backend page without relying on snapshot fallback.

## 2026-07-05 - Runtime Detail Scope Counts v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: separate full-set observability counts from bounded dashboard item
  windows for user request and satellite service summaries.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/unit/test_runtime_observability.py`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py -q`
    - Result: passed, 2 tests.
  - `python -m pytest tests/integration/test_runtime_session_control.py -q`
    - Result: passed, 17 tests.
  - Bundled Node:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 249 tests.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - `active_user_count`, `compute_service_user_count`, and
    `waiting_user_count` were derived from the returned item window. In large
    cases this made bounded windows look like full-system totals.
- Known remaining issues:
  - The dashboard still receives bounded item windows through `/runtime/status`;
    a server-side paginated details endpoint is still needed for true full-table
    browsing.
- Recommended follow-up:
  - Add deterministic `/runtime/details/users` and
    `/runtime/details/satellites` cursor endpoints, then switch the dashboard
    tables to server-side pagination.

## 2026-07-05 - Runtime Completion State Consistency v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: make completed runtime sessions authoritative across legacy demo
  stream paths and frontend status labels, even if the older controller still
  reports `RUNNING`.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/app/App.tsx`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `frontend/tests/configPanel.test.ts`
  - `tests/integration/test_live_runtime_streaming.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_live_runtime_streaming.py -q`
    - Result: passed, 11 tests.
  - Bundled Node:
    `pnpm --dir frontend test -- appSurface.test.ts configPanel.test.ts dataPanel.test.ts`
    - Result: passed, 25 files / 249 tests.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - `SimulationSession` correctly reaches `COMPLETED`, but legacy demo stream
    helpers were gated by `RuntimeController.snapshot().status`, which can
    remain `RUNNING` after the session has completed.
  - Some frontend labels checked `status === RUNNING` before checking
    `lifecycle_state === COMPLETED`, so mixed status payloads could still look
    active.
- Known remaining issues:
  - The older `RuntimeController` enum still has no native `COMPLETED` state;
    the session lifecycle remains the product runtime source of truth.
- Recommended follow-up:
  - Add a small backend status helper that exposes one canonical effective
    status field for all HTTP, WebSocket, and dashboard consumers.

## 2026-07-05 - Visual Layer Budget Explanation v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: make the 3D visual layer buttons explain their render budget and
  effect inline instead of relying on hover-only titles.
- Changed files/modules:
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/appCssLayout.test.js`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `pnpm --dir frontend test -- appCssLayout.test.js visualLayerLimits.test.ts`
    - Result: passed, 25 files / 247 tests.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The layer controls already had deterministic summaries, but the detailed
    effect text was only exposed through `title`, making the buttons feel
    ineffective unless users hovered each summary chip.
- Known remaining issues:
  - This remains a render-budget explanation; it does not add per-layer
    animated before/after previews.
- Recommended follow-up:
  - Add a selected-layer focus mode so toggling links, beams, or tracks can
    briefly highlight the affected entities in the 3D view.

## 2026-07-05 - Runtime Parameter Lock v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: prevent UI/runtime semantic drift by locking execution parameters
  after a runtime session has been initialized, even before START is pressed.
- Changed files/modules:
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 25 files / 247 tests.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The UI already disabled speed/mode while `RUNNING`, but allowed users to
    alter runtime mode, speed, duration, and seed after initialization while
    the backend session still retained the initialized values.
- Known remaining issues:
  - Changing initialized execution parameters now requires RESET and
    re-initialization; a future preview/apply flow could make that clearer.
- Recommended follow-up:
  - Add backend status fields that explicitly report which configuration
    version is bound to the current session.

## 2026-07-05 - Dashboard Usability Firebreak v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: fix several high-friction frontend observability issues without
  changing runtime or Event Kernel behavior.
- Changed files/modules:
  - `frontend/src/3d/cesium/renderLimits.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/visualLayerLimits.test.ts`
  - `frontend/tests/appSurface.test.ts`
  - `frontend/tests/appCssLayout.test.js`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `pnpm --dir frontend test -- visualLayerLimits.test.ts appSurface.test.ts appCssLayout.test.js satelliteVisuals.test.ts`
    - Result: passed, 25 files / 246 tests.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The 3D view kept satellite icon rendering capped at 96, so a 120-satellite
    scenario looked incomplete even though all satellites remained selectable.
  - The backpressure dismissal key included volatile per-tick samples, causing
    the yellow pressure notice to reappear after every backend refresh.
  - The standalone dashboard relied on an internal scroll container under a
    fixed-height shell, which made full-page scrolling unreliable.
- Known remaining issues:
  - Large scenarios still intentionally render a bounded subset of satellite
    icons to preserve 1200-node responsiveness; the backend remains the source
    of truth for full counts.
- Recommended follow-up:
  - Add a compact visual budget indicator near the layer toggles so users can
    distinguish full small-scale rendering from large-scale bounded rendering.

## 2026-07-05 - Configuration File-Only Scope v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: expose backend-owned `file_only_sections` in the configuration
  surface summary so the control panel can show which detailed YAML sections
  remain file-only while the UI continues to expose key operational controls.
- Changed files/modules:
  - `src/leo_twin/services/configuration_view.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `tests/unit/test_configuration_view.py`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_configuration_view.py -q`
    - Result: passed, 3 tests.
  - Bundled Node:
    `pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 25 files / 244 tests.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The existing summary listed all `file_only_fields` but did not group them
    for users. The new `file_only_sections` is exclusive by most-specific
    config section, so counts do not double-count nested paths.
- Known remaining issues:
  - This is a transparency feature only; it does not yet load a selected YAML
    template into the form.
- Recommended follow-up:
  - Add a backend-controlled template apply/preview endpoint so advanced users
    can choose a detailed template without exposing every field in the main UI.

## 2026-07-05 - Full-System Demo Baseline Refresh v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: refresh stale deterministic integration-demo count baselines so the
  default full-system demo test matches the current committed deterministic
  runtime behavior.
- Changed files/modules:
  - `tests/integration/test_full_system_demo.py`
  - `docs/development_log.md`
- Validation:
  - Current default demo measurement:
    - `processed_events=23615`
    - `snapshot_event_count=23615`
    - `space_links=61`
    - `routes_total=100`
    - `routes_available=25`
    - `finished_tasks=65`
    - `deadline_missed_tasks=39`
  - `python -m pytest tests/integration/test_full_system_demo.py -q`
    - Result: passed, 6 tests.
  - `python -m pytest tests/integration/test_runtime_session_control.py -q`
    - Result: passed, 17 tests.
  - Bundled Node:
    `pnpm --dir frontend test -- appSurface.test.ts dataPanel.test.ts`
    - Result: passed, 25 files / 244 tests.
- Problems encountered:
  - The old expected counts (`52` space-space links and `23049` processed
    events) were already failing in a clean worktree at pre-task HEAD. The fix
    keeps exact deterministic assertions rather than weakening them.
- Known remaining issues:
  - Full-system demo counts remain sensitive to intentional topology or
    lifecycle changes and should be refreshed only with measured deterministic
    evidence.
- Recommended follow-up:
  - Add a compact demo-baseline report helper that prints all exact counts used
    by `test_full_system_demo.py` before future baseline refreshes.

## 2026-07-05 - User Request History Scope v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: make user business history sampling explicit by adding backend
  `source`, `history_scope`, `sample_policy`, `summary_item_count`,
  `hidden_user_count`, and `history_user_count` fields to
  `user_request_history_v1`, then displaying the sampling scope and hidden-user
  count in the standalone dashboard history summary.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/integration/test_runtime_session_control.py`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py -q`
    - Result: passed, 17 tests.
  - Bundled Node:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 244 tests.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - User request history is sampled when runtime status is built; it is not a
    complete append-only business log. The new fields make that limitation
    explicit instead of hiding it behind the chart.
- Known remaining issues:
  - Hidden users that are not present in backend-visible summary rows still do
    not get per-user history series.
- Recommended follow-up:
  - Add backend-owned server-side user history pagination or selected-user
    history tracking so large scenarios can inspect arbitrary users without
    pushing every user's history to the frontend.

## 2026-07-05 - Runtime Mode Mapping Completion v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: preserve initialized runtime `mode` and `speed_factor` when the
  integration demo control plane rebuilds `DemoConfig`, so the live
  `SimulationSession` no longer runs as `REAL_TIME/1x` while the UI reports
  `ACCELERATED/Nx`. The generated scenario runtime block now also reflects the
  active runtime mode and speed factor.
- Changed files/modules:
  - `examples/integration_demo/config.py`
  - `examples/integration_demo/scenario.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py -q`
    - Result: passed, 17 tests.
  - `python -m pytest tests/unit/test_configuration_view.py -q`
    - Result: passed, 3 tests.
  - Bundled Node:
    `pnpm --dir frontend test -- configPanel.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 244 tests.
  - Manual focused script:
    - Initialized demo runtime with `ACCELERATED`, `speed_factor=20`, and
      `duration=4`.
    - Verified the installed `SimulationSession.runtime_config` was
      `ACCELERATED/20.0`.
    - Verified one deterministic control step reached `COMPLETED` at
      `current_sim_time=4.0`.
- Problems encountered:
  - `python -m pytest tests/integration/test_full_system_demo.py -q` failed on
    two existing deterministic baseline counts (`52` expected space-space links
    but `61` observed, and `23049` expected processed events but `23615`
    observed). A temporary clean worktree at pre-task HEAD `b3e397b` reproduced
    the same failures, so this was isolated as an existing baseline issue and
    not changed in this task.
- Known remaining issues:
  - The integration demo still has stale full-system demo count expectations
    that should be audited separately from runtime control semantics.
- Recommended follow-up:
  - Add a dedicated acceptance test for UI-visible completion state using a
    short accelerated scenario and stream polling, then refresh or explain the
    stale `test_full_system_demo.py` count baselines in a separate commit.

## 2026-07-05 - Dashboard Detail Scope Notice v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: make standalone dashboard detail coverage explicit by rendering
  backend-owned user/satellite summary coverage, hidden-row fallback status,
  satellite KPI slice limits, and single-satellite history limits inline above
  the user/satellite detail tables.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `frontend/tests/appCssLayout.test.js`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `pnpm --dir frontend test -- dataPanel.test.ts appCssLayout.test.js`
    - Result: passed, 25 files / 244 tests.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The existing dashboard already had backend detail summaries and scrollable
    tables, but it did not visibly distinguish full detail rows from bounded
    KPI slice/history windows. The new notice is inline and responsive rather
    than a floating overlay.
- Known remaining issues:
  - Satellite KPI history is still a representative bounded window; per-satellite
    historical series for every satellite remains a later backend scale task.
- Recommended follow-up:
  - Add user-selectable detail export or server-side pagination if users need
    to inspect thousands of users/satellites beyond the current in-memory table.

## 2026-07-05 - Recent KPI Zero-Reason Transparency v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: expose backend-owned zero-reason labels for recent-window network KPI
  samples and display those explanations in the standalone dashboard so users
  can tell whether 0 loss/jitter means no recent completed-flow sample, no
  triggered loss proxy, or a positive proxy value.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/unit/test_metrics_module.py`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py -q`
    - Result: passed, 21 tests.
  - Bundled Node:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 242 tests.
  - `python -m pytest tests/integration/test_runtime_session_control.py -q`
    - Result: passed, 16 tests.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Existing PowerShell output can show Chinese source as mojibake when read
    without `-Encoding utf8`; edits were made against UTF-8 reads and kept
    narrowly scoped.
- Known remaining issues:
  - Metrics remain deterministic flow-level proxies, not packet-level loss or
    jitter. The new fields explain the proxy state; they do not add a more
    detailed network model.
- Recommended follow-up:
  - Add dashboard copy for per-user and per-satellite observability limits so
    users can distinguish full detail rows from capped KPI history slices.

## 2026-07-05 - Frontend Template Profile Binding v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: bind backend-provided `configuration_surface_summary.template_profiles`
  into the frontend control panel so users can see the detailed YAML templates
  while the UI continues to expose only key operational controls.
- Changed files/modules:
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 25 files / 241 tests.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The first render test used a too-small `GeneratedScenarioConfig` fixture;
    `ConfigPanel` also renders the existing generated scenario summary, so the
    fixture was expanded with the required baseline generated-config fields.
- Known remaining issues:
  - The UI currently displays template paths and purposes but does not yet
    load a selected template into the form.
- Recommended follow-up:
  - Add an explicit "apply template" workflow that loads a template through the
    backend config-control path and then refreshes the backend-derived summary.

## 2026-07-05 - User Dynamic Observability Template v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: add a detailed 120-satellite user configuration template for dynamic
  dashboard observability and expose backend-owned template profiles through
  the configuration surface summary.
- Changed files/modules:
  - `configs/templates/sees_user_dynamic_observability.example.yaml`
  - `src/leo_twin/services/configuration_view.py`
  - `tests/unit/test_configuration_view.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_configuration_view.py -q`
    - Result: passed, 3 tests.
- Problems encountered:
  - `python -m pytest tests/integration/test_config_control.py::test_config_loads_correctly -q`
    failed because the local runtime config `configs/sees_control.yaml` remains
    intentionally dirty and has `compute_nodes=72`, while that test expects the
    checked-in baseline value `10`. Per project rules, the local runtime config
    was not reset or staged.
- Known remaining issues:
  - The frontend does not yet render a template-profile picker; the backend now
    exposes deterministic `template_profiles` for a later UI binding task.
  - Dynamic observability metrics remain deterministic flow-level proxies.
- Recommended follow-up:
  - Add a frontend affordance that links key UI controls to the detailed
    template profiles without exposing every YAML field in the control panel.

## 2026-07-05 - Dashboard Detail Scroll and Fallback Completion v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: make the standalone `/dashboard` page use a stable page-level scroll
  container, increase the visible detail-table area, and ensure backend-limited
  user/satellite summaries are completed with deterministic snapshot fallback
  rows before pagination.
- Changed files/modules:
  - `frontend/src/app/App.css`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/appCssLayout.test.js`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `pnpm --dir frontend test -- appCssLayout.test.js appSurface.test.ts dataPanel.test.ts`
    - Result: passed, 25 files / 238 tests.
  - Bundled Node:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Importing `App.css?raw` from a TypeScript test was transformed to an empty
    string under the current Vitest setup, while using `node:fs` from a
    TypeScript test failed the frontend `tsc` build because Node types are not
    part of the app tsconfig. The CSS contract test was moved to a JavaScript
    Vitest file so build-time TypeScript remains browser-only.
  - A limited satellite-service summary fixture omitted `next_hop_ids`; the
    frontend now defensively treats missing service-user and next-hop arrays as
    empty arrays.
- Known remaining issues:
  - Detail rows still depend on backend summary limits plus snapshot fallback;
    this is not a server-side full-detail API yet.
  - The visual design remains the existing dense dashboard layout, not a full
    dashboard redesign.
- Recommended follow-up:
  - Add backend cursor/pagination endpoints for full user-node and
    satellite-node detail tables when scenarios exceed frontend memory-friendly
    limits.

## 2026-07-05 - Dynamic Network Stress Acceptance v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending in this commit
- Scope: add a user-facing acceptance scenario that drives deterministic
  time-varying network KPI pressure from configuration, and fix the
  service-mix compute path where `task_id` can differ from the input
  `flow_id`.
- Changed files/modules:
  - `configs/acceptance/network_stress_dynamic_72sat.yaml`
  - `src/leo_twin/models/compute/network_aware.py`
  - `tests/unit/test_network_aware_compute.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `tests/integration/test_product_acceptance_scenarios.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_network_aware_compute.py -q`
    - Result: passed, 10 tests.
  - `python -m pytest tests/unit/test_network_aware_compute.py tests/unit/test_integration_demo_scenario.py::test_demo_service_mix_weights_drive_demand_generation tests/integration/test_product_acceptance_scenarios.py::test_network_stress_acceptance_scenario_drives_dynamic_kpis -q`
    - Result: passed, 12 tests.
  - Manual runtime probe using
    `configs/acceptance/network_stress_dynamic_72sat.yaml` with deterministic
    `advance_control_step()`:
    - Result: initialization and start passed; KPI samples showed non-zero
      requested route demand, throughput, latency, loss proxy, delay
      variation, and compute FP32 resource usage.
- Problems encountered:
  - The weighted service-mix scenario generated compute tasks whose
    `task_id` is intentionally different from the input flow ID. A route
    refresh during input transfer could re-key the internal transfer table by
    `flow_id`, causing a later scheduler lookup by `task_id` to fail. The
    compute engine now canonicalizes transferring tasks by `task_id` while
    retaining `flow_id` lookup compatibility.
  - Fast repeated calls to the live `SessionAdvanceLoop.tick()` in
    `REAL_TIME` mode do not advance wall-clock paced simulation time. The
    acceptance test uses the existing deterministic `SimulationSession`
    control-step path instead.
- Known remaining issues:
  - Network loss, jitter, and latency remain deterministic flow-level proxies,
    not packet-level measurements.
  - The new acceptance scenario is a stress/demo profile and is not intended
    to represent exact Starlink or EXATA fidelity.
- Recommended follow-up:
  - Add dashboard scrollable per-user and per-satellite detail tables backed by
    the existing runtime observability summaries.

## 2026-07-05 - Frontend Per-Resource Usage Binding v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: pass backend per-resource compute used/available fields through the
  frontend decoder and snapshot engine, then surface them in the selected
  satellite resource inset and dashboard compute resource summary.
- Changed files/modules:
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/core/decoder/index.ts`
  - `frontend/src/state/snapshot_engine/index.ts`
  - `frontend/src/3d/cesium/satelliteFollow.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/eventDecoder.test.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts satelliteVisuals.test.ts eventDecoder.test.ts renderPerformance.test.ts`
    - Result: passed, 22 files / 106 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - Clean temporary worktree with this task patch applied:
    `python -m pytest tests/integration/test_config_control.py::test_config_loads_correctly tests/unit/test_scenario_builder.py::test_default_generated_scenario_config_file_loads -q`
    - Result: passed, 2 tests.
- Problems encountered:
  - Existing satellite visual tests used exact object assertions. They were
    updated to include the new usage labels while preserving existing capacity
    labels.
- Known remaining issues:
  - The dashboard still presents a compact textual multi-resource summary
    alongside the FP32 pie chart; a full multi-resource chart remains future
    work.
  - Per-resource values are deterministic estimator outputs, not real execution
    telemetry.
- Recommended follow-up:
  - Replace the FP32-only dashboard pie with a multi-resource panel once visual
    design and acceptance tests are defined.

## 2026-07-05 - Compute Node Per-Resource Usage State v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: extend backend compute-node state with deterministic per-resource
  used/available estimates for CPU FP32/FP64, GPU FP32/FP16, NPU INT8, memory,
  and storage while preserving legacy scalar `capacity` / `available_capacity`
  behavior.
- Changed files/modules:
  - `src/leo_twin/schema/domain.py`
  - `src/leo_twin/models/compute/resources.py`
  - `src/leo_twin/models/compute/__init__.py`
  - `src/leo_twin/models/compute/engine.py`
  - `src/leo_twin/models/compute/network_aware.py`
  - `src/leo_twin/models/network/position_engine.py`
  - `src/leo_twin/services/metrics/collector.py`
  - `examples/integration_demo/replay.py`
  - `docs/product_contracts.md`
  - `tests/unit/test_compute_resource_model.py`
  - `tests/unit/test_compute_module.py`
  - `tests/unit/test_metrics_module.py`
  - `tests/unit/test_product_contracts.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_compute_resource_model.py tests/unit/test_compute_module.py tests/unit/test_network_aware_compute.py tests/unit/test_metrics_module.py tests/unit/test_product_contracts.py -q`
    - Result: passed, 40 tests.
  - `python -m pytest tests/integration/test_compute_service_lifecycle.py tests/integration/test_full_domain_pipeline_v1.py tests/integration/test_full_system_demo.py::test_replay_test tests/integration/test_config_control.py::test_frontend_control_messages_are_processed tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 6 tests.
  - `git diff --check`
    - Result: passed with only CRLF warnings for excluded local runtime config
      files.
- Problems encountered:
  - Existing compute-module tests compared full `ComputeNodeState` dataclasses.
    They were updated to assert legacy timing/state fields plus the new
    resource usage fields explicitly.
  - Metrics naming now keeps legacy scalar FP32 fields unchanged and uses
    `compute_resource_available_cpu_gflops_fp32` /
    `compute_resource_used_cpu_gflops_fp32` for vector-estimated CPU FP32.
- Known remaining issues:
  - Frontend decoder and dashboard do not yet consume the new per-resource
    used/available state fields.
  - Resource usage is an average deterministic estimator over the task service
    interval, not packet-level or real execution telemetry.
- Recommended follow-up:
  - Bind frontend `ComputeNodeState` decoding and the selected-satellite /
    dashboard resource panels to the new per-resource used/available fields.

## 2026-07-05 - Dashboard Compute Resource Vector Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: bind the standalone dashboard compute resource pool to backend
  `runtimeStatus.metrics_summary` vector capacity totals while keeping the
  existing FP32 utilization chart and layout structure.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 22 files / 106 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - `git diff --check`
    - Result: passed with only CRLF warnings for excluded local runtime config
      files.
- Problems encountered:
  - Existing DataPanel tests include legacy mojibake snapshot text. Assertions
    were kept compatible and new vector assertions use ASCII field names.
- Known remaining issues:
  - The dashboard still shows dynamic utilization only for scalar FP32 because
    backend state does not yet publish per-lane available/used values.
  - The chart labels still use the existing FP32 resource-pool terminology.
- Recommended follow-up:
  - Add per-lane available/used compute-node state and then replace the FP32-only
    resource pool with a true multi-resource pool view.

## 2026-07-05 - Compute Resource Metrics Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: extend backend `MetricsCollector.summary()` with deterministic
  compute resource-vector capacity totals while keeping dynamic utilization
  explicitly scoped to legacy scalar FP32 availability.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `tests/unit/test_metrics_module.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py -q`
    - Result: passed, 8 tests.
  - `python -m pytest tests/integration/test_config_control.py::test_frontend_control_messages_are_processed tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 2 tests.
  - `git diff --check`
    - Result: passed with only CRLF warnings for excluded local runtime config
      files.
- Problems encountered:
  - There is no per-resource available/used field in `ComputeNodeState` yet, so
    GPU/NPU/memory/storage utilization was not fabricated. The summary exposes
    totals and a deterministic `SCALAR_FP32_AVAILABLE_ONLY` utilization mode.
- Known remaining issues:
  - Frontend dashboard still reads the scalar FP32 pool for dynamic usage.
  - Per-lane usage requires a separate compute-state contract update.
- Recommended follow-up:
  - Add optional per-resource available/used fields to `ComputeNodeState`, then
    bind dashboard resource-pool charts to those backend-provided fields.

## 2026-07-05 - Task Resource Demand Contract v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: extend `TaskRequest` and compute-service traffic generation with
  optional explicit CPU/GPU/NPU/memory/data resource-demand fields, and make the
  existing compute estimator consume them while preserving legacy scalar
  `compute_demand` behavior when explicit lanes are absent.
- Changed files/modules:
  - `src/leo_twin/schema/domain.py`
  - `src/leo_twin/models/compute/resources.py`
  - `src/leo_twin/models/compute/engine.py`
  - `src/leo_twin/models/compute/network_aware.py`
  - `src/leo_twin/models/traffic/demand.py`
  - `docs/product_contracts.md`
  - `tests/unit/test_product_contracts.py`
  - `tests/unit/test_compute_resource_model.py`
  - `tests/unit/test_compute_module.py`
  - `tests/unit/test_traffic_demand_model.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_product_contracts.py tests/unit/test_compute_resource_model.py tests/unit/test_compute_module.py tests/unit/test_network_aware_compute.py tests/unit/test_traffic_demand_model.py -q`
    - Result: passed, 34 tests.
  - `python -m pytest tests/integration/test_compute_service_lifecycle.py tests/integration/test_full_domain_pipeline_v1.py tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 4 tests.
  - `git diff --check`
    - Result: passed with only CRLF warnings for excluded local runtime config
      files.
- Problems encountered:
  - Existing `data_size` is network transfer size and many scenarios still use
    compute nodes with `storage_gb=0`. The new `input_data_mb` /
    `output_data_mb` fields therefore remain explicit instead of implicitly
    mirroring `data_size`, avoiding unintended storage-capacity failures.
- Known remaining issues:
  - Control-panel configuration does not yet expose task lane demands. This
    should be a separate frontend/backend configuration task.
  - Metrics and dashboard still report scalar FP32 utilization; per-lane
    utilization metrics remain a follow-up.
- Recommended follow-up:
  - Add control-plane configuration fields for representative task lane demand
    profiles, then emit per-lane utilization metrics for dashboard charts.

## 2026-07-05 - Compute Service-Time Estimator Wiring v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: route compute scheduling service-time calculations through the
  deterministic `ComputeResourceVector` / `TaskResourceDemand` estimator while
  preserving legacy `compute_demand / compute_capacity` timing semantics.
- Changed files/modules:
  - `src/leo_twin/models/compute/resources.py`
  - `src/leo_twin/models/compute/__init__.py`
  - `src/leo_twin/models/compute/engine.py`
  - `src/leo_twin/models/compute/network_aware.py`
  - `src/leo_twin/models/compute/scheduling.py`
  - `tests/unit/test_compute_resource_model.py`
  - `tests/unit/test_compute_scheduling_runtime.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_compute_resource_model.py tests/unit/test_compute_scheduling_runtime.py tests/unit/test_compute_module.py tests/unit/test_network_aware_compute.py -q`
    - Result: passed, 27 tests.
  - `python -m pytest tests/integration/test_compute_service_lifecycle.py tests/integration/test_full_domain_pipeline_v1.py -q`
    - Result: passed, 3 tests.
  - `git diff --check`
    - Result: passed with only CRLF warnings for excluded local runtime config
      files.
- Problems encountered:
  - The initial scheduling-runtime test expectation assumed the second task
    would wait for the faster node. The deterministic scheduler correctly chose
    the idle slower node because it tied the faster node's finish time. The
    assertion was corrected to preserve existing scheduling semantics.
- Known remaining issues:
  - `TaskRequest` still exposes the legacy scalar `compute_demand`; explicit
    GPU FP32/FP16, NPU INT8, memory, and storage task-demand fields should be
    introduced as a separate product-contract task.
  - Resource utilization metrics are not yet split by resource lane.
- Recommended follow-up:
  - Add explicit task resource-demand fields and emit per-lane utilization
    metrics before changing dashboard charts.

## 2026-07-05 - Runtime Compute Resource Vector State v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: publish configured compute resource vector fields through runtime
  compute node state, replay snapshots, frontend decoding, and the selected
  satellite resource inset while preserving scalar `compute_capacity`
  compatibility.
- Changed files/modules:
  - `src/leo_twin/models/compute/contracts.py`
  - `src/leo_twin/models/compute/engine.py`
  - `src/leo_twin/models/compute/network_aware.py`
  - `src/leo_twin/models/network/position_engine.py`
  - `src/leo_twin/schema/domain.py`
  - `src/leo_twin/services/scenario_builder.py`
  - `examples/integration_demo/scenario.py`
  - `examples/integration_demo/replay.py`
  - `examples/generated_full_system_demo.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/core/decoder/index.ts`
  - `frontend/src/state/snapshot_engine/index.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/3d/cesium/satelliteFollow.ts`
  - `tests/unit/test_compute_module.py`
  - `tests/unit/test_network_aware_compute.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `frontend/tests/eventDecoder.test.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_compute_module.py tests/unit/test_network_aware_compute.py tests/unit/test_integration_demo_scenario.py::test_demo_compute_resource_vector_is_config_driven tests/unit/test_product_contracts.py -q`
    - Result: passed, 19 tests.
  - `python -m pytest tests/unit/test_position_driven_network_engine.py::test_compute_node_update_reroutes_active_flows_with_capacity_feedback tests/integration/test_full_system_demo.py::test_replay_test -q`
    - Result: passed, 2 tests.
  - `python -m pytest tests/unit/test_scenario_builder.py tests/unit/test_backend_derived_summary.py tests/integration/test_config_control.py::test_frontend_control_messages_are_processed tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams -k "not default_generated_scenario_config_file_loads" -q`
    - Result: passed, 18 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts eventDecoder.test.ts renderPerformance.test.ts`
    - Result: passed, 22 files / 105 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - `git diff --check`
    - Result: passed with only CRLF warnings for excluded local runtime config
      files.
- Problems encountered:
  - The first frontend satellite visual test expectation used the old mojibake
    string and omitted numeric thousands formatting. The assertion was corrected
    to the actual UTF-8 UI label: `内存 48 GB / 存储 1,024 GB`.
  - The broader scenario-builder/config-control selection fails if
    `test_default_generated_scenario_config_file_loads` is included because the
    active local `configs/generated_full_system_demo.json` contains runtime
    120-node state while the repository baseline expects 6 satellites. That
    generated runtime config remains intentionally excluded.
- Known remaining issues:
  - Compute scheduling still uses scalar `compute_capacity` as CPU FP32
    compatibility capacity. Vector-aware service-time estimation remains a
    separate backend task.
  - The selected satellite resource inset now displays live vector fields when
    available, but dashboard aggregate charts still use existing summary and
    metric paths.
- Recommended follow-up:
  - Implement deterministic vector-aware compute service-time estimation and
    emit per-resource utilization metrics for CPU FP32/FP64, GPU FP32/FP16,
    NPU INT8, memory, and storage.

## 2026-07-05 - Frontend Compute Vector Controls v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: expose backend-supported compute resource vector fields in the
  existing control panel so users can configure CPU FP64, GPU FP32/FP16, NPU
  INT8, memory, and storage values during initialization without changing the
  frontend architecture.
- Changed files/modules:
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/app/App.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts appSurface.test.ts`
    - Result: passed, 22 files / 104 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - `scenarioWithRuntimeConfig` initially risked adding absent vector fields as
    explicit `undefined` keys. It now merges those fields only when a numeric
    value exists, preserving older scenario object shapes.
- Known remaining issues:
  - These controls configure backend summaries and generated config semantics.
    Runtime compute scheduling remains scalar until vector-aware scheduling is
    implemented as a separate task.
  - The active local runtime config files remain modified and excluded.
- Recommended follow-up:
  - Bind the resource vector controls to vector-aware compute service-time
    estimation in the runtime compute scheduler.

## 2026-07-05 - Compute Resource Vector Config v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: extend the SEES control-plane and generated demo configuration path
  with deterministic compute resource vector fields while preserving
  `compute_capacity` as the legacy CPU FP32 scheduling capacity.
- Changed files/modules:
  - `src/leo_twin/schema/config.py`
  - `src/leo_twin/schema/config_loader.py`
  - `src/leo_twin/services/derived_summary.py`
  - `src/leo_twin/services/scenario_builder.py`
  - `examples/integration_demo/config.py`
  - `examples/integration_demo/scenario.py`
  - `frontend/src/core/event_types/index.ts`
  - `tests/unit/test_backend_derived_summary.py`
  - `tests/unit/test_scenario_builder.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `tests/integration/test_config_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py tests/unit/test_scenario_builder.py::test_scenario_builder_config_from_sees_config_maps_control_plane_fields tests/unit/test_integration_demo_scenario.py::test_demo_compute_resource_vector_is_config_driven tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 9 tests.
  - `python -m pytest tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams tests/unit/test_scenario_builder.py tests/unit/test_integration_demo_scenario.py -q -k "not default_generated_scenario_config_file_loads"`
    - Result: passed, 22 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts configPanel.test.ts`
    - Result: passed, 22 files / 103 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Running the broader scenario-builder selection without a `-k` exclusion
    failed only at `test_default_generated_scenario_config_file_loads` because
    the active local `configs/generated_full_system_demo.json` still contains
    runtime 120-node state while the repository baseline expects 6 satellites.
    The file remains intentionally excluded from this task.
- Known remaining issues:
  - Runtime scheduling still consumes the legacy scalar `compute_capacity`.
    CPU/GPU/NPU/memory/storage fields currently drive backend-derived product
    summaries and generated config semantics, not per-lane scheduling.
  - The active local runtime config files remain modified and excluded.
- Recommended follow-up:
  - Add explicit frontend controls for the resource vector fields, then extend
    compute scheduling to use vector-aware service-time estimates.

## 2026-07-05 - Selected Satellite Compute Detail v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: make the satellite-follow inset show that selected satellites are
  satellite-hosted compute nodes, combining live snapshot load with backend-
  derived `ComputeResourceVector` summary fields for CPU, GPU, NPU, memory, and
  storage explanations.
- Changed files/modules:
  - `frontend/src/3d/cesium/satelliteFollow.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 22 files / 103 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The satellite-follow inset previously only exposed legacy scalar capacity;
    the new vector fields are additive and keep the existing live load labels
    for backward compatibility.
- Known remaining issues:
  - Runtime `ComputeNodeState` still carries legacy scalar capacity. The
    multidimensional vector is displayed from backend-derived scenario summary
    until a later task adds explicit per-node vector state to snapshots.
  - The active local runtime config files remain modified and excluded.
- Recommended follow-up:
  - Add backend/runtime snapshot support for per-satellite compute resource
    vectors so live scheduling can consume CPU/GPU/NPU dimensions directly.

## 2026-07-05 - Backend Summary Integration Assertions v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: strengthen integration-level acceptance that generated demo/control
  configurations expose backend-derived orbital period, coverage/beam summary,
  and compute vector summary fields beyond unit-level summary tests.
- Changed files/modules:
  - `tests/integration/test_config_control.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py tests/unit/test_integration_demo_scenario.py::test_demo_scenario_auto_allocates_starlink_like_planes_when_not_explicit tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams -q`
    - Result: passed, 7 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 22 files / 102 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The exact Starlink-like constellation summary fixture needed to include the
    newly added orbital period fields.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - These are contract assertions; browser screenshot-level visual acceptance
    is still not present because this repository has no Playwright setup yet.
- Recommended follow-up:
  - Add a dedicated browser smoke harness if Playwright is introduced later.

## 2026-07-05 - 3D Beam Summary Binding v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: bind the 3D selected-satellite beam renderer to backend-derived
  coverage/beam summary fields for beam length, footprint radius, and bounded
  beam-cell count, while preserving legacy render defaults as fallback values.
- Changed files/modules:
  - `frontend/src/3d/beam_renderer/beamEntities.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 22 files / 102 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Backend-provided beam counts must not expand unbounded detail rendering in
    1200-satellite scenarios, so the frontend clamps selected-satellite
    footprint cells to the existing safe 1..7 range.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - The backend summary is still generated scenario metadata. Per-satellite
    coverage state is not yet streamed in `WorldSnapshot`.
- Recommended follow-up:
  - Add selected-satellite coverage state to snapshots so beam utilization and
    count can vary by satellite and simulation time.

## 2026-07-05 - Orbit Period Explanation v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: add a backend-derived simplified circular orbital period estimate to
  constellation summaries and display the period in the frontend generated
  scenario summary.
- Changed files/modules:
  - `src/leo_twin/services/derived_summary.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 5 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 22 files / 100 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - This is intentionally a circular-orbit period explanation. It does not add
    SGP4, external ephemeris, or high-fidelity orbit mechanics.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - The frontend still needs a clearer distinction between physical orbital
    period and demo playback speed.
- Recommended follow-up:
  - Add separate playback-speed and physical-orbit explanatory text near the
    runtime controls.

## 2026-07-05 - Dashboard Throughput Fallback v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: make dashboard network throughput prefer positive backend delivered
  throughput and fall back to backend loss-adjusted available throughput before
  using offered capacity or snapshot link capacity.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 22 files / 100 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Existing `network_quality_estimated_delivered_throughput_mbps` must remain
    backward compatible, so the dashboard fallback is additive rather than a
    field rename.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - Throughput is still a deterministic flow-level KPI proxy until traffic
    demand carries delivered data size over simulated time.
- Recommended follow-up:
  - Add flow data-size accounting to backend metrics so delivered throughput can
    be computed from completed data volume and simulation time.

## 2026-07-05 - Compute Resource Vector Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: expose full compute resource vector dimensions in backend-derived
  summaries and display GPU, NPU, memory, and storage dimensions in the
  frontend generated scenario summary while preserving legacy FP32 capacity
  compatibility.
- Changed files/modules:
  - `src/leo_twin/services/derived_summary.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py tests/unit/test_compute_resource_model.py -q`
    - Result: passed, 12 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 22 files / 99 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Current SEES runtime config still supplies a legacy scalar compute capacity,
    so non-FP32 lanes are surfaced as zero until a later config task adds
    explicit GPU/NPU/memory/storage fields.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - Runtime compute-node state still carries scalar capacity for compatibility.
    The vector is currently visible in backend-derived generated scenario
    semantics, not live per-node scheduling state.
- Recommended follow-up:
  - Add explicit compute resource vector config fields and map satellite-hosted
    compute nodes to vector capacities in runtime snapshots.

## 2026-07-05 - Backend Coverage Beam Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: add a backend-derived coverage/beam semantic summary and have the
  frontend scenario summary display beam mode, default beam count, and footprint
  radius from backend-provided fields.
- Changed files/modules:
  - `src/leo_twin/services/derived_summary.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 5 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 22 files / 99 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Existing UTF-8 Chinese UI files display as mojibake in the PowerShell
    console, so patches were anchored on ASCII identifiers to avoid accidental
    unrelated text churn.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - Coverage summary describes the current bounded visual footprint only. Beam
    utilization, per-satellite beam count, and backend coverage geometry are
    not yet dynamic model outputs.
- Recommended follow-up:
  - Add backend-selected satellite coverage fields to `WorldSnapshot` so the
    3D view can consume beam count/radius directly from snapshot state.

## 2026-07-05 - Selected Satellite Multi-Beam Footprint v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: add a bounded honeycomb-style multi-beam footprint for the selected
  satellite in the Cesium globe while keeping global large-scale rendering
  limited to avoid 1200-node regressions.
- Changed files/modules:
  - `frontend/src/3d/beam_renderer/beamEntities.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 22 files / 99 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - One initial test used exact equality for a floating-point radius derived
    from `160000 * 0.34`; it was corrected to a tolerance-based assertion.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - The honeycomb cells are deterministic visual footprints around the nadir
    point. They are not antenna-pattern, RF propagation, or interference
    models.
  - Only the selected satellite renders detailed cells; large-scale global
    multi-beam rendering remains intentionally bounded.
- Recommended follow-up:
  - Move beam count, footprint radius, and beam utilization coloring into
    backend-derived satellite/coverage summary fields.

## 2026-07-05 - Flow-Level Network KPI Dynamics v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: make backend network quality summaries less static by adding
  deterministic flow-level route-latency history, congestion, failed-flow, loss
  proxy, and available-throughput fields while preserving existing metrics
  names consumed by the frontend.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `tests/unit/test_metrics_module.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py -q`
    - Result: passed, 8 tests.
  - `python -m pytest tests/integration/test_runtime_session_control.py tests/integration/test_live_runtime_streaming.py -q`
    - Result: passed, 19 tests.
  - `python -m pytest tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 5 tests.
- Problems encountered:
  - The project does not yet carry packet-level observations or per-flow data
    sizes in `FlowState`, so throughput/loss remain deterministic flow-level
    proxies. No packet-level simulation was introduced.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - `network_quality_estimated_delivered_throughput_mbps` still uses completed
    route capacity for backward compatibility. The new
    `network_quality_estimated_available_throughput_mbps` field is the loss-
    adjusted offered-capacity proxy.
  - Jitter is modeled as route latency standard deviation plus per-route
    latency-delta history, not packet inter-arrival variation.
- Recommended follow-up:
  - Extend traffic demand contracts with deterministic flow data size and
    offered-load fields so throughput can be computed as delivered data over
    simulated time.

## 2026-07-05 - Natural Earth Globe Boundary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: improve 3D Earth country visibility by bundling Natural Earth 1:110m
  Admin 0 country boundaries and replacing the coarse fallback overlays after
  the local GeoJSON asset loads.
- Changed files/modules:
  - `frontend/public/assets/natural-earth/README.md`
  - `frontend/public/assets/natural-earth/ne_110m_admin_0_countries.geojson`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/3d/cesium/countryOverlays.ts`
  - `frontend/tests/countryOverlays.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- countryOverlays.test.ts`
    - Result: passed, 22 files / 98 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - Bundled Node:
    `node -e "JSON.parse(fs.readFileSync('frontend/public/assets/natural-earth/ne_110m_admin_0_countries.geojson','utf8'))"`
    - Result: parsed as `FeatureCollection` with 177 features.
- Problems encountered:
  - PowerShell `ConvertFrom-Json` failed on the large multilingual GeoJSON, so
    validation used Node JSON parsing, which matches the frontend runtime.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - The boundary layer uses one largest outer ring per country for a lightweight
    visual overlay; islands and detailed disputed boundaries remain simplified.
  - This task improves country boundary visibility but does not add a high-
    resolution Earth texture or cloud layer.
- Recommended follow-up:
  - Add screenshot/canvas visual regression for globe opacity, boundary
    visibility, and far-side satellite occlusion.

## 2026-07-05 - NASA Satellite Kit Asset Pipeline v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this commit
- Scope: replace the primary Cesium satellite display with bundled, licensed
  NASA Satellite Kit GLB assets while preserving the deterministic fallback
  satellite-part helper used by tests.
- Changed files/modules:
  - `frontend/public/assets/nasa-satellite-kit/README.md`
  - `frontend/public/assets/nasa-satellite-kit/satellite-kit-body-2.glb`
  - `frontend/public/assets/nasa-satellite-kit/satellite-kit-wings-2.glb`
  - `frontend/public/assets/nasa-satellite-kit/satellite-kit-radio-1.glb`
  - `frontend/src/3d/orbit_renderer/satelliteModelEntities.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 22 files / 96 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Direct Node filesystem imports in the frontend test compile failed because
    the frontend TypeScript config intentionally does not include Node runtime
    types. The test was kept browser/Vite-compatible and now validates the
    model asset contract through exported GLB URIs.
  - Asset source and usage guidance were verified from NASA 3D Resources and
    recorded with SHA-256 hashes in the asset README. NASA media and brand
    usage guidance still applies.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - The bundled satellite is a generic NASA Satellite Kit visual, not an exact
    Starlink bus model.
  - Cesium GLB loading still needs browser screenshot/canvas visual regression
    coverage in a later task.
- Recommended follow-up:
  - Add automated visual QA for GLB loading, satellite orientation, and
    distance-based level-of-detail behavior in the 3D globe.

## 2026-07-05 - Ten Hour Product Enrichment Plan

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `dc1a18b`
- Scope: create a bounded 10-hour product enrichment plan covering frontend-
  backend consistency, 3D Earth quality, satellite assets, coverage and
  multi-beam visualization, resource inspection, network KPI dynamics, compute
  semantics, validation, and multi-agent task flow.
- Changed files/modules:
  - `docs/ten_hour_product_enrichment_plan.md`
  - `docs/development_log.md`
- Validation:
  - `git diff --check -- docs/ten_hour_product_enrichment_plan.md docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - The plan references EXATA only as an inspiration for layered flow-level KPI
    semantics; the project remains forbidden from integrating EXATA or any
    external simulator runtime.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - This is a planning/logging slice. Implementation should proceed in the
    commit slices listed in the plan.
- Recommended follow-up:
  - Start with route/session synchronization and reset semantics before the
    larger 3D asset and metric-model work.

## 2026-07-05 - Frontend Runtime Session Sync v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `422432a`
- Scope: keep the control console and standalone dashboard attached to the same
  runtime session semantics by tightening frontend stream reset policy and
  forcing visible progress/event counts to zero during reset-like transitions.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- appSurface.test.ts`
    - Result: passed, 22 files / 88 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The existing frontend source contains Chinese text that appears mojibake in
    the PowerShell terminal. This task intentionally changed only logic and
    tests around runtime reset semantics, avoiding unrelated text rewrites.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - This slice fixes frontend reset/reattach semantics. Backend-owned KPI
    semantics for throughput, jitter, loss proxy, and compute resources remain
    follow-up work.
- Recommended follow-up:
  - Add backend-owned network quality and compute resource summaries, then bind
    dashboard charts to those summaries instead of local KPI inference.

## 2026-07-05 - Frontend State Stream Freshness v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `aba6caf`
- Scope: prevent stale state snapshots from rolling frontend satellite, task,
  and compute-node state backwards after newer event-stream updates, and make
  the configuration panel respect backend-provided compute node counts while
  preserving satellite-as-compute-node convenience when users change satellite
  count.
- Changed files/modules:
  - `frontend/src/state/reducer/index.ts`
  - `frontend/src/stream/state_store/index.ts`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/tests/renderPerformance.test.ts`
  - `frontend/tests/stateStore.test.ts`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- renderPerformance.test.ts stateStore.test.ts configPanel.test.ts`
    - Result: passed, 22 files / 91 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The first target test asserted `sim_time` on `WorldSnapshot.compute_nodes`,
    but the rendered compute-node contract intentionally omits that field. The
    test was adjusted to verify visible anti-rollback fields instead:
    `available_capacity` and `status`.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - State snapshots still upsert links and routes without per-entity freshness
    checks because those frontend contracts do not currently include
    `sim_time`.
  - Earth far-side visual bleed-through and backend-owned KPI semantics remain
    separate follow-up tasks.
- Recommended follow-up:
  - Fix Cesium depth/opaque globe rendering next, then add backend-owned network
    quality summaries for throughput, delay, loss proxy, and jitter.

## 2026-07-05 - Cesium Globe Depth Occlusion v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `dd7d0c6`
- Scope: reduce the transparent-globe effect by keeping satellite point,
  billboard, and label overlays depth-tested, and enabling Cesium globe depth
  testing against the terrain/ellipsoid surface so far-side satellites are
  occluded by Earth.
- Changed files/modules:
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/3d/orbit_renderer/satelliteEntities.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts visualLayerLimits.test.ts countryOverlays.test.ts`
    - Result: passed, 22 files / 92 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - No Playwright screenshot baseline exists in this repository yet. This slice
    uses deterministic unit checks and TypeScript/Vite build validation; a
    later visual QA task should add screenshot/canvas checks.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - The satellite model is still a code-built multi-part primitive, not a
    licensed downloaded glTF asset.
  - Selected-satellite foreground emphasis may need a separate design after
    full depth testing hides far-side labels as intended.
- Recommended follow-up:
  - Add licensed satellite glTF assets and screenshot-based visual acceptance
    checks, then implement selected-satellite coverage and beam rendering.

## 2026-07-05 - Backend Metrics Quality Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `7509d90`
- Scope: add backend-owned flow-level network quality proxy fields and
  satellite-hosted compute resource pool fields to `MetricsCollector.summary()`
  without introducing packet-level simulation or extra metric events.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `tests/unit/test_metrics_module.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py -q`
    - Result: passed, 7 tests.
  - `python -m pytest tests/integration/test_full_domain_pipeline_v1.py tests/integration/test_full_system_demo.py -q`
    - Result: passed, 14 tests.
  - `python -m pytest tests/integration/test_full_system_pipeline.py tests/integration/test_generated_full_system_demo.py tests/integration/test_orbit_batch_scale.py tests/scale/test_position_network_scale_smoke.py -q`
    - Result: passed, 18 tests.
- Problems encountered:
  - The first implementation emitted new metric records for
    `COMPUTE_NODE_UPDATE`, which increased full-system demo processed event
    count from 21,849 to 21,865. That would break existing deterministic event
    baselines, so compute resource collection was changed to summary-only.
  - The new `network_quality_loss_proxy_rate` is explicitly a flow-level route
    blocking proxy, not packet loss.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - Runtime status and frontend dashboard do not yet consume these backend-owned
    KPI fields directly.
  - Link and route contracts still lack per-update timestamp fields for richer
    temporal jitter analysis.
- Recommended follow-up:
  - Bind dashboard KPI charts to backend-owned `network_quality_*` and
    `compute_resource_*` fields, then add timestamped link/route quality
    contract fields in a separate task if needed.

## 2026-07-05 - Runtime Metrics Summary Binding v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `3f54984`
- Scope: expose `MetricsCollector.summary()` through runtime status and make
  the standalone DataPanel prefer backend-owned `network_quality_*` and
  `compute_resource_*` fields for dynamic telemetry values.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 22 files / 93 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - `python -m pytest tests/integration/test_runtime_session_control.py tests/integration/test_live_runtime_streaming.py -q`
    - Result: passed, 19 tests.
- Problems encountered:
  - TypeScript/esbuild rejected a mixed `??` / `||` expression without
    parentheses. The throughput fallback expression was split into a stable
    intermediate value and retested.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - Dashboard charts still use a frontend envelope over backend values rather
    than a backend-owned time-series sample window.
  - The loss field is still a route-blocking proxy and is intentionally not
    packet loss.
- Recommended follow-up:
  - Add backend-owned time-series samples for network quality and compute
    resource pool consumption, then remove the local envelope approximation.

## 2026-07-05 - Selected Satellite Coverage Beam v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `67ddf82`
- Scope: enable a bounded selected-satellite coverage beam in the Cesium view
  by rendering at most one coverage cone for the active selected satellite.
  This is a visual abstraction only and does not introduce RF propagation or
  antenna pattern modeling.
- Changed files/modules:
  - `frontend/src/3d/beam_renderer/beamEntities.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/3d/cesium/renderLimits.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `frontend/tests/visualLayerLimits.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts visualLayerLimits.test.ts`
    - Result: passed, 22 files / 94 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The existing renderer had a beam entity path but `beamRenderLimit` was set
    to zero, so no coverage visualization could appear. The limit is now one
    and the selection filter prevents large-scale beam fan-out.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - This is a single selected-satellite coverage cone, not honeycomb
    multi-beam cells.
  - The cone is a simplified visual cue and is not RF/antenna fidelity.
- Recommended follow-up:
  - Add backend-derived coverage assumptions and a selected-satellite resource
    inspector before implementing multi-beam cell overlays.

## 2026-07-05 - Selected Satellite Resource Inset v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: this commit (created before hash assignment)
- Scope: show selected satellite compute-node resource status in the satellite
  follow inset, reflecting the product assumption that satellites are compute
  nodes when matching compute-node ids are present in the snapshot.
- Changed files/modules:
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/3d/cesium/satelliteFollow.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 22 files / 95 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The Cesium component file contains existing Chinese UI strings that appear
    as mojibake in PowerShell output. The task limited text changes to the new
    inset resource rows.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - The inset only shows resources for selected satellites whose ids match
    compute-node ids in the snapshot.
  - It still uses the legacy scalar FP32 GFLOPS capacity fields.
- Recommended follow-up:
  - Extend snapshot compute nodes with `ComputeResourceVector` dimensions and
    show CPU/GPU/NPU/memory/storage resource lanes in the selected-satellite
    inspector.

## 2026-07-04 - Development Log Requirement

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: this commit
- Scope: document the mandatory development log workflow.
- Changed files:
  - `docs/codex_skill.md`
  - `docs/development_log.md`
- Validation:
  - `git diff --check`
- Problems encountered:
  - The workspace still contains local runtime/config state in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`.
    These files are intentionally excluded from this documentation task.
- Follow-up:
  - Future development tasks must add a dated entry here before commit.

## 2026-07-04 - Windows Demo Launcher

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `8ca7331`
- Scope: add a Windows one-click launcher for starting, stopping, restarting,
  and checking the SEES demo backend/frontend services.
- Changed files/modules:
  - `scripts/sees_launcher.ps1`
  - `start_leo_twin.bat`
  - `restart_leo_twin.bat`
  - `stop_leo_twin.bat`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - PowerShell AST parse for `scripts/sees_launcher.ps1`
    - Result: passed.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sees_launcher.ps1 status`
    - Result: passed; reported backend/frontend stopped on ports 8765/5173
      in the current local environment.
  - `git diff --check -- . ':(exclude)configs/generated_full_system_demo.json' ':(exclude)configs/sees_control.yaml'`
    - Result: passed.
- Problems encountered:
  - The active workspace still has unrelated local runtime config changes in
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`;
    they remain excluded from this task.
  - The launcher start path was not executed during validation to avoid
    changing the user's currently running local service state.
- Known remaining issues:
  - The launcher depends on Python and pnpm/corepack being available from the
    user's PATH. A later packaged desktop app can bundle these dependencies.
- Recommended follow-up:
  - Package the launcher as a small desktop application or tray controller
    after backend/frontend workflows stabilize.

## 2026-07-04 - Windows Launcher Readiness Fix

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `686894d`
- Scope: fix launcher startup when Node.js is available only through the
  bundled Codex runtime and delay browser opening until service ports are
  actually ready.
- Changed files/modules:
  - `scripts/sees_launcher.ps1`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - PowerShell AST parse for `scripts/sees_launcher.ps1`
    - Result: passed.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sees_launcher.ps1 start -NoBrowser`
    - Result: passed; backend became ready on port 8765 and frontend became
      ready on port 5173.
  - `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173/`
    - Result: HTTP 200.
  - `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/runtime/status`
    - Result: HTTP 200.
  - `git diff --check -- . ':(exclude)configs/generated_full_system_demo.json' ':(exclude)configs/sees_control.yaml'`
    - Result: passed.
- Problems encountered:
  - The first launcher version found `pnpm.cmd` from the bundled runtime but
    did not add the sibling bundled `node.exe` directory to PATH, so Vite could
    exit immediately with `node` unavailable.
  - The first launcher version opened the browser before Vite/backend ports
    were ready, which could leave the user on a connection failure page.
- Known remaining issues:
  - This is still a script launcher. A packaged app should eventually capture
    service logs and show health status in one window.
- Recommended follow-up:
  - Add log files or a small local tray UI for backend/frontend process output.

## 2026-07-04 - 1200 Node Live Control Stabilization

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `9168508`
- Scope: keep 1200-satellite live runtime responsive after batch orbit updates
  by bounding server-side advance loop work and avoiding detailed space-space
  link updates for very large orbit batches.
- Changed files/modules:
  - `src/leo_twin/runtime/session.py`
  - `src/leo_twin/runtime/advance_loop.py`
  - `src/leo_twin/models/network/position_engine.py`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/replay.py`
  - `tests/integration/test_live_runtime_streaming.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_live_runtime_streaming.py::test_large_batch_runtime_keeps_snapshot_and_controls_responsive -q`
    - Result: passed.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py tests/integration/test_runtime_session_control.py tests/integration/test_orbit_batch_scale.py tests/unit/test_position_driven_network_engine.py tests/unit/test_metrics_module.py -q`
    - Result: passed, 55 tests.
  - 1200-satellite WebSocket control smoke against local demo server:
    - `INITIALIZE`: acknowledged in 118 ms.
    - `/metrics/snapshot`: returned 1200 satellites.
    - `START`: acknowledged in 57 ms.
    - `/stream/state`: first satellite-bearing frame contained 1200 satellites.
    - `PAUSE`: acknowledged in 63 ms.
    - `STOP`: acknowledged in 62 ms.
    - `RESET`: acknowledged in 186 ms.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test`
    - Result: passed, 22 files / 78 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - `git diff --check -- . ':(exclude)configs/generated_full_system_demo.json' ':(exclude)configs/sees_control.yaml'`
    - Result: passed.
- Problems encountered:
  - Reproduction showed `INITIALIZE` and `START` returned quickly, but `PAUSE`
    did not acknowledge within 30 seconds because the background advance loop
    held the session lock while processing a large same-time network batch.
  - The initial live snapshot had no satellites because `DemoStateProjector`
    started empty and the control plane did not expose session snapshots while
    lifecycle state was `INITIALIZED`.
  - The active local workspace config files were modified by runtime control
    tests and remain excluded from the commit scope.
- Known remaining issues:
  - Large batches still update satellite state and star-ground access, but
    detailed space-space link updates are skipped once a batch exceeds the
    configured threshold. This keeps live control responsive but is not a
    high-fidelity ISL scale model.
- Recommended follow-up:
  - Add a frontend-visible fidelity notice explaining when large-scale mode
    skips detailed space-space link updates.

## 2026-07-04 - Scale Fidelity Notice v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `3672b4c`
- Scope: expose backend-owned scale fidelity mode details through runtime
  status, generated backend summary, and live state snapshots, then render a
  visible frontend notice when large-scale mode reduces fidelity.
- Changed files/modules:
  - `src/leo_twin/services/scale_fidelity.py`
  - `src/leo_twin/models/network/position_engine.py`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/replay.py`
  - `examples/integration_demo/scenario.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/core/decoder/index.ts`
  - `frontend/src/state/reducer/index.ts`
  - `frontend/src/state/snapshot_engine/index.ts`
  - `frontend/src/stream/state_store/index.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `tests/integration/test_live_runtime_streaming.py`
  - `tests/integration/test_runtime_session_control.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `frontend/tests/appSurface.test.ts`
  - `frontend/tests/eventDecoder.test.ts`
  - `frontend/tests/stateStore.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_live_runtime_streaming.py::test_large_batch_runtime_keeps_snapshot_and_controls_responsive tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 4 tests.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py tests/integration/test_runtime_session_control.py tests/integration/test_orbit_batch_scale.py tests/unit/test_position_driven_network_engine.py tests/unit/test_metrics_module.py tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 57 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test`
    - Result: passed, 22 files / 82 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - 1200-satellite direct control-plane smoke:
    - `INITIALIZE`: 43.4 ms.
    - `START`: 0.6 ms.
    - First state stream batch after one bounded tick included
      `fidelity_summary.space_link_mode=REDUCED_LARGE_BATCH`.
    - `PAUSE`: 0.2 ms.
    - `STOP`: 10.8 ms.
    - `RESET`: 47.7 ms.
- Problems encountered:
  - The first state-stream assertion ran immediately after `START`; no
    snapshot had been published yet, so the test now advances one bounded tick
    before checking the cursor batch.
  - A direct Python smoke script initially failed outside pytest because
    `PYTHONPATH` was not set. It passed after using `PYTHONPATH=src;.`.
  - The active local runtime config files remain modified by local runs and
    are intentionally excluded from this commit.
- Known remaining issues:
  - Large-scale mode is now transparent to users, but 1200-satellite ISL
    fidelity is still reduced: detailed space-space link updates are skipped
    beyond the current batch threshold.
  - Task 2, bounded ISL candidate modeling, was not mixed into this commit so
    the transparency change remains isolated and reviewable.
- Recommended follow-up:
  - Implement Bounded ISL Candidate Model v1 as the next separate network
    fidelity task, with explicit config fields and cap/determinism tests.

## 2026-07-04 - Scale Mode Productization v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `73fab2b`
- Scope: make 1200-satellite scale mode an explicit backend-owned product mode
  and replace silent large-batch ISL skipping with deterministic bounded
  candidate updates.
- Changed files/modules:
  - `src/leo_twin/schema/config.py`
  - `src/leo_twin/schema/config_loader.py`
  - `src/leo_twin/core/config/__init__.py`
  - `src/leo_twin/core/config/schema.py`
  - `src/leo_twin/models/network/position_engine.py`
  - `src/leo_twin/models/network/__init__.py`
  - `src/leo_twin/services/scale_fidelity.py`
  - `src/leo_twin/services/scenario_builder.py`
  - `examples/integration_demo/config.py`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/runtime.py`
  - `examples/integration_demo/scenario.py`
  - `examples/integration_demo/replay.py`
  - `examples/generated_full_system_demo.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/core/decoder/index.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `frontend/tests/eventDecoder.test.ts`
  - `frontend/tests/stateStore.test.ts`
  - `tests/integration/test_config_control.py`
  - `tests/integration/test_live_runtime_streaming.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `tests/unit/test_position_driven_network_engine.py`
  - `tests/unit/test_scenario_builder.py`
  - `docs/scale_mode_1200_acceptance.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py tests/unit/test_position_driven_network_engine.py -q`
    - Result: passed, 29 tests.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py::test_large_batch_runtime_keeps_snapshot_and_controls_responsive -q`
    - Result: passed.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py tests/integration/test_orbit_batch_scale.py tests/unit/test_metrics_module.py -q`
    - Result: passed, 20 tests.
  - `python -m pytest tests/integration/test_config_control.py::test_network_protocol_profile_can_be_updated_directly tests/integration/test_config_control.py::test_frontend_control_messages_are_processed tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams tests/unit/test_scenario_builder.py::test_scenario_builder_config_from_sees_config_maps_control_plane_fields tests/unit/test_scenario_builder.py::test_load_full_system_scenario_builder_config_from_json tests/unit/test_scenario_builder.py::test_write_full_system_scenario_builder_config_round_trips -q`
    - Result: passed, 6 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test`
    - Result: passed, 22 files / 82 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - Clean detached worktree from the committed tree:
    `python -m pytest -q`
    - Result: passed, 270 tests.
  - 1200-satellite live control smoke using the real `INITIALIZE` path:
    - `INITIALIZE`: ok in 51.76 ms.
    - `START`: status `RUNNING`.
    - One explicit advance-loop tick completed in 16164.06 ms.
    - `PAUSE`: acknowledged in 0.27 ms.
    - `STOP`: acknowledged in 10.92 ms.
    - `RESET`: acknowledged in 127.94 ms and visible satellites reset to 0.
    - Fidelity summary reported `orbit_update_mode=BATCH`,
      `metrics_mode=AGGREGATED`, and `space_link_mode=BOUNDED_CANDIDATE`.
- Problems encountered:
  - Running `python -m pytest tests/integration/test_config_control.py tests/unit/test_scenario_builder.py -q`
    in the active workspace failed only on tests that read the two known local
    runtime config files. The files currently contain 1200-node local state
    while repository baselines expect 72 and 6 respectively.
  - A direct 1200 `run_integration_demo()` smoke timed out because it exercised
    offline precomputed demo execution instead of the live control path. The
    validation was rerun through the frontend-equivalent `INITIALIZE` live path.
  - Clean-worktree frontend verification was attempted after commit. Running
    frontend test/build in parallel caused a pnpm `EEXIST`/`EBUSY` symlink race
    in the temporary `node_modules`; rerunning sequentially then hit npm
    registry `ECONNRESET`/`fetch failed` while installing clean dependencies.
    The active workspace frontend test/build had already passed with the
    existing dependency installation.
  - The first live advance tick remains heavy when 1200 satellites are also
    configured as 1200 compute nodes with same-time flow/task bursts.
- Known remaining issues:
  - `BOUNDED_CANDIDATE` is a deterministic approximation. It does not model
    high-fidelity ISL geometry, RF/optical acquisition, or packet-level
    behavior.
  - The first tick can still take multiple seconds under the current
    1200-node traffic/compute burst. Pause/stop/reset remain responsive after
    the tick returns, but the next scale task should smooth first-tick
    workload.
  - The active local runtime config files remain excluded from the commit.
- Recommended follow-up:
  - Implement deterministic traffic/compute first-tick smoothing and runtime
    backpressure reporting for 1200 satellite-as-compute-node scenarios.

## 2026-07-05 - Runtime Load Smoothing & Backpressure v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: this commit (created before hash assignment)
- Scope: reduce 1200-node first-tick workload spikes and expose backend-owned
  runtime profiling/backpressure status without changing Event Kernel ordering.
- Changed files/modules:
  - `src/leo_twin/runtime/profiling.py`
  - `src/leo_twin/runtime/session.py`
  - `src/leo_twin/runtime/advance_loop.py`
  - `src/leo_twin/runtime/status.py`
  - `src/leo_twin/runtime/__init__.py`
  - `src/leo_twin/schema/config.py`
  - `src/leo_twin/schema/config_loader.py`
  - `src/leo_twin/core/config/__init__.py`
  - `src/leo_twin/core/config/schema.py`
  - `src/leo_twin/models/network/position_engine.py`
  - `examples/integration_demo/config.py`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/runtime.py`
  - `examples/integration_demo/scenario.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `tests/integration/test_live_runtime_streaming.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_integration_demo_scenario.py tests/integration/test_live_runtime_streaming.py::test_large_batch_runtime_keeps_snapshot_and_controls_responsive -q`
    - Result: passed, 11 tests.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py tests/integration/test_runtime_session_control.py tests/integration/test_orbit_batch_scale.py tests/unit/test_position_driven_network_engine.py tests/unit/test_metrics_module.py tests/unit/test_integration_demo_scenario.py -q`
    - Result: passed, 68 tests.
  - `python -m pytest tests/unit/test_integration_demo_scenario.py tests/integration/test_live_runtime_streaming.py::test_large_batch_runtime_keeps_snapshot_and_controls_responsive tests/integration/test_config_control.py::test_frontend_control_messages_are_processed tests/unit/test_scenario_builder.py::test_scenario_builder_config_from_sees_config_maps_control_plane_fields tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 15 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test`
    - Result: passed, 22 files / 84 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - 1200-satellite / 1200-compute direct control-plane smoke:
    - Previous recorded first explicit tick: 16164.06 ms.
    - Current first explicit tick: 1805.53 ms.
    - Processed events in tick: 4073.
    - Backpressure summary reported `overloaded=true`,
      `tick_budget_ms=1000.0`, `bottleneck_component=metrics_aggregation`.
    - Workload smoothing summary reported
      `mode=DETERMINISTIC_STAGGER`, `initial_workload_window_s=59.0`,
      `spacing_s=0.04920767306088407`, `workload_count=1200`.
- Problems encountered:
  - `python -m pytest tests/integration/test_config_control.py tests/unit/test_scenario_builder.py tests/unit/test_backend_derived_summary.py -q`
    still fails in the active workspace only on tests that read the two known
    local runtime config files. `configs/sees_control.yaml` and
    `configs/generated_full_system_demo.json` contain local 1200-node state and
    remain excluded from this commit.
  - A direct smoke script initially failed because `PYTHONPATH=src;.` was not
    set outside pytest. The same smoke passed after setting `PYTHONPATH`.
  - The new frontend smoothing fields initially appeared in small-scenario
    `traffic_model` output as default values. This was corrected so small
    scenarios keep their existing frontend fixture shape unless smoothing is
    explicit or scale-triggered.
- Known remaining issues:
  - The first scale tick is reduced substantially but can still exceed the
    1-second runtime budget because metrics aggregation and snapshot projection
    are still in-process.
  - Phase 4 bounded wall-time tick budgeting was not implemented in this task;
    doing it cleanly should be a separate runtime scheduling task if needed.
  - Active local runtime/generated config files remain excluded from the commit.
- Recommended follow-up:
  - Optimize or aggregate metrics/snapshot projection for scale mode, using the
    new profiling/backpressure fields as the acceptance signal.

## 2026-07-05 - Morning Product Hardening Baseline

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: this commit (created before hash assignment)
- Scope: establish Phase 0 baseline health before further product hardening.
- Changed files/modules:
  - `docs/morning_hardening_baseline.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_live_runtime_streaming.py tests/integration/test_runtime_session_control.py tests/integration/test_orbit_batch_scale.py tests/unit/test_position_driven_network_engine.py tests/unit/test_metrics_module.py tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 60 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test`
    - Result: passed, 22 files / 84 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - Integration demo control-plane smoke:
    - 72 satellites: initialize/start/tick/pause/stop/reset passed; explicit
      tick 15.92 ms; state stream contained satellites and fidelity summary.
    - 1200 satellites / 1200 compute nodes: initialize/start/tick/pause/stop/reset
      passed; explicit full START-path tick 2169.18 ms; state stream contained
      satellites and fidelity summary.
    - Isolated 1200 explicit first tick: 1466.91 ms, 4073 events,
      `bottleneck_component=metrics_aggregation`, `overloaded=true`.
- Problems encountered:
  - The smoke scripts required `PYTHONPATH=src;.` when run directly outside
    pytest.
  - The active local runtime config files remain modified and are intentionally
    excluded from this baseline commit.
- Known remaining issues:
  - 1200-scale runtime is controllable, but the first tick still exceeds the
    1000 ms budget. Profiling shows metrics aggregation and snapshot projection
    dominate the remaining cost.
- Recommended follow-up:
  - Treat scale-mode metrics/snapshot aggregation as the next targeted hardening
    phase before broader product UI or business-model work.

## 2026-07-05 - Business Model Deepening v1A

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: this commit (created before hash assignment)
- Scope: enrich backend-derived constellation summaries with deterministic
  orbit/allocation semantics for product explanation surfaces.
- Changed files/modules:
  - `src/leo_twin/services/derived_summary.py`
  - `src/leo_twin/services/scenario_builder.py`
  - `examples/integration_demo/scenario.py`
  - `frontend/src/core/event_types/index.ts`
  - `tests/unit/test_backend_derived_summary.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py tests/unit/test_integration_demo_scenario.py tests/unit/test_scenario_builder.py::test_scenario_builder_config_from_sees_config_maps_control_plane_fields tests/integration/test_config_control.py::test_frontend_control_messages_are_processed tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams -q`
    - Result: passed, 18 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test`
    - Result: passed, 22 files / 84 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Existing tests used exact dictionary comparisons for derived summaries.
    The tests were intentionally updated to include the new backend-owned
    semantic fields.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - This phase completed the constellation-summary portion of Phase 3 only.
    Traffic demand, compute resource, and communication-compute lifecycle
    already have baseline implementations and tests, but they were not expanded
    further in this isolated commit.
- Recommended follow-up:
  - Add product acceptance scenarios next, or target metrics/snapshot scale
    aggregation before deeper traffic/compute semantics.

## 2026-07-05 - Frontend Product Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: this commit (created before hash assignment)
- Scope: display backend-derived constellation semantics in the existing
  product control summary without changing frontend architecture.
- Changed files/modules:
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test`
    - Result: passed, 22 files / 84 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - No product logic or protocol changes were needed; the frontend consumed
    optional backend summary fields.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - This was a bounded UI hardening step, not a full visual redesign.
- Recommended follow-up:
  - Add reproducible product acceptance scenarios, then use screenshots/manual
    QA for a broader visual polish pass.

## 2026-07-05 - Product Acceptance Scenarios v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: this commit (created before hash assignment)
- Scope: add deterministic product acceptance scenarios and runtime smoke tests
  for 72, 300, and 1200 satellite configurations.
- Changed files/modules:
  - `configs/acceptance/small_demo_72sat.yaml`
  - `configs/acceptance/medium_demo_300sat.yaml`
  - `configs/acceptance/scale_demo_1200sat_short.yaml`
  - `docs/product_acceptance_scenarios.md`
  - `tests/integration/test_product_acceptance_scenarios.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_product_acceptance_scenarios.py -q`
    - Result: passed, 4 tests. Runtime was about 90 seconds because the
      1200-satellite acceptance smoke executes a live tick.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py tests/integration/test_runtime_session_control.py tests/integration/test_orbit_batch_scale.py tests/unit/test_position_driven_network_engine.py tests/unit/test_metrics_module.py tests/unit/test_backend_derived_summary.py tests/integration/test_product_acceptance_scenarios.py -q`
    - Result: passed, 67 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test`
    - Result: passed, 22 files / 84 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - `metrics_mode`, traffic mix, and compute-service mix are documented as
    derived product semantics rather than loader fields, so the YAML files stay
    compatible with the existing SEES config schema.
  - The active local runtime config files remain modified and excluded.
- Known remaining issues:
  - The 1200 acceptance smoke is intentionally not a fast unit test. It is a
    product-level smoke and should stay in targeted/acceptance validation
    rather than every tight edit loop.
- Recommended follow-up:
  - Use these scenarios as stable fixtures for the next scale-mode metrics and
    snapshot aggregation task.

## 2026-07-04 - Scale Firebreak v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `a9c8acd`
- Scope: reduce orbit event explosion for large constellations by adding
  scale-safe batch orbit updates without changing Event Kernel ordering.
- Changed files/modules:
  - `src/leo_twin/schema/domain.py`
  - `src/leo_twin/schema/events.py`
  - `src/leo_twin/schema/config.py`
  - `src/leo_twin/schema/config_loader.py`
  - `src/leo_twin/models/orbit/`
  - `src/leo_twin/models/network/engine.py`
  - `src/leo_twin/models/network/position_engine.py`
  - `src/leo_twin/services/control/runtime.py`
  - `src/leo_twin/services/metrics/collector.py`
  - `examples/integration_demo/`
  - `tests/integration/test_orbit_batch_scale.py`
  - `tests/unit/test_module_contracts.py`
- Validation:
  - `python -m pytest tests/integration/test_orbit_batch_scale.py tests/unit/test_module_contracts.py tests/unit/test_orbit_module.py tests/unit/test_keplerian_orbit.py -q`
    - Result: passed, 23 tests.
  - `python -m pytest tests/unit/test_metrics_module.py tests/unit/test_position_driven_network_engine.py -q`
    - Result: passed, 29 tests.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py tests/integration/test_runtime_session_control.py -q`
    - Result: passed, 18 tests.
  - `python -m pytest tests/integration/test_config_control.py::test_frontend_control_messages_are_processed tests/unit/test_integration_demo_scenario.py::test_demo_scenario_uses_configured_orbit_parameters tests/integration/test_orbit_batch_scale.py -q`
    - Result: passed, 9 tests.
  - `python -m pytest -q`
    - Result: failed only on local runtime/config baseline drift:
      `configs/sees_control.yaml` has `satellite_count=120` where the test
      expects 72, and `configs/generated_full_system_demo.json` has
      `satellite_count=120` where the test expects 6.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test`
    - Result: passed, 22 files / 78 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Direct `pnpm --dir frontend test` could not find `node` from the system
    PATH, so the bundled Codex Node and pnpm paths were used.
  - Full `pytest` in the active working tree is still affected by the two
    pre-existing local runtime/generated config modifications. These files
    remain excluded from the task scope and will not be submitted.
  - Initial frontend scenario config exposed `orbit_update_mode: None`, which
    broke exact compatibility assertions. The key is now omitted unless
    explicitly configured.
- Known remaining issues:
  - Large-scale batch mode reduces orbit event volume but still computes
    network geometry in-process for each satellite; this is a scale
    firebreak, not distributed execution or a network model rewrite.
- Recommended follow-up:
  - Add a frontend-facing scale/fidelity summary so users can see when the
    backend automatically selected batch orbit updates and aggregated metrics.

## 2026-07-05 - Network KPI Dynamics v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `cdc455f`
- Scope: make dashboard network KPI curves consume backend-owned effective
  flow-level metrics for throughput, latency, loss proxy, and jitter proxy.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/unit/test_metrics_module.py`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py -q`
    - Result: passed, 10 tests.
  - `python -m pytest tests/unit/test_metrics_module.py tests/integration/test_full_system_demo.py::test_replay_test tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 12 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 22 files / 107 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The current model is still flow-level only, so loss and jitter must remain
    documented deterministic proxies instead of packet-level measurements.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The KPI proxy can show pressure-driven loss/jitter when enough completed
    flow evidence exists, but it is not a high-fidelity transport simulator.
  - More realistic latency and throughput still require a later bounded traffic
    demand and transport model enrichment task.
- Recommended follow-up:
  - Add backend-generated time-series KPI samples so the dashboard can plot
    actual per-tick metric history instead of deriving chart points from the
    latest summary.

## 2026-07-05 - Backend KPI Time-Series v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `ee4c4ce`
- Scope: expose backend-owned bounded KPI time series to runtime status and
  make the data dashboard prefer true backend samples over frontend envelope
  interpolation.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/state/snapshot_engine/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/unit/test_metrics_module.py`
  - `tests/integration/test_runtime_session_control.py`
  - `frontend/tests/dataPanel.test.ts`
  - `frontend/tests/renderPerformance.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 12 tests.
  - `python -m pytest tests/integration/test_full_system_demo.py::test_replay_test tests/integration/test_live_runtime_streaming.py::test_http_cursor_batches_return_incremental_events tests/integration/test_live_runtime_streaming.py::test_live_stream_reads_do_not_run_until_idle tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 4 tests.
  - `python -m pytest tests/integration/test_full_domain_pipeline_v1.py tests/integration/test_generated_full_system_demo.py::test_generated_full_system_demo_runs_domain_lifecycle tests/integration/test_generated_full_system_demo.py::test_generated_full_system_demo_is_deterministic -q`
    - Result: passed, 4 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts renderPerformance.test.ts`
    - Result: passed, 22 files / 110 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The first live runtime tick can process orbit events before network or
    compute KPI samples exist, so `kpi_time_series_v1` returns a deterministic
    current-summary baseline sample when the bounded sample window is empty.
  - The frontend test file contains historical Chinese mojibake in existing
    strings, so new assertions avoid exact localized duration labels where the
    label itself is not the behavior under test.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - `kpi_time_series_v1` is still flow-level and summary-derived; it is not a
    packet trace or high-fidelity transport measurement.
  - Compute chart samples currently use FP32 GFLOPS used; later work should add
    GPU FP32/FP16, NPU INT8, memory, and storage time-series channels.
- Recommended follow-up:
  - Add a bounded traffic-demand pressure model so backend KPI series changes
    under configurable data-transfer, telemetry, downlink, and compute-service
    mixes instead of only reacting to route/link/task events.

## 2026-07-05 - Traffic Demand KPI Binding v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `76b5c87`
- Scope: preserve originating flow demand on route outputs and use route demand
  in metrics pressure proxies so configured flow demand affects backend KPI
  summaries and time-series samples.
- Changed files/modules:
  - `src/leo_twin/schema/domain.py`
  - `src/leo_twin/models/network_engine.py`
  - `src/leo_twin/models/network/engine.py`
  - `src/leo_twin/models/network/routing.py`
  - `src/leo_twin/models/network/datalink.py`
  - `src/leo_twin/models/network/transport.py`
  - `src/leo_twin/models/network/position_engine.py`
  - `src/leo_twin/models/compute/network_aware.py`
  - `src/leo_twin/services/metrics/collector.py`
  - `examples/integration_demo/replay.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/core/decoder/index.ts`
  - `docs/product_contracts.md`
  - `tests/unit/test_metrics_module.py`
  - `tests/unit/test_network_engine.py`
  - `tests/unit/test_network_routing_runtime.py`
  - `tests/unit/test_product_contracts.py`
  - `frontend/tests/eventDecoder.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_network_engine.py tests/unit/test_position_driven_network_engine.py tests/unit/test_network_routing_runtime.py tests/unit/test_network_datalink_runtime.py tests/unit/test_network_transport_runtime.py tests/unit/test_metrics_module.py -q`
    - Result: passed, 62 tests.
  - `python -m pytest tests/unit/test_product_contracts.py tests/unit/test_integration_demo_scenario.py -q`
    - Result: passed, 17 tests.
  - `python -m pytest tests/integration/test_full_system_demo.py::test_replay_test tests/integration/test_full_system_demo.py::test_frontend_sync_test tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer tests/integration/test_runtime_session_control.py::test_runtime_kpi_series_changes_with_configured_flow_demand tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 5 tests.
  - `python -m pytest tests/integration/test_generated_full_system_demo.py::test_generated_full_system_demo_runs_domain_lifecycle tests/integration/test_generated_full_system_demo.py::test_generated_full_system_demo_is_deterministic tests/integration/test_full_domain_pipeline_v1.py tests/unit/test_product_contracts.py tests/unit/test_integration_demo_scenario.py -q`
    - Result: passed, 21 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- eventDecoder.test.ts dataPanel.test.ts renderPerformance.test.ts`
    - Result: passed, 22 files / 111 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - `FLOW_ARRIVAL` is targeted to network, not metrics, so metrics should not
    observe it directly without changing event contracts. The safer binding is
    to preserve `FlowRequest.demand_capacity` on the resulting `RouteState`.
  - Existing route equality tests needed expected `demand_capacity` values
    because network-generated routes now retain the request demand.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Demand pressure is a flow-level route proxy. It does not model packets,
    queues, RF, retransmissions, or per-hop congestion buffers.
  - Demo traffic generation is still task-coupled and should later move toward
    the reusable traffic demand model for richer traffic classes.
- Recommended follow-up:
  - Replace the hand-built integration demo flow/task burst generator with the
    reusable `leo_twin.models.traffic` demand profiles while keeping the same
    event contracts and deterministic ordering.

## 2026-07-05 - Route Loss KPI Binding v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `a05452a`
- Scope: preserve data-link and transport loss as route-level flow proxies and
  include route loss in backend network KPI loss summaries.
- Changed files/modules:
  - `src/leo_twin/schema/domain.py`
  - `src/leo_twin/models/network/datalink.py`
  - `src/leo_twin/models/network/transport.py`
  - `src/leo_twin/models/compute/network_aware.py`
  - `src/leo_twin/services/metrics/collector.py`
  - `examples/integration_demo/replay.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/core/decoder/index.ts`
  - `docs/product_contracts.md`
  - `tests/unit/test_network_datalink_runtime.py`
  - `tests/unit/test_network_transport_runtime.py`
  - `tests/unit/test_metrics_module.py`
  - `tests/unit/test_product_contracts.py`
  - `tests/integration/test_generated_full_system_demo.py`
  - `frontend/tests/eventDecoder.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_network_datalink_runtime.py tests/unit/test_network_transport_runtime.py tests/unit/test_metrics_module.py tests/unit/test_product_contracts.py -q`
    - Result: passed, 32 tests.
  - `python -m pytest tests/unit/test_network_engine.py tests/unit/test_position_driven_network_engine.py tests/unit/test_network_routing_runtime.py tests/integration/test_runtime_session_control.py::test_runtime_kpi_series_changes_with_configured_flow_demand -q`
    - Result: passed, 40 tests.
  - `python -m pytest tests/integration/test_generated_full_system_demo.py::test_generated_full_system_demo_transport_profile_changes_capacity -q`
    - Result: passed, 1 test.
  - `python -m pytest tests/integration/test_full_system_demo.py::test_replay_test tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 3 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- eventDecoder.test.ts dataPanel.test.ts renderPerformance.test.ts`
    - Result: passed, 22 files / 111 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The first generated-demo integration assertion used a direct `>= 0.1`
    comparison and failed on the expected `0.09999999999999998` floating-point
    representation. The assertion now uses `pytest.approx(0.1)`.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Route `loss_rate` is still a deterministic flow-level proxy derived from
    configured layer profiles; it is not packet-level observed loss.
  - Loss is aggregated at route-summary level. Per-hop or per-medium loss
    decomposition should be a later channel/link observability task.
- Recommended follow-up:
  - Add frontend route detail text for demand pressure and route loss so users
    can see whether loss comes from transport profile, MAC collision profile,
    route blocking, or demand pressure.

## 2026-07-05 - Frontend Route KPI Detail v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `0e4f355`
- Scope: display backend-provided best-route demand and route loss in the
  protocol/link dashboard summary.
- Changed files/modules:
  - `frontend/src/dashboard/link_protocol/LinkProtocolPanel.tsx`
  - `frontend/tests/linkProtocolPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- linkProtocolPanel.test.ts eventDecoder.test.ts dataPanel.test.ts`
    - Result: passed, 22 files / 111 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The PowerShell terminal displays historical Chinese text as mojibake, so
    exact UTF-8 lines were inspected with Python `repr()` before patching.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The current panel shows best-route demand and route loss only. It does not
    yet break loss down into transport, MAC, blocking, and demand-pressure
    components.
- Recommended follow-up:
  - Add a compact route-explanation strip sourced from backend metrics fields:
    demand pressure, route loss, route blocking, and congestion proxy.

## 2026-07-05 - Traffic Demand Generator Integration v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `7aed3ce`
- Scope: make the integration demo initial workload use reusable traffic demand
  records while preserving existing `FLOW_ARRIVAL` and `TASK_ARRIVAL` event
  contracts, event IDs, timing, priorities, and deterministic ordering.
- Changed files/modules:
  - `examples/integration_demo/scenario.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_integration_demo_scenario.py tests/unit/test_traffic_demand_model.py -q`
    - Result: passed, 17 tests.
  - `python -m pytest tests/integration/test_full_system_demo.py::test_replay_test tests/integration/test_full_system_demo.py::test_frontend_sync_test tests/integration/test_config_control.py::test_frontend_control_messages_are_processed tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 4 tests.
  - `python -m pytest tests/integration/test_compute_service_lifecycle.py -q`
    - Result: passed, 1 test.
  - `python -m pytest tests/integration/test_runtime_session_control.py -q`
    - Result: passed, 12 tests.
- Problems encountered:
  - `TrafficDemandBatch.task_arrival_events()` schedules tasks at record
    arrival time, but the integration demo intentionally sends the input flow
    first and the compute task 0.05 seconds later. The demo therefore uses
    `TrafficDemandRecord` as the reusable business record and keeps a local
    projection to the legacy event timing.
  - Payload-level `FlowRequest.application_id`, `FlowRequest.priority`,
    `TaskRequest.flow_id`, and `TaskRequest.priority` were left at their
    previous defaults so this integration slice does not change existing
    frontend/runtime payload compatibility.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The demo workload is now represented by traffic demand records, but it is
    still a single compute-service class. User-selectable traffic mixes should
    be introduced in a later bounded task.
  - Output/result flow metadata is not emitted by this demo integration yet;
    that belongs with the communication-compute lifecycle expansion.
- Recommended follow-up:
  - Add backend configuration fields for traffic class mix and destination type
    so frontend user parameters can drive traffic demand profiles directly.

## 2026-07-05 - Traffic Mix Config v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `8107145`
- Scope: add deterministic traffic class, destination type, and output data
  size configuration across backend config, generated scenario summaries,
  integration demo traffic records, and frontend control payload typing.
- Changed files/modules:
  - `src/leo_twin/schema/config.py`
  - `src/leo_twin/schema/config_loader.py`
  - `src/leo_twin/core/config/schema.py`
  - `src/leo_twin/core/config/__init__.py`
  - `src/leo_twin/services/derived_summary.py`
  - `src/leo_twin/services/scenario_builder.py`
  - `examples/integration_demo/config.py`
  - `examples/integration_demo/scenario.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `tests/unit/test_backend_derived_summary.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `tests/unit/test_scenario_builder.py`
  - `tests/integration/test_config_control.py`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py tests/unit/test_integration_demo_scenario.py tests/unit/test_scenario_builder.py::test_scenario_builder_config_from_sees_config_maps_control_plane_fields tests/integration/test_config_control.py::test_invalid_config_is_rejected tests/integration/test_config_control.py::test_frontend_control_messages_are_processed tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams tests/integration/test_config_control.py::test_system_remains_deterministic_under_config_changes -q`
    - Result: passed, 25 tests.
  - `python -m pytest tests/integration/test_full_system_demo.py::test_replay_test tests/integration/test_full_system_demo.py::test_frontend_sync_test tests/integration/test_runtime_session_control.py tests/integration/test_live_runtime_streaming.py -q`
    - Result: passed, 22 tests.
  - `python -m pytest tests/integration/test_product_acceptance_scenarios.py tests/integration/test_compute_service_lifecycle.py tests/unit/test_traffic_demand_model.py -q`
    - Result: passed, 10 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts appSurface.test.ts`
    - Result: passed, 22 files / 111 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Two read-only subagents inspected the frontend/control-plane path and the
    backend summary/scenario path. Both confirmed the safe v1 boundary is
    config, payload typing, backend summary, and `TrafficDemandRecord`
    metadata; non-compute traffic execution semantics should remain a later
    task.
  - `tests/integration/test_config_control.py::test_config_loads_correctly`
    and
    `tests/unit/test_scenario_builder.py::test_default_generated_scenario_config_file_loads`
    read the locally modified `configs/sees_control.yaml` and
    `configs/generated_full_system_demo.json`; those files are intentionally
    not reset or committed. Targeted tests avoid relying on those local dirty
    baseline files, and the same two tests pass in a clean temporary worktree.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The integration demo still executes a compute-service workload shape. The
    new traffic class and destination type are product semantics and demand
    metadata; true non-compute flow scheduling needs a separate bounded task.
  - Output data size is reported through configuration, backend summary, and
    demand records. Result/output flow emission remains part of the later
    communication-compute lifecycle expansion.
- Recommended follow-up:
  - Add a Traffic Mix Execution v1 task that supports non-compute flow-only
    records and compute-service output metadata without changing Event Kernel
    ordering or introducing packet-level simulation.

## 2026-07-05 - Traffic Mix Execution v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `0139952`
- Scope: make non-compute traffic classes execute as network flow-only
  workloads while preserving compute-service `FLOW_ARRIVAL` + `TASK_ARRIVAL`
  behavior.
- Changed files/modules:
  - `examples/integration_demo/scenario.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `tests/integration/test_full_system_demo.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_full_system_demo.py -q`
    - Result: passed, 6 tests.
  - `python -m pytest tests/unit/test_integration_demo_scenario.py tests/integration/test_config_control.py::test_frontend_control_messages_are_processed tests/integration/test_runtime_session_control.py tests/integration/test_live_runtime_streaming.py -q`
    - Result: passed, 35 tests.
  - `python -m pytest tests/unit/test_backend_derived_summary.py tests/unit/test_traffic_demand_model.py tests/integration/test_compute_service_lifecycle.py -q`
    - Result: passed, 13 tests.
- Problems encountered:
  - The existing full-system demo exact event-count assertion expected
    `21_849`, but the clean `8107145` baseline already produced `23_049`
    events after the previous traffic semantics work. The deterministic test
    baseline was updated to `23_049` after confirming the value in a clean
    temporary worktree.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Non-compute traffic uses deterministic flow-level network routing only. It
    does not create application-specific service endpoints, packet flows, or
    protocol-specific payload models.
  - `COMPUTE_SERVICE` still uses the existing task-offload shape. Output/result
    flow emission remains a later lifecycle task.
- Recommended follow-up:
  - Add dashboard/control explanation text that distinguishes compute-service
    traffic from flow-only telemetry, bulk downlink, and data-transfer traffic.

## 2026-07-05 - Frontend Traffic Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `dbb3151`
- Scope: surface backend-provided traffic semantics in the frontend without
  changing control layout or rendering architecture.
- Changed files/modules:
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts dataPanel.test.ts appSurface.test.ts`
    - Result: passed, 22 files / 111 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The dashboard component currently has helper-focused tests rather than a
    dedicated rendered dashboard assertion. This slice relies on TypeScript
    build and existing app-surface coverage for the dashboard markup change.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The frontend displays the backend-selected traffic class, destination, data
    sizes, and execution shape, but it still does not provide user-facing
    controls for choosing traffic class in the panel.
  - Dashboard traffic display is a compact runtime summary, not a dedicated
    traffic-analysis card.
- Recommended follow-up:
  - Add a small traffic mix control group with segmented traffic-class choices
    and numeric output-data input, reusing the existing backend config fields.

## 2026-07-05 - Frontend Traffic Mix Controls v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `f1909f6`
- Scope: add frontend controls for backend traffic class, destination type, and
  output data size without changing the control architecture.
- Changed files/modules:
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 22 files / 112 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The control panel already had state and payload plumbing from the backend
    config slice, so the UI change was limited to rendering controls and
    adding a deterministic static-markup test.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Destination choices are user-selectable, but compute-service execution
    still uses the backend compute-service workload shape. A later backend
    validation task should prevent incompatible class/destination combinations
    or explain how they are coerced.
- Recommended follow-up:
  - Add backend validation and frontend helper text for traffic-class and
    destination compatibility.

## 2026-07-05 - Traffic Compatibility Guard v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: `c8fb326`
- Scope: make compute-service traffic destination compatibility a backend
  configuration rule and keep the frontend control payload aligned with that
  rule.
- Changed files/modules:
  - `src/leo_twin/schema/config.py`
  - `tests/integration/test_config_control.py`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_config_control.py::test_invalid_config_is_rejected -q`
    - Result: passed, 1 test.
  - `python -m pytest tests/integration/test_config_control.py -k "not test_config_loads_correctly" -q`
    - Result: passed, 9 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 22 files / 113 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - `python -m pytest tests/integration/test_config_control.py -q` still
    fails only in `test_config_loads_correctly` because the local
    `configs/sees_control.yaml` runtime state has `satellite_count: 120`
    while the committed baseline expects `72`. The file is intentionally not
    reset or submitted; the remaining config-control tests pass.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Non-compute destinations remain flexible because only `COMPUTE_SERVICE`
    currently has a hard backend lifecycle dependency on compute nodes.
- Recommended follow-up:
  - Add explicit backend summary wording for unsupported or degraded traffic
    combinations when future traffic classes gain stricter lifecycle rules.

## 2026-07-05 - Traffic Lifecycle Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make traffic execution shape, compatibility constraints, and lifecycle
  notes backend-derived summary fields consumed by the frontend.
- Changed files/modules:
  - `src/leo_twin/services/derived_summary.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `tests/integration/test_config_control.py`
  - `tests/integration/test_full_system_demo.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/configPanel.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py tests/unit/test_integration_demo_scenario.py tests/integration/test_config_control.py::test_frontend_control_messages_are_processed tests/integration/test_full_system_demo.py::test_non_compute_traffic_mix_runs_without_compute_tasks -q`
    - Result: passed, 24 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts dataPanel.test.ts`
    - Result: passed, 22 files / 115 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Two read-only subagents reviewed the backend summary path and frontend
    consumption path. They confirmed the minimal safe scope is
    `backend_summary.traffic_demand_summary` plus frontend display tests, not
    new scenario config fields.
  - The control input area previously showed a frontend-inferred lifecycle
    note. It now shows the backend note only when an initialized generated
    config matches the current controls, otherwise it shows a neutral
    initialization prompt.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The lifecycle notes are explanatory summary fields. They do not implement
    output/result flow scheduling beyond the current metadata.
  - Unknown future traffic classes are displayed from backend labels when
    present; without backend labels the frontend falls back to raw enum values.
- Recommended follow-up:
  - Add a dedicated traffic-analysis dashboard card that charts generated
    traffic class mix, flow completion, and compute-service lifecycle latency
    components over simulation time.

## 2026-07-05 - Network KPI Source Notice v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make the dashboard network KPI chart disclose whether values come
  from backend realtime KPI series, snapshot KPI series, backend metric
  summary, or frontend snapshot estimates.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 22 files / 119 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Read-only KPI source review was started in parallel, but the bounded UI
    change did not need to wait for backend model changes. The implementation
    follows existing frontend telemetry precedence.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This slice explains KPI provenance and proxy fidelity. It does not change
    backend loss, jitter, latency, or throughput equations.
  - When no backend network quality metrics are present, the dashboard still
    falls back to frontend snapshot estimates for display continuity.
- Recommended follow-up:
  - Add a backend metrics provenance summary to runtime status so the UI can
    show exact formula inputs for throughput, latency, loss proxy, and delay
    variation proxy.

## 2026-07-05 - Network KPI Resolver v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: centralize frontend network KPI unit conversion and fallback rules in
  a pure resolver used by dashboard telemetry generation.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 22 files / 122 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - A read-only subagent confirmed backend network KPIs are generated by
    `MetricsCollector._network_quality_summary()` and recommended a frontend
    resolver as the smallest safe step before changing formulas.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The resolver preserves existing formula precedence. It does not make loss,
    jitter, latency, or throughput more realistic by itself.
  - Zero delivered throughput is still treated as incomplete data for display
    and falls back to available/offered capacity, matching the previous UI
    behavior.
- Recommended follow-up:
  - Add backend KPI provenance fields alongside `network_quality_*` so the
    resolver can show formula inputs and distinguish measured flow completion
    from route-capacity estimates.

## 2026-07-05 - Opaque Globe Overlay v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: stop country labels from bypassing globe depth testing so far-side
  labels no longer make the earth look transparent.
- Changed files/modules:
  - `frontend/src/3d/cesium/countryOverlays.ts`
  - `frontend/tests/countryOverlays.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- countryOverlays.test.ts satelliteVisuals.test.ts`
    - Result: passed, 22 files / 123 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The earth material was already opaque and satellite overlays were already
    depth-tested. The visible far-side effect came from country labels using a
    very large `disableDepthTestDistance`, so the bounded fix changes that
    overlay policy to depth-tested labels.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This does not upgrade earth imagery resolution or terrain. It only prevents
    far-side country labels from drawing through the globe.
- Recommended follow-up:
  - Add an explicit globe visual configuration helper that locks imagery,
    atmosphere, depth testing, and optional country overlay modes in one tested
    place.

## 2026-07-05 - Globe Visual Policy v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: centralize Cesium globe opacity, base color, atmosphere, and terrain
  depth-testing policy in a tested frontend helper.
- Changed files/modules:
  - `frontend/src/3d/cesium/globeVisualPolicy.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/tests/globeVisualPolicy.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- globeVisualPolicy.test.ts countryOverlays.test.ts satelliteVisuals.test.ts`
    - Result: passed, 23 files / 125 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Cesium globe settings were previously embedded directly in `CesiumGlobe`.
    The helper keeps behavior the same while making opacity and depth-test
    expectations explicit and testable.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The earth still uses the existing bundled NaturalEarthII texture. This task
    does not download or integrate higher-resolution imagery or terrain.
- Recommended follow-up:
  - Add a high-resolution earth asset task that evaluates local/public-domain
    imagery availability, asset size, attribution, and offline loading behavior.

## 2026-07-05 - Selected Satellite Model v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: keep large-scene satellite model rendering bounded while ensuring the
  currently selected satellite receives a GLB model even when it is outside the
  default model render budget.
- Changed files/modules:
  - `frontend/src/3d/cesium/renderLimits.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/tests/visualLayerLimits.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- visualLayerLimits.test.ts satelliteVisuals.test.ts`
    - Result: passed, 23 files / 128 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The NASA Satellite Kit GLB files are present under
    `frontend/public/assets/nasa-satellite-kit`. The remaining issue was the
    render budget: only the first 32 satellites received GLB models, so a
    selected satellite outside that range could still appear as an icon.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The model budget remains intentionally bounded for large scenes. This does
    not render GLB models for all 1200 satellites.
- Recommended follow-up:
  - Add a selected-satellite visual quality task that improves orientation,
    scale, and panel alignment of the GLB kit during satellite-follow mode.

## 2026-07-05 - Network KPI Provenance v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose backend network KPI source/provenance fields and surface those
  labels in the dashboard KPI source note.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `tests/unit/test_metrics_module.py`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py::test_metrics_collector_reports_effective_flow_level_network_quality tests/unit/test_metrics_module.py::test_metrics_collector_uses_route_loss_rate_for_network_loss_proxy tests/unit/test_metrics_module.py::test_metrics_collector_publishes_backend_kpi_time_series tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 4 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 23 files / 129 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - `RuntimeMetricsSummary` is a flat string/number/bool record, so the
    provenance is intentionally exposed as deterministic flat source and label
    fields instead of nested objects.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This improves KPI explainability, not physical fidelity. The underlying
    loss, jitter, latency, and throughput formulas remain flow-level proxy
    models.
- Recommended follow-up:
  - Add a dashboard details panel that displays the numeric formula inputs:
    route demand, offered capacity, completed flow capacity, route loss,
    congestion proxy, and pressure proxy.

## 2026-07-05 - Network KPI Formula Inputs v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: display backend network KPI formula inputs in the dashboard network
  chart using existing `network_quality_*` runtime metric fields.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 23 files / 131 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Initial frontend validation failed because the new formula input formatter
    referenced a non-existent `formatDecimal` helper. The task now uses a local
    deterministic number formatter shared by Mbps and percentage display.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Formula chips expose scalar backend inputs only. They do not yet show a
    full derivation tree or per-route breakdown.
- Recommended follow-up:
  - Add a route-level KPI detail table for top constrained routes and top
    overloaded links.

## 2026-07-05 - Route KPI Detail Table v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a deterministic dashboard route constraint detail table using
  existing snapshot `Route` and `LinkState` fields.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 23 files / 133 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - A parallel explorer confirmed the existing frontend route/link protocol is
    sufficient for v1. The implementation therefore avoids extending decoder
    contracts or backend payloads in this slice.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The table explains top constrained routes from current snapshots only. It
    does not yet expose backend-owned per-route congestion history or
    overloaded-link time series.
- Recommended follow-up:
  - Add backend route/link constraint summaries so the dashboard can rank
    overloaded links and constrained flows from backend metrics rather than
    relying only on the latest snapshot.

## 2026-07-05 - Backend Route Constraint Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose backend-owned flat route/link constraint summary fields from
  `MetricsCollector.summary()` without changing Event Kernel behavior.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `tests/unit/test_metrics_module.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py -q`
    - Result: passed, 14 tests.
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 1 test.
- Problems encountered:
  - Runtime metrics summaries are flat string/number/bool dictionaries, so this
    task publishes deterministic scalar/string fields instead of nested route
    arrays.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The backend now identifies one top constrained route and one top
    constrained link, but it does not yet emit a ranked list or time-series
    history of overloaded links.
- Recommended follow-up:
  - Bind the dashboard route detail table to these backend summary fields and
    show a backend-source note when constraint summaries are available.

## 2026-07-05 - Frontend Backend Route Constraint Binding v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: bind the dashboard route constraint table to backend
  `network_constraint_*` summary fields, with deterministic snapshot fallback.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 23 files / 134 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - `RuntimeMetricsSummary` already supports flat string/number/bool values, so
    no frontend event type or decoder expansion was needed.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The UI shows one backend top constrained route/link summary. It does not
    yet display a backend-ranked list of multiple constrained routes or links.
- Recommended follow-up:
  - Extend backend summaries to a bounded top-N representation once the runtime
    status contract supports structured route/link constraint rows.

## 2026-07-05 - Selected Satellite Coverage Footprint v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: render a deterministic selected-satellite coverage footprint boundary
  together with the existing bounded honeycomb beam cells.
- Changed files/modules:
  - `frontend/src/3d/beam_renderer/beamEntities.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts visualLayerLimits.test.ts`
    - Result: passed, 23 files / 135 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The existing beam renderer already had selected-satellite honeycomb cells,
    but lacked a larger boundary footprint that made coverage extent visually
    explicit.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This is a deterministic visual footprint only. It is not RF propagation,
    antenna pattern, interference, or link budget simulation.
- Recommended follow-up:
  - Add a coverage legend in the satellite-follow inset that reports footprint
    radius, beam count, and the simplified visual model note.

## 2026-07-05 - Satellite Coverage Legend v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: show selected-satellite coverage radius, beam length, beam count, and
  visual-model note in the satellite-follow inset.
- Changed files/modules:
  - `frontend/src/3d/beam_renderer/beamEntities.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts visualLayerLimits.test.ts`
    - Result: passed, 23 files / 136 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The same beam geometry resolver is now used for both Cesium rendering and
    the inset labels, so the text cannot drift from the visual footprint.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The legend explains the selected-satellite visual approximation only; it
    does not provide RF, antenna, or link-budget fidelity.
- Recommended follow-up:
  - Add a selected-satellite coverage/user intersection panel that reports how
    many visible ground users fall inside the visual footprint.

## 2026-07-05 - Coverage User Intersection v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: count positioned ground users inside the selected satellite's visual
  coverage footprint and show the result in the satellite-follow inset.
- Changed files/modules:
  - `frontend/src/3d/beam_renderer/beamEntities.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts visualLayerLimits.test.ts`
    - Result: passed, 23 files / 137 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Ground-user intersection is intentionally computed against the same visual
    footprint radius used by the selected-satellite beam renderer, so it stays
    consistent with what the user sees.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The count is not an access decision, RF coverage result, antenna pattern,
    or link-budget model. It only explains the current visual footprint.
- Recommended follow-up:
  - Promote coverage/user intersection into a backend-derived observation once
    the coverage model contract is upgraded beyond visual approximation.

## 2026-07-05 - Coverage Summary Transparency v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose backend-owned coverage/beam fidelity and visual-footprint
  intersection policy in the derived summary and frontend configuration
  explanation.
- Changed files/modules:
  - `src/leo_twin/services/derived_summary.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 8 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts satelliteVisuals.test.ts`
    - Result: passed, 23 files / 137 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The existing frontend visual footprint count could be mistaken for an
    access or RF result, so this task makes the backend summary explicitly
    report display-only fidelity and excluded physics.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Coverage/user intersection remains deterministic visual geometry only; no
    RF propagation, antenna pattern, link budget, or interference model is
    introduced in this task.
- Recommended follow-up:
  - Add a backend-owned coverage observation contract before using coverage
    counts for access decisions or KPI calculations.

## 2026-07-05 - Network KPI Semantics v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose backend-owned network KPI proxy semantics and zero-value
  reasons, then render compact caveats in the standalone data dashboard.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `tests/unit/test_metrics_module.py`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py -q`
    - Result: passed, 14 tests.
  - `python -m pytest tests/integration/test_runtime_session_control.py tests/integration/test_generated_full_system_demo.py -q`
    - Result: passed, 21 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 23 files / 139 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Users can interpret zero loss or jitter as real packet-level measurements;
    this task keeps the existing formulas unchanged and adds explicit
    backend-provided proxy semantics and zero-value reasons instead.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Network KPIs remain deterministic flow-level proxy metrics. No packet-level
    loss, jitter, queueing, or protocol emulation is introduced.
- Recommended follow-up:
  - Add a deterministic flow-level demand/route pressure scenario that
    demonstrates non-zero loss and delay-variation proxy values in the default
    dashboard without packet-level simulation.

## 2026-07-05 - Runtime KPI Series Tail Refresh v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: ensure `kpi_time_series_v1` appends or refreshes a current metrics
  summary sample when runtime status is read, so dashboard charts do not keep
  showing stale zero loss/jitter values after backend metrics have advanced.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `tests/unit/test_metrics_module.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py -q`
    - Result: passed, 15 tests.
  - `python -m pytest tests/integration/test_runtime_session_control.py -q`
    - Result: passed, 12 tests.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py -q`
    - Result: passed, 8 tests.
  - Live runtime probe:
    - Result: `metrics_summary` and `kpi_time_series_v1` latest loss/jitter
      values matched after one control step (`0.7` loss proxy and
      `0.026494054645502058` delay-variation proxy).
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 23 files / 139 tests.
- Problems encountered:
  - The metrics summary already had non-zero flow-level loss and delay
    variation proxy values, but `kpi_time_series_v1` could lag behind because
    its sampled tail point was produced before the current summary state.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The KPI values remain flow-level proxies. This task fixes live status
    synchronization only; it does not add packet-level network simulation.
- Recommended follow-up:
  - Add a dashboard-side badge when the latest time-series point is synthesized
    from the current metrics summary rather than from the historical sampling
    interval.

## 2026-07-05 - KPI Tail Source Notice v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add backend and frontend transparency for the `kpi_time_series_v1`
  tail sample source so users can see when the chart tail is synchronized from
  the current metrics summary.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/unit/test_metrics_module.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py tests/integration/test_runtime_session_control.py -q`
    - Result: passed, 27 tests.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py -q`
    - Result: passed, 8 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 23 files / 139 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The dashboard should not silently mix historical samples and a current
    summary tail point, so the backend now exposes `tail_sample_source` and
    `tail_sample_source_label` and the frontend renders the label as a compact
    caveat.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The tail label is descriptive only; the chart still displays flow-level
    proxy metrics rather than packet-level measurements.
- Recommended follow-up:
  - Add a small dashboard control to switch between historical-only KPI series
    and current-summary-tail series for debugging.

## 2026-07-05 - Selected Satellite Resource Meter v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a compact compute-resource load meter to the selected-satellite
  follow inset, using the existing satellite-to-compute-node summary.
- Changed files/modules:
  - `frontend/src/3d/cesium/satelliteFollow.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 23 files / 139 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The selected-satellite inset already had detailed resource labels, but the
    load state was not visually scannable. This task reuses the same summary
    math and adds bounded percentage fields plus a compact meter.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The meter reflects the compute-node snapshot currently associated with the
    selected satellite ID. It does not add a new backend resource scheduler.
- Recommended follow-up:
  - Add a selected-satellite resource history sparkline once backend per-node
    resource samples are exposed as a time series.

## 2026-07-05 - Visualization Layer Effects v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make the visualization layer switches self-explanatory by showing the
  exact 3D layers affected by each switch.
- Changed files/modules:
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts visualLayerLimits.test.ts`
    - Result: passed, 23 files / 140 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The layer switches were already consumed by `visualLayerLimits`, but the UI
    did not tell users what each switch changed. This task adds a deterministic
    explanation map without changing Cesium rendering behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The switches still apply after configuration update/initialization through
    the existing control-plane flow; this task does not add an immediate local
    preview mode.
- Recommended follow-up:
  - Add immediate local preview toggles for 3D-only visibility once control
    state and runtime config updates are separated cleanly.

## 2026-07-05 - Orbit Velocity Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose a simplified circular-orbit velocity estimate in the
  backend-derived constellation summary and frontend configuration
  explanations.
- Changed files/modules:
  - `src/leo_twin/services/derived_summary.py`
  - `tests/unit/test_backend_derived_summary.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 8 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 23 files / 140 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Users can mistake LEO motion for "a few minutes per orbit"; this task keeps
    the existing simplified circular-orbit model and exposes the derived speed
    alongside the orbital period.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This remains a circular-orbit explanatory estimate. It does not add SGP4,
    perturbation modeling, or external ephemeris fidelity.
- Recommended follow-up:
  - Add an orbit explanation tooltip that relates update interval, display
    interpolation, orbital period, and visual motion speed.

## 2026-07-05 - Orbit Motion Explanation v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a deterministic orbit-motion explanation block to the frontend
  configuration panel so users can distinguish backend orbit sample interval,
  simplified circular-orbit speed, orbital period, and display interpolation.
- Changed files/modules:
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 23 files / 142 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Orbit step controls can be mistaken for physical orbital period. This task
    keeps the existing simplified model unchanged and explains that the step is
    a backend sampling interval.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This task does not add high-fidelity orbital mechanics or change Cesium
    interpolation/rendering behavior.
- Recommended follow-up:
  - Add a selected-satellite orbit inspector that shows current angular
    position, period, speed, and next sample time from the runtime stream.

## 2026-07-05 - Selected Satellite Resource Vector Details v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add structured selected-satellite resource-vector rows to the 3D
  satellite follow inset, showing capacity and used values for CPU, GPU, NPU,
  memory, and storage without inventing missing backend usage data.
- Changed files/modules:
  - `frontend/src/3d/cesium/satelliteFollow.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 23 files / 142 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Existing tests used full-object equality for compute summaries. The new
    resource breakdown is additive, so those checks were narrowed to
    `toMatchObject` and a dedicated breakdown assertion was added.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Per-satellite resource history is still not available; this task displays
    only the current snapshot values from the runtime stream.
- Recommended follow-up:
  - Add backend per-node resource time-series samples so the selected-satellite
    inset can show short history sparklines for CPU/GPU/NPU/memory/storage.

## 2026-07-05 - Frontend Surface Sync Status v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a shared topbar sync status pill that shows the frontend display
  time, latest snapshot time, interpolation/snapshot delta, and event count
  across both the 3D control console and dashboard surfaces.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- appSurface.test.ts`
    - Result: passed, 23 files / 144 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Users reported that dashboard/control navigation felt unsynchronized. This
    task does not change stream ownership; it makes the shared display clock and
    snapshot lag visible on both surfaces.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The status pill is a diagnostic display only. It does not persist a backend
    session id across independent browser tabs.
- Recommended follow-up:
  - Add explicit runtime session id and stream cursor diagnostics once the
    backend exposes them in `/runtime/status`.

## 2026-07-05 - Frontend Attach Snapshot Hydration v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: hydrate frontend world state from `/metrics/snapshot` when attaching
  to runtime control state, and carry snapshot-level `event_count` /
  `last_sim_time` into the shared reducer without rolling back newer stream
  events.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/core/decoder/index.ts`
  - `frontend/src/state/reducer/index.ts`
  - `frontend/tests/eventDecoder.test.ts`
  - `frontend/tests/renderPerformance.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- eventDecoder.test.ts renderPerformance.test.ts appSurface.test.ts`
    - Result: passed, 23 files / 145 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Read-only consistency audit showed new dashboard/browser tabs relied on
    stream replay alone for initial runtime baseline. The frontend now applies
    the visible backend snapshot before opening or reattaching streams.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Independent browser tabs still have separate frontend reducer caches; this
    task only hydrates them from the backend visible snapshot.
- Recommended follow-up:
  - Add runtime session id and stream cursor diagnostics to `/runtime/status`
    and display them in the frontend sync pill.

## 2026-07-05 - Network Flow Completion Metrics v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make `PositionDrivenNetworkEngine` emit deterministic flow-level
  `FLOW_COMPLETE` events to metrics after `FLOW_ARRIVAL` routing, using
  `complete` for available routes and `blocked` for unavailable routes.
- Changed files/modules:
  - `src/leo_twin/models/network/position_engine.py`
  - `tests/unit/test_position_driven_network_engine.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_position_driven_network_engine.py -q`
    - Result: passed, 27 tests.
  - `python -m pytest tests/unit/test_metrics_module.py tests/unit/test_position_driven_network_engine.py tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer tests/integration/test_runtime_session_control.py::test_runtime_kpi_series_changes_with_configured_flow_demand -q`
    - Result: passed, 44 tests.
  - `python -m pytest tests/integration/test_runtime_session_control.py -q`
    - Result: passed, 12 tests.
- Problems encountered:
  - The default small demo still produces blocked early flows, so runtime-level
    assertions validate that metrics sees completed flow outcomes rather than
    claiming successful delivered throughput for that scenario.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This remains flow-level completion reporting. It is not packet-level loss,
    jitter, retransmission, or EXATA integration.
- Recommended follow-up:
  - Add a deterministic demo scenario with at least one successful data flow so
    dashboard KPI source switches to `COMPLETED_FLOW_CAPACITY` in an integration
    test.

## 2026-07-05 - Globe Visual Mode Toggle v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a Cesium frontend-only globe display mode toggle with default
  opaque Earth and an explicit translucent observation mode for inspecting
  far-side/through-globe context.
- Changed files/modules:
  - `frontend/src/3d/cesium/globeVisualPolicy.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/globeVisualPolicy.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- globeVisualPolicy.test.ts satelliteVisuals.test.ts`
    - Result: passed, 23 files / 146 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The 3D audit showed the default globe was already opaque; the user need is
    better served by an explicit optional observation mode instead of making the
    default globe transparent.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This is a visual observation toggle only. It does not add terrain, imagery
    fidelity, RF coverage physics, or satellite occlusion semantics.
- Recommended follow-up:
  - Add a Cesium-local layer toolbar for country borders, coverage beams,
    satellite models/icons, and orbit tracks without requiring reinitialization.

## 2026-07-05 - Cesium Local Layer Toolbar v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add frontend-only local 3D layer toggles for the Cesium control view
  so users can immediately show/hide country borders, satellite points/icons,
  satellite models, orbit tracks, coverage beams, ground users, links, and
  routes without reinitializing the scenario.
- Changed files/modules:
  - `frontend/src/3d/cesium/renderLimits.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/visualLayerLimits.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- visualLayerLimits.test.ts satelliteVisuals.test.ts`
    - Result: passed, 23 files / 149 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Existing visualization switches were scenario/config inputs, so changing
    layer visibility during runtime required reinitialization. This task adds a
    local visual-layer state that only reduces existing backend-derived render
    limits and never increases large-scale rendering load.
  - Natural Earth country overlays load asynchronously; the loader now applies
    the current local visibility state after replacing the fallback overlay.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The layer toolbar is a visibility control only. It does not add higher
    fidelity Earth imagery, terrain, RF coverage physics, or packet-level link
    visualization.
- Recommended follow-up:
  - Add a selected-satellite detail drawer backed by backend snapshot fields for
    resource use, current access users, route participation, and recent service
    metrics.

## 2026-07-05 - Selected Satellite Detail Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a frontend 3D control-view summary for the selected satellite,
  using existing backend snapshot fields for orbit state, active links, route
  participation, coverage users, compute load, task counts, and compute
  resource model labels.
- Changed files/modules:
  - `frontend/src/3d/cesium/satelliteDetailSummary.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts visualLayerLimits.test.ts`
    - Result: passed, 23 files / 151 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The prior selected-satellite resource details were mainly visible in the
    satellite-follow inset. This task adds a compact always-available summary in
    the 3D control surface without changing backend protocol or Cesium entity
    load.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The summary is still based on flow-level snapshot aggregates. It does not
    introduce packet-level loss/jitter, RF antenna patterns, or high-fidelity
    link-budget simulation.
- Recommended follow-up:
  - Add backend-emitted per-satellite recent KPI slices so selected satellite
    detail can show recent throughput, latency, loss proxy, compute demand, and
    task lifecycle without frontend-only filtering.

## 2026-07-05 - Selected Satellite Route KPI Proxy v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: extend selected-satellite detail with route-level loss and jitter proxy
  labels derived from related available routes in the backend snapshot, showing
  `--` when there is no supporting route data instead of implying a true zero.
- Changed files/modules:
  - `frontend/src/3d/cesium/satelliteDetailSummary.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 23 files / 151 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Route loss and jitter are available only as flow-level/proxy semantics, not
    packet-level measurements. The UI now labels them explicitly as proxies and
    avoids presenting missing data as zero.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - These values are selected-satellite route proxies, not RF, transport
    retransmission, or packet-level telemetry.
- Recommended follow-up:
  - Add backend per-satellite KPI slice contracts so the dashboard and selected
    satellite detail can share the same semantic source of truth.

## 2026-07-05 - Dashboard Top Compute Nodes v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a high-load compute node table to the standalone data panel so
  users can identify which satellite-hosted compute nodes are overloaded or
  busy, using existing snapshot compute-node fields.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 23 files / 153 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The dashboard already had a global compute pool chart, but it did not expose
    which satellite nodes were consuming resources. The new table is derived
    from snapshot node state and does not change backend protocol.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This is a snapshot ranking, not a backend per-satellite KPI time series.
    It does not yet show recent per-node throughput, task wait time, or service
    lifecycle latency.
- Recommended follow-up:
  - Add backend per-satellite KPI slices for recent network and compute service
    metrics, then bind both dashboard and selected-satellite details to that
    shared source.

## 2026-07-05 - Runtime Satellite KPI Slices v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose a backend-owned `/runtime/status` satellite KPI slice contract
  derived from the metrics collector, covering per-satellite active links,
  route counts, route capacity/demand/latency/loss/jitter proxies, FP32 compute
  load, and task counts. The v1 payload is bounded with
  `mode=TOP_ACTIVITY_LIMITED` and `slice_limit=64`.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `tests/unit/test_metrics_module.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py tests/integration/test_runtime_session_control.py -q`
    - Result: passed, 28 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - MetricsCollector had global running/finished task counts but no per-node
    task count state. This task adds minimal task-to-node counters inside the
    passive metrics collector without changing compute scheduling or event
    ordering.
  - Payload size is bounded to avoid making 1200-node status polling heavy.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The contract is a bounded top-activity slice, not a full 1200-satellite
    per-node telemetry dump.
  - Route loss and jitter remain flow-level proxies, not packet-level metrics.
- Recommended follow-up:
  - Bind `satellite_kpi_slices_v1` into the dashboard top-node table and the
    selected-satellite detail panel, preferring backend slice semantics over
    frontend-only aggregation.

## 2026-07-05 - Dashboard Backend Satellite KPI Binding v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make the standalone dashboard high-load compute-node table prefer
  backend `satellite_kpi_slices_v1` from runtime status, while retaining the
  previous snapshot compute-node aggregation as a fallback.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 23 files / 154 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed after fixing a readonly-array sort type issue by sorting a
      copied array.
- Problems encountered:
  - TypeScript correctly rejected sorting a readonly fallback row array. The
    implementation now sorts `Array.from(sourceRows)` and leaves the pure
    fallback function immutable.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Selected-satellite detail still uses frontend aggregation; it should be
    bound to the same backend slice contract next.
- Recommended follow-up:
  - Pass runtime satellite KPI slices into the Cesium selected-satellite detail
    summary so console and dashboard explain satellite KPIs from one source.

## 2026-07-05 - Console Selected Satellite KPI Binding v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: pass backend `satellite_kpi_slices_v1` into the Cesium control console
  and make selected-satellite details prefer backend slice fields for link
  counts, route capacity/latency/loss/jitter proxies, compute FP32 load, and
  task counts. Snapshot aggregation remains the fallback.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/3d/cesium/satelliteDetailSummary.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts appSurface.test.ts`
    - Result: passed, 23 files / 155 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The Cesium surface did not previously receive runtime status fields, so this
    task passes only the narrow satellite slice object instead of broadening the
    3D component dependency on runtime control state.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Coverage-user containment is still computed from the frontend snapshot; the
    backend slice currently covers network/compute KPIs only.
- Recommended follow-up:
  - Extend backend satellite KPI slices with selected-satellite coverage counts
    or access-user counts once the coverage/access semantics are stable.

## 2026-07-05 - Config Scale Presets v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add one-click scenario scale presets for 72, 300, and 1200 satellites
  in the control panel, setting satellite count, user count, and compute node
  count together so the UI preserves the product rule that satellites are
  compute nodes by default.
- Changed files/modules:
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 23 files / 156 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Numeric inputs were already present next to key sliders, so the higher-value
    control improvement was quick scale presets rather than duplicating inputs.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The presets only set scale counts. They do not yet switch orbit profile,
    traffic class, or fidelity mode labels directly.
- Recommended follow-up:
  - Add preset-specific backend summary text after initialization so users can
    see which fidelity policy and plane allocation the chosen scale produced.

## 2026-07-05 - Launcher HTTP Health Check v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: harden the Windows one-click launcher so it validates backend and
  frontend HTTP readiness, pins frontend Vite to the requested port, starts
  services with deterministic backend host/port arguments, and writes
  diagnostic logs under `artifacts\launcher`.
- Changed files/modules:
  - `scripts/sees_launcher.ps1`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sees_launcher.ps1 status`
    - Result: passed; existing backend and frontend were reported as HTTP
      healthy on `127.0.0.1:8765` and `127.0.0.1:5173`.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 23 files / 156 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - `git diff --check`
    - Result: passed with warnings only for the existing uncommitted
      runtime/generated config files.
- Problems encountered:
  - The previous launcher treated a listening port as ready, which could hide a
    broken frontend or backend HTTP path. The launcher now checks
    `/runtime/status` and the frontend homepage before opening the browser.
  - Vite previously could choose another dev port if the requested one was not
    available. The launcher now starts the frontend with `--strictPort`.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This task validates `status` without restarting the user's currently
    running services. A full restart smoke test should be run when disrupting
    local services is acceptable.
- Recommended follow-up:
  - Add a small native launcher or tray-style command surface if the project
    needs a non-terminal end-user startup experience.

## 2026-07-05 - Scale Preset Backend Explanation v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a compact scale-preset explanation strip to the control panel.
  Before initialization it shows deterministic preset expectations; after a
  matching backend-generated config is available it prefers backend-derived
  constellation and fidelity summaries.
- Changed files/modules:
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 23 files / 159 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - `git diff --check`
    - Result: passed with warnings only for the existing uncommitted
      runtime/generated config files.
- Problems encountered:
  - The first test run expected the full backend model note, but the existing
    summary formatter intentionally truncates long assumptions for compact UI
    cells. The test was updated to assert the existing truncation behavior.
  - The minimal generated-config test fixture needed an `unknown` cast before
    `GeneratedScenarioConfig` because it intentionally included only fields
    relevant to this helper.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The pre-initialization preset text is a frontend explanation. Backend output
    remains the source of truth once initialization returns a generated config.
- Recommended follow-up:
  - Add preset-specific traffic and workload-smoothing explanations once those
    backend summaries are stable across all scale presets.

## 2026-07-05 - Frontend Runtime API Diagnostics v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make frontend runtime API failures visible and actionable by adding a
  Chinese error mapper for backend connection, HTTP, and contract-shape errors,
  then routing App startup, polling, and post-control reload failures through
  that mapper.
- Changed files/modules:
  - `frontend/src/app/api.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/tests/api.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- api.test.ts appSurface.test.ts`
    - Result: passed, 24 files / 163 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - `git diff --check`
    - Result: passed with warnings only for the existing uncommitted
      runtime/generated config files.
- Problems encountered:
  - Previous failed API loads only degraded the connection state, which left the
    user without a concrete recovery action. The new mapper points to the
    one-click launcher and `scripts\sees_launcher.ps1 status`.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - WebSocket transport errors still rely on stream/client lifecycle state and
    console warnings; this task covers HTTP runtime/control-state reload paths.
- Recommended follow-up:
  - Add typed WebSocket connection diagnostics so `/control`, `/stream/events`,
    and `/stream/state` failures produce similarly actionable UI feedback.

## 2026-07-05 - Frontend WebSocket Diagnostics v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add typed connection-issue callbacks for the control WebSocket and
  event/state stream WebSockets, suppress intentional client-close reports, and
  surface unexpected stream/control disconnects as Chinese launcher
  troubleshooting text in the App.
- Changed files/modules:
  - `frontend/src/config_panel/controlClient.ts`
  - `frontend/src/stream/websocket_client/index.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/tests/controlClient.test.ts`
  - `frontend/tests/websocketClient.test.ts`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- controlClient.test.ts websocketClient.test.ts appSurface.test.ts`
    - Result: passed, 24 files / 166 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - `git diff --check`
    - Result: passed with warnings only for the existing uncommitted
      runtime/generated config files.
- Problems encountered:
  - WebSocket close handlers also fire during intentional client shutdown. Both
    clients now keep a local closing flag so teardown does not produce false
    degraded-state feedback.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The diagnostic text is channel-level. It does not yet classify close codes
    into separate user actions.
- Recommended follow-up:
  - Add a compact connection diagnostics row that distinguishes HTTP status,
    control WebSocket, event stream, and state stream health at a glance.

## 2026-07-05 - Frontend Connection Diagnostics Row v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a compact topbar connection diagnostics row for HTTP, control
  WebSocket, event stream, and state stream health. The App now tracks channel
  open/error transitions and renders each channel as idle, connecting, normal,
  or abnormal.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/src/config_panel/controlClient.ts`
  - `frontend/src/stream/websocket_client/index.ts`
  - `frontend/tests/appSurface.test.ts`
  - `frontend/tests/controlClient.test.ts`
  - `frontend/tests/websocketClient.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- controlClient.test.ts websocketClient.test.ts appSurface.test.ts`
    - Result: passed, 24 files / 167 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - `git diff --check`
    - Result: passed with warnings only for the existing uncommitted
      runtime/generated config files.
- Problems encountered:
  - The previous WebSocket diagnostics only surfaced failures. This task added
    open callbacks so the UI can distinguish live channels from connecting or
    idle channels without inferring from aggregate connection state.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Stream health is still connection-level. It does not yet show cursor lag or
    backpressure per stream.
- Recommended follow-up:
  - Add cursor/backpressure counters to the diagnostics row using backend
    runtime status once those fields are stable.

## 2026-07-05 - Runtime Stream Diagnostics Status v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose backend stream buffer diagnostics through
  `/runtime/status.status.stream_diagnostics_v1`, including event/state cursor
  bounds, retained item counts, drop counts, buffer limits, advance-loop state,
  and tick count. Frontend TypeScript contracts now include the optional field.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_adapter_exposes_cursor_batches -q`
    - Result: passed.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- api.test.ts appSurface.test.ts`
    - Result: passed, 24 files / 167 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - `git diff --check`
    - Result: passed with warnings only for the existing uncommitted
      runtime/generated config files.
- Problems encountered:
  - The first attempted file read used a non-existent `runtime/streaming.py`.
    The actual runtime stream code is split into `stream_buffer.py` and
    `advance_loop.py`.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The frontend connection diagnostics row does not yet render these cursor
    counters; this task only exposes and types the backend contract.
- Recommended follow-up:
  - Bind `stream_diagnostics_v1` into the topbar diagnostics row so users can
    see cursor lag, retained records, and dropped records without opening logs.

## 2026-07-05 - Frontend Stream Diagnostics Binding v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: bind backend `stream_diagnostics_v1` into the topbar connection
  diagnostics row so event/state stream cells show cursor, retained, and
  dropped record counts when runtime status provides them.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- appSurface.test.ts`
    - Result: passed, 24 files / 168 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - `git diff --check`
    - Result: passed with warnings only for the existing uncommitted
      runtime/generated config files.
- Problems encountered:
  - The diagnostics row needed to remain compact, so cursor details are appended
    to the channel label and rely on existing overflow/ellipsis styling.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The row shows retained and dropped records, but not consumer-side lag per
    browser tab.
- Recommended follow-up:
  - Add a frontend-side stream cursor tracker so the diagnostics row can compare
    backend latest cursor with the browser's last consumed cursor.

## 2026-07-05 - WebSocket Cursor Envelope v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: send cursor batch envelopes on live WebSocket event/state streams and
  make the frontend stream client consume both the new envelope format and the
  legacy array/single-snapshot formats. The main app now tracks browser-side
  consumed cursors for event and state streams, then compares them with backend
  stream diagnostics in the connection diagnostics row.
- Changed files/modules:
  - `examples/integration_demo/server.py`
  - `frontend/src/stream/websocket_client/index.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/tests/websocketClient.test.ts`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- websocketClient.test.ts appSurface.test.ts`
    - Result: passed, 24 files / 170 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_adapter_exposes_cursor_batches -q`
    - Result: passed.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py::test_large_batch_runtime_keeps_snapshot_and_controls_responsive -q`
    - Result: passed.
- Problems encountered:
  - An initial backend validation command referenced a stale test node name and
    pytest reported it was not found. The test file was inspected and the
    correct large-scale runtime responsiveness test was rerun successfully.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - WebSocket state streams now send batch envelopes, but the frontend keeps
    compatibility with legacy single-snapshot messages.
  - Consumer cursor tracking is browser-local stream state, not a server-side
    multi-consumer registry.
- Recommended follow-up:
  - Add a small diagnostics detail surface explaining stream lag, overflow, and
    dropped records in Chinese for non-developer users.

## 2026-07-05 - Stream Diagnostics Explanation v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add Chinese tooltip and accessibility descriptions to the existing
  topbar connection diagnostics so users can understand stream cursor lag,
  retained records, dropped records, and buffer overflow risk without changing
  the frontend layout or backend protocol.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- appSurface.test.ts`
    - Result: passed, 24 files / 170 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The Windows terminal displayed existing UTF-8 Chinese strings as mojibake
    in one command output. Files were reread with UTF-8 encoding before editing,
    and tests confirmed the intended Chinese strings.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The explanation is exposed as hover/title text and aria labels. It is not
    yet a dedicated visible drawer for touch-only users.
- Recommended follow-up:
  - Add an optional compact diagnostics popover if users need visible details
    without relying on hover.

## 2026-07-05 - Dashboard Scale Summary Alignment v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: align the standalone data panel scale label with backend-derived
  constellation and fidelity summaries. The dashboard now shows derived plane
  count, satellites per plane, user count, and backend scale mode, and can fall
  back to runtime fidelity status before generated config is present.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 24 files / 173 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None beyond preserving the existing compact dashboard layout.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The data panel shows the scale mode label, but not yet a full expandable
    explanation of each fidelity policy field.
- Recommended follow-up:
  - Add a small scale/fidelity details popover shared by the control console
    and data dashboard.

## 2026-07-05 - Opaque Globe Policy Hardening v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: harden the Cesium opaque globe policy so switching back from the
  explicit translucent observation mode clears distance-based globe
  translucency fields. This prevents stale transparent-earth settings from
  leaking into the default opaque view.
- Changed files/modules:
  - `frontend/src/3d/cesium/globeVisualPolicy.ts`
  - `frontend/tests/globeVisualPolicy.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- globeVisualPolicy.test.ts`
    - Result: passed, 24 files / 173 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The existing UI already had an explicit translucent observation mode, so
    the fix was constrained to preventing translucency state from persisting
    when the user selects the default opaque mode.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This is a policy-level regression guard. A browser screenshot pass should
    still be used later to visually verify Cesium terrain/imagery behavior on
    the target machine.
- Recommended follow-up:
  - Add an in-app visual smoke check for opaque globe, country overlay, and
    selected satellite model rendering.

## 2026-07-05 - Satellite Model Asset Manifest v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: enrich the bundled NASA Satellite Kit model asset definitions with
  source filenames and SHA-256 manifest values, and extend satellite visual
  tests so model URIs, source metadata, and hash strings are stable. This keeps
  the primary satellite model path explicit and reduces the chance of silently
  falling back to only point markers.
- Changed files/modules:
  - `frontend/src/3d/orbit_renderer/satelliteModelEntities.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 24 files / 173 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The first test attempt used Node `fs`/`crypto` imports to verify file bytes,
    but the frontend TypeScript test scope does not include Node typings and
    the build failed. The test was revised to a frontend-compatible static
    manifest check.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The test validates the manifest fields, not file bytes. A separate
    repo-level Node or PowerShell asset verification script would be better for
    byte-for-byte integrity checks.
- Recommended follow-up:
  - Add a dedicated asset verification script outside the frontend browser
    TypeScript build, then include it in CI or acceptance checks.

## 2026-07-05 - Frontend Asset Verification Script v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a repository-level PowerShell verification script for bundled
  frontend visual assets. The script checks that NASA Satellite Kit GLB files
  exist and match the expected SHA-256 values without adding Node-specific
  imports to frontend TypeScript tests.
- Changed files/modules:
  - `scripts/verify_frontend_assets.ps1`
  - `docs/development_log.md`
- Validation:
  - `powershell -ExecutionPolicy Bypass -File scripts\verify_frontend_assets.ps1`
    - Result: passed, verified 3 frontend visual assets.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 24 files / 173 tests.
- Problems encountered:
  - None. This script is intentionally outside frontend TypeScript compilation
    to keep the browser test/build target free of Node typings.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The script currently covers the bundled satellite GLB assets. Natural Earth
    country overlay verification can be added separately.
- Recommended follow-up:
  - Wire the asset verification script into a broader frontend acceptance
    command after the visual smoke workflow is stable.

## 2026-07-05 - Natural Earth Asset Verification v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: include the bundled Natural Earth 1:110m country boundary GeoJSON in
  the repository-level frontend visual asset verification script. This gives the
  country overlay asset the same existence and SHA-256 guard as the satellite
  GLB files.
- Changed files/modules:
  - `scripts/verify_frontend_assets.ps1`
  - `docs/development_log.md`
- Validation:
  - `powershell -ExecutionPolicy Bypass -File scripts\verify_frontend_assets.ps1`
    - Result: passed, verified 4 frontend visual assets.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- countryOverlays.test.ts`
    - Result: passed, 24 files / 173 tests.
- Problems encountered:
  - None.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The country overlay still depends on Cesium/browser rendering for visual
    confirmation; this task only verifies asset integrity.
- Recommended follow-up:
  - Add browser screenshot checks for opaque globe plus visible country
    boundaries once the in-app browser connector is stable.

## 2026-07-05 - Dashboard Compute Vector Wording v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: clarify standalone dashboard compute-resource wording so FP32 is
  presented as the primary capacity metric, while FP64, GPU FP32/FP16, NPU
  INT8, memory, and storage are explicitly shown as the resource vector. This
  avoids implying that the product only models single-precision compute.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 24 files / 173 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Existing backend and selected-satellite views already expose the resource
    vector; the issue was mostly dashboard wording, so the change stayed
    frontend-only.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The compute time-series chart still tracks FP32-equivalent primary
    consumption. Separate FP64/GPU/NPU time-series can be added later if backend
    publishes per-resource history.
- Recommended follow-up:
  - Add backend time-series samples for compute resource vector dimensions, then
    render them as selectable dashboard series.

## 2026-07-05 - Coverage Beam Semantic Labels v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose backend coverage-beam semantics in the selected-satellite
  local inset. The inset now shows beam pattern, coverage fidelity, and visual
  footprint intersection policy in addition to footprint radius, beam length,
  and bounded honeycomb beam count.
- Changed files/modules:
  - `frontend/src/3d/beam_renderer/beamEntities.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 24 files / 173 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Existing coverage geometry was already bounded and deterministic. The gap
    was missing product-facing labels in the selected-satellite view.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The coverage beam remains a deterministic visual footprint, not RF
    propagation or an antenna-pattern simulation.
- Recommended follow-up:
  - Add a visible selected-satellite coverage legend explaining footprint,
    honeycomb cells, and covered-user counting in one compact panel.

## 2026-07-05 - Satellite Motion Projection Label v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make frontend display-clock satellite motion projection visible in the
  selected-satellite inset. The inset now shows whether the current satellite
  view is snapshot-synchronized or display-projected ahead of the latest backend
  snapshot.
- Changed files/modules:
  - `frontend/src/3d/cesium/positions.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/tests/orbitTrackRenderer.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- orbitTrackRenderer.test.ts`
    - Result: passed, 24 files / 174 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Satellite position projection already existed. The issue was that users had
    no visible indication of display-time extrapolation relative to the latest
    backend snapshot.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This labels projection state; it does not change the simplified circular
    orbit or backend update cadence.
- Recommended follow-up:
  - Add a short movement/fidelity legend near the 3D controls explaining
    backend snapshot cadence versus frontend display interpolation.

## 2026-07-05 - 3D Layer Render Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make the 3D visualization layer toggles explain their effect. The
  control overlay now shows a compact render summary for country boundaries,
  satellite points, icons, GLB models, tracks, coverage beams, users, links, and
  routes, including current visibility and bounded render limits.
- Changed files/modules:
  - `frontend/src/3d/cesium/renderLimits.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/visualLayerLimits.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- visualLayerLimits.test.ts`
    - Result: passed, 24 files / 176 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The change is a UI explanation layer over existing render limits and
    does not change Cesium rendering architecture.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The summary reports configured limits, not actual rendered object counts
    after Cesium pruning.
- Recommended follow-up:
  - Add actual rendered entity counters from the render caches when a visual
    smoke/instrumentation pass is added.

## 2026-07-05 - Runtime KPI Compute Vector Samples v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: extend runtime KPI time-series samples with compute resource vector
  usage fields beyond FP32: CPU FP64, GPU FP32/FP16, NPU INT8, memory, and
  storage. MetricsCollector also emits derived compute resource metric records
  for these used-resource dimensions on compute-node updates.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `frontend/src/core/event_types/index.ts`
  - `tests/unit/test_metrics_module.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py::test_metrics_collector_publishes_backend_kpi_time_series tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 2 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The change reuses existing compute resource summary fields and does
    not alter compute scheduling or Event Kernel behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The dashboard still renders the FP32-equivalent compute time-series as the
    primary chart. The new vector sample fields are available for a later
    selectable multi-resource chart.
- Recommended follow-up:
  - Add dashboard series selectors for CPU FP64, GPU FP32/FP16, NPU INT8,
    memory, and storage usage from `kpi_time_series_v1`.

## 2026-07-05 - Dashboard Compute Vector Tail v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: consume the new runtime KPI compute resource vector fields in the
  standalone data panel. The compute chart now shows the latest KPI tail usage
  for CPU FP64, GPU FP32/FP16, NPU INT8, memory, and storage alongside the FP32
  primary time-series.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 24 files / 178 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The UI remains compatible with older FP32-only KPI samples by hiding
    the vector tail when optional fields are absent.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The main chart is still FP32-primary; the vector values are shown as latest
    tail labels rather than separate trend lines.
- Recommended follow-up:
  - Add a segmented control for selecting FP32, FP64, GPU, NPU, memory, or
    storage trend lines in the compute chart.

## 2026-07-05 - Frontend Visual Verification Script v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a single PowerShell verification script for frontend visual work.
  The script verifies bundled visual assets, runs the relevant globe/dashboard
  frontend test set, and builds the frontend.
- Changed files/modules:
  - `scripts/verify_frontend_visuals.ps1`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; powershell -ExecutionPolicy Bypass -File scripts\verify_frontend_visuals.ps1`
    - Result: passed; verified 4 visual assets, 24 frontend test files / 178
      tests passed, and frontend build passed.
- Problems encountered:
  - None. The script expects `pnpm` to be available on PATH and reports a clear
    error if it is missing.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The script is still a code-level visual acceptance check; it does not take
    browser screenshots.
- Recommended follow-up:
  - Add optional Playwright screenshot verification once the local browser
    automation path is stable.

## 2026-07-05 - Dashboard Selectable Compute Series v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make the standalone data panel compute chart selectable across backend
  compute resource vector series. The default remains FP32 primary capacity, and
  users can switch the trend line and current KPI to CPU FP64, GPU FP32/FP16,
  NPU INT8, memory, or storage when those backend KPI fields are available.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 24 files / 180 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. Older FP32-only KPI samples remain compatible; optional resource
    vector series fall back to zero until the backend provides those fields.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The chart displays one selected resource series at a time and does not yet
    support multi-axis overlays or side-by-side resource comparison.
- Recommended follow-up:
  - Add a richer compare mode for multiple compute resources after backend
    compute workload semantics are expanded.

## 2026-07-05 - Selected Satellite Resource Detail v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose per-satellite compute resource usage in the 3D control view.
  The selected satellite strip now expands existing backend/snapshot resource
  vectors into deterministic rows for CPU FP32/FP64, GPU FP32/FP16, NPU INT8,
  memory, and storage, with used value, capacity, and utilization bar.
- Changed files/modules:
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/3d/cesium/satelliteDetailSummary.ts`
  - `frontend/src/app/App.css`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 24 files / 181 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The change reuses existing selected-satellite summary data and does
    not alter Cesium entity rendering, backend runtime, or Event Kernel logic.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Runtime satellite KPI slices still expose FP32 scalar load for backend
    slices; per-resource live usage depends on compute-node snapshot vector
    fields being present.
- Recommended follow-up:
  - Add backend per-satellite vector usage slices once compute workload
    lifecycle metrics are expanded beyond FP32.

## 2026-07-05 - Network KPI Acceptance v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add integration acceptance coverage for flow-level network quality
  proxies used by the dashboard. The default integration demo must expose
  non-zero effective loss and delay-variation proxies, and the UDP +
  SLOTTED_ALOHA variant must carry its configured 8% route loss into metrics.
- Changed files/modules:
  - `tests/integration/test_full_system_demo.py`
  - `docs/development_log.md`
- Validation:
  - `PYTHONPATH=src python -m pytest tests/integration/test_full_system_demo.py::test_network_stack_trace_uses_configured_protocols -q`
    - Result: passed, 1 test.
- Problems encountered:
  - Initial ad-hoc inspection command failed because the local Python process
    did not include `src` on `PYTHONPATH`; rerunning with `PYTHONPATH=src`
    confirmed the metrics path and guided the test assertions.
  - No production model code changed; the task records a regression guard for
    existing backend KPI semantics.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This test confirms integration-demo quality proxies, but it does not make
    the model more physically accurate and does not introduce packet-level
    loss or jitter simulation.
- Recommended follow-up:
  - Add route-quality scenario presets that let users deliberately choose
    low-load, congested, lossy, or high-variation network conditions from the
    control panel without changing the Event Kernel.

## 2026-07-05 - Network Quality Presets v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add user-facing network quality presets to the configuration panel.
  The presets drive existing backend-consumed fields only: flow demand,
  application/transport protocol, transport loss, congestion window, routing
  protocol, MAC protocol, and routing cost weights. Presets cover stable
  low-load, congested demand, lossy access, and high delay-variation scenarios.
- Changed files/modules:
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 24 files / 182 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The presets reuse existing control-plane payload fields and do not
    add backend schema, protocol-stack logic, packet-level simulation, or Event
    Kernel changes.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Preset names are frontend affordances; backend summaries do not yet echo a
    selected preset id because no new backend field was introduced.
- Recommended follow-up:
  - Add backend-derived route-quality summary fields once the product contract
    needs to persist preset provenance across sessions.

## 2026-07-05 - Ten Hour Plan Progress Update v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: update the 10-hour product enrichment plan with the issue-sized
  slices already delivered and pushed in this thread, mapping recent commits to
  the original suggestions and hour-based task flow.
- Changed files/modules:
  - `docs/ten_hour_product_enrichment_plan.md`
  - `docs/development_log.md`
- Validation:
  - `git diff --check`
    - Result: passed; only the pre-existing uncommitted runtime/config files
      produced CRLF warnings and were excluded from the commit scope.
- Problems encountered:
  - None. This is documentation-only and does not change runtime behavior,
    frontend rendering, backend models, or Event Kernel logic.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The plan progress section is a snapshot of the latest delivered slices; it
    should be updated again after future multi-hour development batches.
- Recommended follow-up:
  - Promote the remaining high-value gaps into issue-sized tasks before the
    next implementation batch.

## 2026-07-05 - Runtime Contract Fixture v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a frontend runtime-status contract fixture and decoder test for
  fields consumed by the console and dashboard. The fixture covers runtime
  status, generated config, fidelity summary, KPI time series, satellite KPI
  slices, stream diagnostics, and compute resource summary fields.
- Changed files/modules:
  - `frontend/src/app/api.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 185 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The task exports the existing runtime status decoder for direct
    testing and does not change backend payload shape or Event Kernel behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The fixture is static; it should be regenerated or updated when backend
    runtime contracts intentionally change.
- Recommended follow-up:
  - Add a backend-side fixture generation command once runtime contract
    versioning is formalized.

## 2026-07-05 - Satellite KPI Slice Resource Vector v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: extend backend runtime satellite KPI slices with compute resource
  vector fields for CPU FP64, GPU FP32/FP16, NPU INT8, memory, and storage. The
  selected-satellite detail summary can now build resource rows from backend
  satellite KPI slices when a compute-node snapshot is not present.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/3d/cesium/satelliteDetailSummary.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `tests/unit/test_metrics_module.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `PYTHONPATH=src python -m pytest tests/unit/test_metrics_module.py::test_metrics_collector_publishes_satellite_kpi_slices tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 2 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 185 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. MetricsCollector remains a read-only observation service; the change
    adds optional summary fields and does not alter compute scheduling,
    runtime advancement, or Event Kernel behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Satellite KPI slices still report current aggregate resource usage only;
    they do not yet provide per-satellite history windows.
- Recommended follow-up:
  - Add bounded per-satellite resource sparkline samples for the selected
    satellite after runtime sampling policy is formalized.

## 2026-07-05 - Ten Hour Plan Progress Update v2

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: update the 10-hour product enrichment plan execution progress with
  the newly delivered runtime contract fixture and satellite KPI slice resource
  vector commits.
- Changed files/modules:
  - `docs/ten_hour_product_enrichment_plan.md`
  - `docs/development_log.md`
- Validation:
  - `git diff --check`
    - Result: passed; only the pre-existing uncommitted runtime/config files
      produced CRLF warnings and were excluded from the commit scope.
- Problems encountered:
  - None. Documentation-only update; no runtime, frontend rendering, backend
    model, or Event Kernel behavior changed.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Plan progress still needs periodic updates as more 10-hour batch tasks
    land.
- Recommended follow-up:
  - Continue with selected-satellite resource sparkline samples or visual
    screenshot acceptance once the next implementation slice starts.

## 2026-07-05 - Selected Satellite Resource Sparkline v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a bounded frontend observation history for the currently selected
  satellite's backend-derived/snapshot-derived compute utilization and render a
  compact sparkline in the selected satellite strip. The history resets when
  the selected satellite changes and remains local to the control view.
- Changed files/modules:
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/3d/cesium/satelliteDetailSummary.ts`
  - `frontend/src/app/App.css`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 25 files / 186 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. This is a local frontend visual slice and does not change backend
    payload shape, runtime advancement, or Event Kernel behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The sparkline is a bounded frontend observation history, not a backend-owned
    per-satellite resource time-series contract.
- Recommended follow-up:
  - Add backend-owned per-satellite resource history samples once runtime
    sampling policy and retention limits are formalized.

## 2026-07-05 - Satellite KPI History v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a backend-owned bounded `satellite_kpi_history_v1` runtime status
  field sourced from satellite `COMPUTE_NODE_UPDATE` observations. The 3D
  control view now prefers backend-provided selected-satellite resource history
  and keeps the frontend-local sparkline history as a compatibility fallback.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/3d/cesium/satelliteDetailSummary.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `tests/unit/test_metrics_module.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `PYTHONPATH=src python -m pytest tests/unit/test_metrics_module.py::test_metrics_collector_publishes_bounded_satellite_kpi_history tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 2 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- satelliteVisuals.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 187 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. This is an observability/status-contract extension. It does not
    change Event Kernel ordering, runtime advancement, compute scheduling, or
    network model behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - `satellite_kpi_history_v1` records bounded resource samples from
    `COMPUTE_NODE_UPDATE`; it is not yet a full communication-compute lifecycle
    trace with network input/output latency components.
- Recommended follow-up:
  - Add route-quality provenance labels or end-to-end reset/route-switch smoke
    coverage before broadening lifecycle history.

## 2026-07-05 - Network Quality Provenance v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose structured `network_quality_provenance_v1` in runtime status
  and let the data panel prefer this backend-owned provenance object when
  explaining throughput, latency, loss, and delay-variation proxy sources. The
  existing scalar `metrics_summary` fields remain for backward compatibility.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `PYTHONPATH=src python -m pytest tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 1 test.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 188 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The change only structures existing flow-level proxy provenance and
    keeps packet-level simulation explicitly disabled.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The network KPI values remain flow-level deterministic proxies; this task
    improves transparency, not physical or packet-level fidelity.
- Recommended follow-up:
  - Add screenshot-based visual acceptance for the 3D console/dashboard or a
    durable reset/route-switch smoke test.

## 2026-07-05 - Dashboard Attach Progress Smoke v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a frontend regression test that locks the intended route-switch
  behavior: dashboard/control surface changes are treated as ATTACH, do not
  reset local stream state, and do not roll back the shared display progress
  clock while the backend runtime is already running.
- Changed files/modules:
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- appSurface.test.ts`
    - Result: passed, 25 files / 189 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. This is a test-only guard for existing route attach/progress behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This is a unit-level frontend guard, not a browser-driven end-to-end smoke
    test against a running backend.
- Recommended follow-up:
  - Add Playwright/browser smoke coverage for initialize, start, dashboard
    switch, pause, stop, and reset once the local launcher is stable.

## 2026-07-05 - Frontend Visual Verification Scope v2

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expand `scripts/verify_frontend_visuals.ps1` so the frontend visual
  verification entry point also runs the runtime status contract fixture and
  dashboard attach progress tests. This keeps visual, dashboard, and
  frontend-backend contract guards together in one command.
- Changed files/modules:
  - `scripts/verify_frontend_visuals.ps1`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_frontend_visuals.ps1`
    - Result: passed; verified 4 frontend visual assets, 25 frontend test files
      / 189 tests, and frontend build.
- Problems encountered:
  - None. The script extension only adds existing tests to the verification
    target and does not change application runtime behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The script remains a code-level visual and contract verification command;
    it does not capture browser screenshots or pixel baselines.
- Recommended follow-up:
  - Add optional browser screenshot checks once the local service launcher and
    browser smoke workflow are stable enough for repeatable CI-style runs.

## 2026-07-05 - Service Latency Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: aggregate existing communication-compute lifecycle `service.*`
  `METRIC_SAMPLE` records into scalar metrics summary fields for input network
  latency, compute queue delay, compute execution delay, output network
  latency, and total service latency. This exposes lifecycle components through
  the existing metrics summary path without adding packet-level simulation or
  changing the compute/network lifecycle model.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `tests/integration/test_compute_service_lifecycle.py`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `PYTHONPATH=src python -m pytest tests/integration/test_compute_service_lifecycle.py tests/unit/test_metrics_module.py::test_metrics_collector_publishes_bounded_satellite_kpi_history -q`
    - Result: passed, 2 tests.
  - `PYTHONPATH=src python -m pytest tests/unit/test_metrics_module.py -q`
    - Result: passed, 17 tests.
- Problems encountered:
  - None. The collector only observes existing `METRIC_SAMPLE` payloads and
    does not schedule new simulation work or modify Event Kernel behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The dashboard does not yet render a dedicated communication-compute
    lifecycle card from these summary fields.
- Recommended follow-up:
  - Add a compact dashboard lifecycle panel or KPI row for service component
    latency once the UI placement is agreed.

## 2026-07-05 - Dashboard Service Latency Components v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: bind the dashboard to the backend `service_latency_*` metrics summary
  fields by adding a compact communication-compute service latency block inside
  the compute resource panel. The block shows service sample counts, complete
  closed-loop counts, total latency, and input-network/queue/execution/output
  component latency values.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 191 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The UI only renders the block when backend service latency samples
    exist, so scenarios without compute-service lifecycle samples stay compact.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The service latency display is a compact dashboard block, not a dedicated
    drill-down view with per-service trace rows.
- Recommended follow-up:
  - Add selected service trace rows once backend exposes bounded per-service
    lifecycle histories.

## 2026-07-05 - Runtime Contract Service Latency Fixture v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: extend the frontend runtime status contract fixture with
  `service_latency_*` metrics summary fields and assert the service latency
  model, task count, and total latency in the contract test.
- Changed files/modules:
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_frontend_visuals.ps1`
    - Result: passed; verified 4 frontend visual assets, 25 frontend test files
      / 191 tests, and frontend build.
- Problems encountered:
  - None. This is a fixture/test contract update only.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The fixture is representative, not generated from a live server command.
- Recommended follow-up:
  - Add a fixture generation/update command once runtime contract versioning is
    formalized.

## 2026-07-05 - Service Latency History Contract v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose a bounded `service_latency_history_v1` runtime status field
  derived from the existing communication-compute service latency components
  tracked by `MetricsCollector`. The field is sorted deterministically and
  limited to recent service items so future UI trace rows can consume it safely.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `tests/integration/test_compute_service_lifecycle.py`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `PYTHONPATH=src python -m pytest tests/integration/test_compute_service_lifecycle.py tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 2 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 191 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The first lifecycle test expectation used a shortened task id; the actual
    traffic demand id is `svc-00-compute_service-00000-task`. The test was
    corrected to assert the deterministic product id.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The dashboard does not yet render per-service trace rows from
    `service_latency_history_v1`; it currently displays aggregate components.
- Recommended follow-up:
  - Add bounded dashboard service trace rows with task id, complete state, and
    component latencies.

## 2026-07-05 - Dashboard Service Trace Rows v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: bind `service_latency_history_v1` into the dashboard by showing a
  bounded set of per-service trace labels in the compute resource panel. Rows
  include compact task id, complete/partial status, and total latency, while
  preserving the full task id as the element title.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 192 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The rows render only when `service_latency_history_v1` provides
    items, preserving compact dashboard behavior for scenarios without service
    traces.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The trace rows are compact labels, not an expandable lifecycle table.
- Recommended follow-up:
  - Add a dedicated service lifecycle drill-down when more per-service metadata
    such as input/output flow ids is exposed to the frontend.

## 2026-07-05 - Service Trace Metadata v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: carry existing service `METRIC_SAMPLE` tag metadata into
  `service_latency_history_v1`, including input flow id, output flow id, input
  route id, and output route id. The dashboard trace row title now exposes
  these ids while keeping the visible row compact.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/integration/test_compute_service_lifecycle.py`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `PYTHONPATH=src python -m pytest tests/integration/test_compute_service_lifecycle.py -q`
    - Result: passed, 1 test.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 192 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The collector reads existing MetricRecord tags and does not alter
    RouteAwareComputeEngine or network behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Trace rows remain compact labels; no expandable detail table exists yet.
- Recommended follow-up:
  - Add a dedicated lifecycle details table or drawer once service traces carry
    timestamps and per-component status.

## 2026-07-05 - Service Trace Timing v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: carry first and last service metric observation simulation times into
  `service_latency_history_v1`. The dashboard trace row title exposes the
  bounded observation window while preserving the compact row layout.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/integration/test_compute_service_lifecycle.py`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `PYTHONPATH=src python -m pytest tests/integration/test_compute_service_lifecycle.py -q`
    - Result: passed, 1 test.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 192 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - A first frontend test attempt failed because the plain shell `PATH` did not
    expose `node`; the same test command passed after prepending the bundled
    Codex Node/Pnpm paths.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The timestamps are service metric observation bounds, not per-component
    start/end timeline records.
- Recommended follow-up:
  - Add a lifecycle detail table with per-component timing when the backend
    emits component-level start/end observations.

## 2026-07-05 - Service Trace Detail v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose component-level service trace samples inside
  `service_latency_history_v1`. Each trace item now carries a deterministic
  `component_timeline` with component name, metric name, sample simulation
  time, duration, route id, and available input/output flow ids. The dashboard
  keeps the compact trace row layout and appends the component timeline to the
  hover title.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/integration/test_compute_service_lifecycle.py`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `PYTHONPATH=src python -m pytest tests/unit/test_metrics_module.py::test_service_latency_history_includes_sorted_component_timeline tests/integration/test_compute_service_lifecycle.py -q`
    - Result: passed, 2 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 192 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - A parallel read-only explorer noted that `component_timeline` and
    `duration_s` better describe the new contract than the initial local
    `components`/`latency_s` draft; the implementation was adjusted before
    commit.
  - The implementation is passive metrics enrichment over existing
    `METRIC_SAMPLE` records and does not alter kernel, network, or compute
    behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The dashboard still renders component details in a hover title rather than
    a dedicated expandable lifecycle table.
- Recommended follow-up:
  - Add a bounded lifecycle detail table or drawer with component rows when the
    UI has room for a richer service-inspection interaction.

## 2026-07-05 - Dashboard Service Trace Timeline v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: render the backend-provided `service_latency_history_v1`
  `component_timeline` as visible compact stage chips in the dashboard compute
  panel. The existing service trace row remains in place, and legacy runtime
  status packets without component timelines still render as before.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 193 tests.
  - Bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\node\bin;<codex-runtime>\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The UI uses the existing backend contract and does not infer service
    timing semantics locally.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The timeline is a compact stage-chip row, not an interactive drill-down
    drawer with filtering or per-service expansion.
- Recommended follow-up:
  - Add a browser-driven dashboard smoke test that verifies service timeline
    rendering against a mocked runtime status response.

## 2026-07-05 - Frontend Visual Verification Runtime Path v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: harden `scripts/verify_frontend_visuals.ps1` so it can run when
  `pnpm.cmd` is available from a bundled runtime but `node.exe` is not already
  on `PATH`. The script now detects a sibling `node\bin\node.exe` under the
  same dependency root and prepends it before invoking frontend tests.
- Changed files/modules:
  - `scripts/verify_frontend_visuals.ps1`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - Bundled runtime PATH without bundled Node:
    `$env:PATH='<codex-runtime>\dependencies\bin;C:\Windows\System32;C:\Windows;C:\Windows\System32\WindowsPowerShell\v1.0'; powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_frontend_visuals.ps1 -SkipBuild`
    - Result: passed; verified 4 frontend visual assets and 25 frontend test
      files / 193 tests.
- Problems encountered:
  - None. This is a developer-experience hardening step for the existing visual
    verification script.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - If neither `pnpm` nor the bundled runtime `pnpm.cmd` is discoverable on
    `PATH`, the script still fails fast with an actionable message.
- Recommended follow-up:
  - Add a broader one-command local dev launcher that starts backend/frontend
    services and runs smoke checks without requiring manual command assembly.

## 2026-07-05 - Launcher Dashboard Surface v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make the Windows launcher more direct for dashboard-first workflows.
  `scripts/sees_launcher.ps1` now accepts `-OpenSurface console|dashboard`,
  opens `/dashboard` when requested, and prints both console and dashboard URLs
  from `status`.
- Changed files/modules:
  - `scripts/sees_launcher.ps1`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sees_launcher.ps1 status -OpenSurface dashboard`
    - Result: passed; reported healthy backend/frontend on local ports and
      printed both `http://127.0.0.1:5173` and
      `http://127.0.0.1:5173/dashboard`.
- Problems encountered:
  - None. This is a launcher/UI workflow improvement and does not alter runtime
    services or simulation behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The launcher remains PowerShell/Windows oriented; there is no cross-platform
    dev-service manager yet.
- Recommended follow-up:
  - Add a smoke command that verifies initialize/start/pause/reset after the
    launcher reports both services healthy.

## 2026-07-05 - README Local Workflow v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make the repository landing page point users to the supported Windows
  launcher, dashboard URL, backend runtime status URL, launcher logs, and
  frontend visual/dashboard verification script.
- Changed files/modules:
  - `README.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sees_launcher.ps1 status -OpenSurface dashboard`
    - Result: passed; confirmed the documented console/dashboard URLs are
      reported by the launcher.
  - `git diff --check`
    - Result: passed, with only the pre-existing local runtime config CRLF
      warnings.
- Problems encountered:
  - None. This is documentation alignment with existing launcher behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - README intentionally stays concise and links to the launcher path rather
    than documenting every backend/frontend endpoint.
- Recommended follow-up:
  - Add a short troubleshooting table for occupied ports and missing Python or
    pnpm once launcher smoke tests are formalized.

## 2026-07-05 - Runtime Health Smoke Script v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a read-only local health smoke script for already running services.
  `scripts/smoke_runtime_health.ps1` validates backend `/runtime/status`,
  required runtime/generated summary fields, frontend console URL, and
  standalone dashboard URL without sending control commands or mutating config.
- Changed files/modules:
  - `scripts/smoke_runtime_health.ps1`
  - `README.md`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1`
    - Result: passed; backend `/runtime/status`, frontend console, and
      dashboard returned HTTP success against the local running services.
- Problems encountered:
  - None. The script is read-only and intentionally avoids `/control` commands.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This smoke check verifies service health and contract presence, not
    initialize/start/pause/reset behavior.
- Recommended follow-up:
  - Add an opt-in control smoke test that uses a disposable config path or
    isolated test server so it cannot mutate local runtime configuration.

## 2026-07-05 - Product Acceptance Service Timeline v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: update product acceptance scenarios so service timeline and local
  read-only runtime health smoke are part of the documented acceptance surface.
  The acceptance checks now mention backend `component_timeline` fields and
  dashboard service timeline rendering.
- Changed files/modules:
  - `docs/product_acceptance_scenarios.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `git diff --check`
    - Result: passed, with only the pre-existing local runtime config CRLF
      warnings.
- Problems encountered:
  - None. This is acceptance documentation only.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The acceptance document references smoke/visual verification commands but
    does not yet define a CI job that runs them.
- Recommended follow-up:
  - Add CI or a local aggregate acceptance script for runtime health, frontend
    visual checks, and targeted backend runtime tests.

## 2026-07-05 - Product Acceptance Verification Script v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add `scripts/verify_product_acceptance.ps1`, a local aggregate
  verification command that runs targeted service timeline backend tests,
  frontend visual/dashboard verification, and the read-only runtime health
  smoke check.
- Changed files/modules:
  - `scripts/verify_product_acceptance.ps1`
  - `README.md`
  - `docs/product_acceptance_scenarios.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -SkipBuild`
    - Result: passed; backend targeted tests 2 passed, visual assets 4
      verified, frontend test files 25 / tests 193 passed, and read-only
      runtime health smoke passed.
- Problems encountered:
  - None. The aggregate script keeps runtime health smoke read-only and exposes
    `-SkipBuild` for faster local loops.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The default command runs the frontend build through
    `verify_frontend_visuals.ps1`; CI integration is still a follow-up.
- Recommended follow-up:
  - Add an optional isolated control smoke mode once config mutation can be
    redirected to a temporary path.

## 2026-07-05 - Runtime Health JSON Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add `-JsonSummary` to `scripts/smoke_runtime_health.ps1` so local
  tools and future CI jobs can consume runtime health results as structured
  JSON while preserving the existing human-readable output by default.
- Changed files/modules:
  - `scripts/smoke_runtime_health.ps1`
  - `README.md`
  - `docs/integration_demo.md`
  - `docs/product_acceptance_scenarios.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1`
    - Result: passed; human-readable output unchanged.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1 -JsonSummary`
    - Result: passed; emitted JSON with `ok`, runtime status URL,
      lifecycle state, simulation status, session id, console URL, and
      dashboard URL.
- Problems encountered:
  - None. This remains a read-only smoke check.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - JSON summary does not yet include timing measurements or endpoint latency.
- Recommended follow-up:
  - Add endpoint timing fields if runtime smoke becomes part of performance
    acceptance.

## 2026-07-05 - Runtime Health Endpoint Timing v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: extend `scripts/smoke_runtime_health.ps1` with endpoint latency
  timings for backend `/runtime/status`, frontend console, and frontend
  dashboard. Human-readable output now prints milliseconds, and `-JsonSummary`
  includes `runtime_status_ms`, `console_ms`, and `dashboard_ms`.
- Changed files/modules:
  - `scripts/smoke_runtime_health.ps1`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1`
    - Result: passed; printed endpoint timings.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1 -JsonSummary`
    - Result: passed; emitted JSON timing fields.
- Problems encountered:
  - None. Timing is observational only and does not affect runtime control.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - These timings are local smoke observations, not benchmark-grade performance
    measurements.
- Recommended follow-up:
  - Add threshold checks only after stable local/CI baselines are established.

## 2026-07-05 - Runtime Health Product Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: extend `scripts/smoke_runtime_health.ps1` so the read-only smoke check
  validates backend-derived product summaries, including constellation,
  traffic demand, and compute resource summaries. Human and JSON outputs now
  include satellite count, user count, constellation profile, traffic class,
  and compute node count.
- Changed files/modules:
  - `scripts/smoke_runtime_health.ps1`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1`
    - Result: passed; printed runtime product summary fields.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1 -JsonSummary`
    - Result: passed; emitted product summary fields in JSON.
- Problems encountered:
  - None. The script remains read-only and does not alter runtime configuration.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The smoke check validates presence and reporting, not semantic correctness
    of every backend-derived assumption.
- Recommended follow-up:
  - Add optional expected-value parameters for satellite count, user count, and
    traffic class once acceptance scenarios are selected by script.

## 2026-07-05 - Runtime Health Expected Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add optional expected-value checks to
  `scripts/smoke_runtime_health.ps1` for satellite count, user count, and
  traffic class. Defaults remain non-strict so the smoke script still works for
  ad-hoc local scenarios.
- Changed files/modules:
  - `scripts/smoke_runtime_health.ps1`
  - `docs/integration_demo.md`
  - `docs/product_acceptance_scenarios.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1 -JsonSummary -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed against the local running demo services.
- Problems encountered:
  - None. Expected-value checks are opt-in and read-only.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Expected values are command-line parameters rather than scenario YAML driven.
- Recommended follow-up:
  - Load expected counts from acceptance scenario YAML when acceptance scenario
    selection is automated.

## 2026-07-05 - Product Acceptance Expected Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: pass expected satellite count, user count, and traffic class from
  `scripts/verify_product_acceptance.ps1` into the runtime health smoke script
  so the aggregate acceptance command can validate scenario-scale assumptions.
- Changed files/modules:
  - `scripts/verify_product_acceptance.ps1`
  - `README.md`
  - `docs/product_acceptance_scenarios.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -SkipBuild -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed; backend targeted tests 2 passed, visual assets 4
      verified, frontend test files 25 / tests 193 passed, read-only runtime
      health smoke passed with expected product summary values.
- Problems encountered:
  - None. Expected checks are opt-in and keep the default aggregate command
    scenario-agnostic.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Expected values are still passed manually rather than loaded from an
    acceptance scenario file.
- Recommended follow-up:
  - Add an `-AcceptanceConfig` option that reads expected values from YAML once
    the acceptance config schema is stable enough for script consumption.

## 2026-07-05 - Product Acceptance Config Expectations v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add `-AcceptanceConfig` to `scripts/verify_product_acceptance.ps1`.
  The aggregate acceptance command can now read satellite count, user count,
  and traffic class expectations from acceptance YAML, with explicit CLI
  expected values still able to override the file-derived values.
- Changed files/modules:
  - `scripts/verify_product_acceptance.ps1`
  - `README.md`
  - `docs/product_acceptance_scenarios.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -SkipBuild -AcceptanceConfig configs\acceptance\small_demo_72sat.yaml -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed; acceptance YAML parsing path was exercised while explicit
      expected values matched the currently running local demo.
- Problems encountered:
  - The first implementation used a double-quoted PowerShell here-string for
    Python `-c` code, which stripped Python string quotes in the child process.
    It was fixed by using a single-quoted here-string and Python single-quoted
    literals before commit.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The script reads only the minimal acceptance expectations needed for the
    smoke check; it does not initialize the backend from the YAML.
- Recommended follow-up:
  - Add an isolated acceptance runner that launches a disposable backend using
    the selected YAML before running strict expected-value checks.

## 2026-07-05 - Runtime Health Compute Count Expectation v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: extend runtime health and aggregate acceptance scripts with
  `ExpectedComputeNodeCount`, and read `scenario.compute_nodes` from acceptance
  YAML alongside satellite/user counts.
- Changed files/modules:
  - `scripts/smoke_runtime_health.ps1`
  - `scripts/verify_product_acceptance.ps1`
  - `README.md`
  - `docs/integration_demo.md`
  - `docs/product_acceptance_scenarios.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1 -JsonSummary -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -SkipBuild -AcceptanceConfig configs\acceptance\small_demo_72sat.yaml -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed; backend targeted tests 2 passed, visual assets 4
      verified, frontend test files 25 / tests 193 passed, and runtime smoke
      passed with expected compute node count.
- Problems encountered:
  - None. The new expected value is opt-in and read-only.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Acceptance YAML values are only used as expected smoke values; the running
    backend is not automatically relaunched with that config.
- Recommended follow-up:
  - Add disposable acceptance launch mode before using config-derived expected
    values as strict defaults in CI.

## 2026-07-05 - Dashboard Launcher Batch v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add `dashboard_leo_twin.bat`, a Windows launcher shortcut that starts
  the normal backend/frontend services and opens the standalone dashboard
  surface through `scripts/sees_launcher.ps1 start -OpenSurface dashboard`.
- Changed files/modules:
  - `dashboard_leo_twin.bat`
  - `README.md`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `git diff --check`
    - Result: passed, with only the pre-existing local runtime config CRLF
      warnings.
- Problems encountered:
  - The new batch file was not executed during validation to avoid restarting
    the currently running local backend/frontend services.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The batch file remains Windows-specific, matching the existing launcher
    approach.
- Recommended follow-up:
  - Add a cross-platform launcher once non-Windows development becomes a
    supported workflow.

## 2026-07-05 - Status And Smoke Batch Shortcuts v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add non-destructive Windows batch shortcuts for service status and
  read-only runtime health smoke checks.
- Changed files/modules:
  - `status_leo_twin.bat`
  - `smoke_leo_twin.bat`
  - `README.md`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `cmd /c status_leo_twin.bat`
    - Result: passed; reported backend/frontend health and URLs.
  - `cmd /c smoke_leo_twin.bat`
    - Result: passed; read-only runtime health smoke succeeded.
- Problems encountered:
  - None. Both shortcuts are non-destructive and do not start, stop, or reset
    services.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Windows batch shortcuts duplicate PowerShell entry points for convenience.
- Recommended follow-up:
  - Consider a small launcher menu only if users need a guided interactive
    workflow.

## 2026-07-05 - Interactive Launcher Menu v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add `leo_twin_launcher.bat`, an interactive Windows menu for common
  local operations: start console, start dashboard, status, read-only smoke
  health check, restart, and stop.
- Changed files/modules:
  - `leo_twin_launcher.bat`
  - `README.md`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `cmd /c "echo 3| leo_twin_launcher.bat"`
    - Result: passed; selected the non-destructive status action and reported
      backend/frontend health and URLs.
- Problems encountered:
  - None. Validation used the status path only, so running backend/frontend
    services were not restarted.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The menu is a Windows batch wrapper over the PowerShell launcher, not a GUI
    installer.
- Recommended follow-up:
  - Add a desktop shortcut or packaged launcher only after the dev workflow is
    stable.

## 2026-07-05 - Launcher Acceptance Menu Option v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: extend `leo_twin_launcher.bat` with a product acceptance verification
  menu option that runs `scripts/verify_product_acceptance.ps1 -SkipBuild`.
- Changed files/modules:
  - `leo_twin_launcher.bat`
  - `README.md`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `cmd /c "echo 3| leo_twin_launcher.bat"`
    - Result: passed; menu still selected the non-destructive status action and
      reported backend/frontend health and URLs.
- Problems encountered:
  - None. The acceptance option was not executed through the menu in this slice
    to avoid repeating the longer validation path; the underlying script was
    validated in previous slices.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The menu acceptance option uses `-SkipBuild` for fast local feedback; full
    build validation remains available by running the PowerShell script
    directly without `-SkipBuild`.
- Recommended follow-up:
  - Add a second menu option for full acceptance with build only if users ask
    for it.

## 2026-07-05 - Launcher Full Acceptance Menu Option v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: split launcher acceptance verification into two menu options: fast
  product acceptance with `-SkipBuild`, and full product acceptance that also
  runs the frontend build through the aggregate verification script.
- Changed files/modules:
  - `leo_twin_launcher.bat`
  - `README.md`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `cmd /c "echo 3| leo_twin_launcher.bat"`
    - Result: passed; menu still selected the non-destructive status action and
      reported backend/frontend health and URLs.
- Problems encountered:
  - None. The full acceptance option was not executed through the menu in this
    slice; the underlying full script path remains available directly.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Menu validation still uses a non-destructive status selection rather than
    executing every menu branch.
- Recommended follow-up:
  - Add a dry-run mode for menu branch validation if batch menu complexity
    increases.

## 2026-07-05 - Launcher Troubleshooting Guide v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add `docs/launcher_troubleshooting.md` covering common local launcher
  failures and non-destructive checks for frontend blank page, dashboard not
  opening, stuck controls, occupied ports, missing Node/Pnpm, dashboard-first
  startup, logs, and read-only smoke validation.
- Changed files/modules:
  - `docs/launcher_troubleshooting.md`
  - `README.md`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `git diff --check`
    - Result: passed, with only the pre-existing local runtime config CRLF
      warnings.
- Problems encountered:
  - None. This is documentation for existing launcher and smoke-check behavior.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The guide is local Windows focused because the current launcher is
    PowerShell/batch based.
- Recommended follow-up:
  - Add screenshots or a short GIF once the UI stabilizes further.

## 2026-07-05 - Runtime Config Staging Guard v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add `scripts/check_no_runtime_config_staged.ps1`, a commit-safety
  helper that fails when `configs/generated_full_system_demo.json` or
  `configs/sees_control.yaml` are staged.
- Changed files/modules:
  - `scripts/check_no_runtime_config_staged.ps1`
  - `README.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_no_runtime_config_staged.ps1`
    - Result: passed; no runtime/local config files were staged.
- Problems encountered:
  - None. The script only inspects staged files.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The guard is manual and not installed as a Git hook.
- Recommended follow-up:
  - Add this guard to the aggregate acceptance command or a pre-commit hook if
    the team wants automated enforcement.

## 2026-07-05 - Product Acceptance Staging Guard v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: run `scripts/check_no_runtime_config_staged.ps1` at the start of
  `scripts/verify_product_acceptance.ps1` so aggregate acceptance fails before
  tests if local runtime config files are staged.
- Changed files/modules:
  - `scripts/verify_product_acceptance.ps1`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -SkipBuild -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed; guard reported no staged runtime/local config files,
      backend targeted tests 2 passed, frontend visual tests 193 passed, and
      runtime health smoke passed.
- Problems encountered:
  - None. The guard only inspects staged files and leaves dirty local runtime
    configs untouched.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The guard is enforced by the aggregate script, not by Git itself.
- Recommended follow-up:
  - Add a pre-commit hook installer only if the team wants local Git hook
    enforcement.

## 2026-07-05 - Launcher Status Hints v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make `scripts/sees_launcher.ps1 status` print the non-destructive
  smoke shortcut and dashboard launcher shortcut alongside service URLs.
- Changed files/modules:
  - `scripts/sees_launcher.ps1`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `cmd /c status_leo_twin.bat`
    - Result: passed; status output includes backend/frontend health, console
      URL, dashboard URL, smoke shortcut, and dashboard launcher shortcut.
- Problems encountered:
  - None. This is status output only.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Status output does not inspect browser state; it only checks backend and
    frontend HTTP health.
- Recommended follow-up:
  - Keep browser-level smoke checks separate so status remains fast and
    non-invasive.

## 2026-07-05 - Runtime Health Frontend Shell Check v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make `scripts/smoke_runtime_health.ps1` verify that frontend console
  and dashboard URLs return the expected React/Vite application shell, not just
  any HTTP 200 response.
- Changed files/modules:
  - `scripts/smoke_runtime_health.ps1`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1 -JsonSummary -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed; frontend shell checks and expected runtime summary checks
      passed.
- Problems encountered:
  - None. The check is read-only and works against the current Vite shell.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This is still an HTTP shell check, not a browser-rendered Playwright test.
- Recommended follow-up:
  - Add browser-level route smoke once Playwright/browser automation is adopted
    for CI.

## 2026-07-05 - Runtime Health Compute Vector Check v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make runtime health smoke assert that backend compute resource summary
  reports `resource_model=ComputeResourceVector`, and include the resource
  model in human and JSON smoke output.
- Changed files/modules:
  - `scripts/smoke_runtime_health.ps1`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1 -JsonSummary -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed; JSON output included
      `compute_resource_model=ComputeResourceVector`.
- Problems encountered:
  - None. This validates backend summary semantics only.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The smoke check does not yet validate individual CPU/GPU/NPU/memory/storage
    vector capacities.
- Recommended follow-up:
  - Add expected resource-vector dimensions once acceptance configs declare
    them explicitly.

## 2026-07-05 - Runtime Health Constellation Profile Expectation v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add optional `ExpectedConstellationProfile` checks to runtime health
  and aggregate acceptance scripts, so acceptance commands can assert backend
  derived constellation profile names such as `CUSTOM_WALKER`.
- Changed files/modules:
  - `scripts/smoke_runtime_health.ps1`
  - `scripts/verify_product_acceptance.ps1`
  - `README.md`
  - `docs/integration_demo.md`
  - `docs/product_acceptance_scenarios.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1 -JsonSummary -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -SkipBuild -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed; staged runtime config guard, backend targeted tests,
      frontend visual tests, and runtime smoke all passed.
- Problems encountered:
  - None. The new expected value is opt-in.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Acceptance YAML currently does not declare a top-level constellation profile
    field, so profile is usually passed explicitly for local checks.
- Recommended follow-up:
  - Add explicit `constellation_profile` to acceptance YAML if profile checks
    become required in CI.

## 2026-07-05 - Runtime Health Protocol Guard v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: extend runtime health smoke with a hard-constraint guard that fails if
  runtime status JSON contains forbidden `STK`, `EXATA`, `AFSIM`, or `DDS`
  markers. The smoke JSON also reports orbit model, application protocol,
  transport protocol, and routing protocol.
- Changed files/modules:
  - `scripts/smoke_runtime_health.ps1`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1 -JsonSummary -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed; JSON output reported `KEPLERIAN`,
      `TASK_OFFLOAD_FLOW`, `TCP`, and `LINK_STATE`.
- Problems encountered:
  - None. This is read-only contract inspection of runtime status.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The marker guard is a coarse smoke check; architectural bans are still
    primarily enforced by code review and targeted tests.
- Recommended follow-up:
  - Add repository-wide static checks for forbidden simulator/runtime names if
    the project needs CI enforcement.

## 2026-07-05 - Forbidden Runtime Import Guard v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add `scripts/check_forbidden_runtime_imports.ps1` to scan source,
  examples, tests, and frontend code for actual `import`/`from` statements that
  pull in forbidden STK/EXATA/GloMoSim/AFSIM/DDS runtime packages. The guard is
  also run by aggregate product acceptance verification.
- Changed files/modules:
  - `scripts/check_forbidden_runtime_imports.ps1`
  - `scripts/verify_product_acceptance.ps1`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_forbidden_runtime_imports.ps1`
    - Result: passed.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -SkipBuild -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed; aggregate acceptance ran runtime config guard, forbidden
      import guard, backend targeted tests, frontend visual tests, and runtime
      health smoke.
- Problems encountered:
  - The repository contains legitimate forbidden-name strings in reviewer and
    auto-fix rules, so the guard intentionally scans only import/from lines.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The guard catches direct imports, not arbitrary dynamic loading strings.
- Recommended follow-up:
  - Add deeper static analysis only if dynamic plugin loading becomes part of
    the architecture.

## 2026-07-05 - README Guard Commands v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: document the forbidden runtime import guard next to the runtime config
  staging guard in `README.md` so local pre-commit checks are discoverable.
- Changed files/modules:
  - `README.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `git diff --check`
    - Result: passed, with only the pre-existing local runtime config CRLF
      warnings.
- Problems encountered:
  - None. This is documentation only.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The README documents manual guard commands; hook installation is not
    automated.
- Recommended follow-up:
  - Add a single pre-commit aggregate command if more guard scripts are added.

## 2026-07-05 - Full Product Acceptance Verification Run

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: record the latest full aggregate product acceptance verification run
  after launcher, smoke, runtime guard, and service timeline slices.
- Changed files/modules:
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed.
    - Runtime config staging guard: passed.
    - Forbidden runtime import guard: passed.
    - Backend targeted tests: 2 passed.
    - Frontend visual/dashboard tests: 25 files / 193 tests passed.
    - Frontend build: passed.
    - Read-only runtime health smoke: passed.
- Problems encountered:
  - None in this full verification run.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Full verification used the currently running local demo services; it did
    not relaunch an isolated backend from an acceptance YAML.
- Recommended follow-up:
  - Add disposable acceptance launch mode for strict per-scenario verification.

## 2026-07-05 - Current Product Status Summary v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add `docs/current_product_status.md`, a short handoff page covering
  local entry points, acceptance command, latest full local verification result,
  current product signals, and remaining gaps.
- Changed files/modules:
  - `docs/current_product_status.md`
  - `README.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `git diff --check`
    - Result: passed, with only the pre-existing local runtime config CRLF
      warnings.
- Problems encountered:
  - None. This is documentation consolidation only.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The status page is manually maintained; it is not generated from scripts.
- Recommended follow-up:
  - Update the status page after the next substantial backend or frontend
    milestone.

## 2026-07-05 - Pre-Commit Aggregate Checks v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add one local pre-commit verification entry point that aggregates the
  runtime config staging guard, forbidden runtime import guard, and whitespace
  diff check before developers commit.
- Changed files/modules:
  - `scripts/pre_commit_checks.ps1`
  - `README.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pre_commit_checks.ps1`
    - Result: passed.
    - Runtime config staging guard: passed.
    - Forbidden runtime import guard: passed.
    - `git diff --check`: passed, with only pre-existing local runtime config
      CRLF warnings.
- Problems encountered:
  - None.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - This is still a manual command, not an installed Git hook.
- Recommended follow-up:
  - Add an optional hook installer only if the team wants enforced local
    pre-commit behavior.

## 2026-07-05 - Runtime Control Cycle Smoke v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a developer/user smoke command that exercises the existing
  runtime control websocket through INITIALIZE, START, PAUSE, RESUME, STOP,
  and RESET for large-scale-safe 1200-satellite scenarios.
- Changed files/modules:
  - `scripts/smoke_runtime_control_cycle.ps1`
  - `control_smoke_leo_twin.bat`
  - `leo_twin_launcher.bat`
  - `README.md`
  - `docs/launcher_troubleshooting.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_control_cycle.ps1 -JsonSummary`
    - Result: passed.
    - Scenario: 1200 satellites / 20 users / 1200 compute nodes.
    - START advanced simulation time from 0 to 0.58.
    - PAUSE held simulation time at 0.58 across the pause wait.
    - RESUME advanced simulation time to 0.84.
    - STOP returned `STOPPED`.
    - RESET returned lifecycle `INITIALIZED` with `initialized=false`.
  - `cmd /c control_smoke_leo_twin.bat`
    - Result: passed.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1 -ExpectedSatelliteCount 1200 -ExpectedUserCount 20 -ExpectedComputeNodeCount 1200 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed.
- Problems encountered:
  - None during implementation.
  - This smoke intentionally mutates the running backend session and is kept
    separate from the read-only health smoke.
- Known remaining issues:
  - This verifies backend control responsiveness through HTTP/websocket paths;
    it does not click the browser UI.
- Recommended follow-up:
  - Add browser-driven Playwright control smoke when a browser E2E harness is
    introduced.

## 2026-07-05 - Optional Acceptance Control Cycle Gate v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add an explicit aggregate acceptance flag that can run the mutating
  runtime control-cycle smoke after the default product acceptance checks.
- Changed files/modules:
  - `scripts/verify_product_acceptance.ps1`
  - `README.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -SkipBuild -RunControlCycleSmoke -ExpectedSatelliteCount 1200 -ExpectedUserCount 20 -ExpectedComputeNodeCount 1200 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed.
    - Runtime config staging guard: passed.
    - Forbidden runtime import guard: passed.
    - Backend targeted tests: 2 passed.
    - Frontend visual/dashboard tests: 25 files / 193 tests passed.
    - Runtime health smoke: passed for 1200 satellites / 20 users / 1200
      compute nodes.
    - Runtime control-cycle smoke: passed for INITIALIZE, START, PAUSE,
      RESUME, STOP, and RESET.
- Problems encountered:
  - None during implementation.
  - The control-cycle gate is opt-in because it resets the active backend
    session.
- Known remaining issues:
  - The aggregate acceptance still assumes local backend/frontend services are
    already running.
- Recommended follow-up:
  - Add disposable acceptance launch mode for fully isolated scenario checks.

## 2026-07-05 - Current Product Status Refresh v2

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: refresh the current product handoff page with the new control-cycle
  smoke command, optional acceptance gate, and latest 1200-node control
  validation result.
- Changed files/modules:
  - `docs/current_product_status.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `git diff --check`
    - Result: passed, with only pre-existing local runtime config CRLF
      warnings.
- Problems encountered:
  - None. This is documentation-only.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - The status page is still manually maintained.
- Recommended follow-up:
  - Refresh this page after the next backend/frontend product milestone.

## 2026-07-05 - Frontend Pending Control Guard v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: prevent duplicate frontend runtime control commands while a
  `*_PENDING` transition is visible locally, covering start/pause/resume and
  shared initialize/stop/reset buttons.
- Changed files/modules:
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `pnpm --dir frontend test -- configPanel.test.ts`
    - Initial result: environment failure because `node` was not on the current
      shell PATH.
  - `$env:PATH='C:\Users\沈高青\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin;C:\Users\沈高青\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 25 files / 196 tests passed.
  - `$env:PATH='C:\Users\沈高青\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin;C:\Users\沈高青\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin;' + $env:PATH; pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Direct `pnpm` invocation failed until bundled Node was added to PATH; the
    code/tests passed after using the workspace runtime Node path.
- Known remaining issues:
  - This is a frontend guard for duplicate clicks; backend control
    responsiveness is covered separately by `smoke_runtime_control_cycle.ps1`.
- Recommended follow-up:
  - Add browser-driven button-click smoke when a Playwright harness is
    introduced.

## 2026-07-05 - Final 10-Hour Acceptance Checkpoint

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: record the final aggregate verification checkpoint after the frontend
  pending-control guard and runtime control-cycle smoke work.
- Changed files/modules:
  - `docs/current_product_status.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -SkipBuild -RunControlCycleSmoke -ExpectedSatelliteCount 1200 -ExpectedUserCount 20 -ExpectedComputeNodeCount 1200 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed.
    - Runtime config staging guard: passed.
    - Forbidden runtime import guard: passed.
    - Backend targeted tests: 2 passed.
    - Frontend visual/dashboard tests: 25 files / 196 tests passed.
    - Runtime health smoke: passed for 1200 satellites / 20 users / 1200
      compute nodes.
    - Runtime control-cycle smoke: passed for INITIALIZE, START, PAUSE,
      RESUME, STOP, and RESET.
- Problems encountered:
  - None in this final checkpoint.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Browser-driven button-click smoke is still future work.
  - Disposable isolated acceptance launch mode is still future work.
- Recommended follow-up:
  - Add Playwright browser control smoke before the next large frontend control
    refactor.

## 2026-07-05 - Frontend Pending Button Render Test v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a rendered ConfigPanel regression test confirming pending runtime
  control states disable the visible initialize/start/stop/reset buttons.
- Changed files/modules:
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - `$env:PATH='C:\Users\沈高青\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin;C:\Users\沈高青\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin;' + $env:PATH; pnpm --dir frontend test -- configPanel.test.ts`
    - Result: passed, 25 files / 197 tests passed.
- Problems encountered:
  - None during implementation.
- Known remaining issues:
  - This is still jsdom/static-render coverage, not a real browser click test.
- Recommended follow-up:
  - Add Playwright button-click smoke once an E2E harness exists.

## 2026-07-05 - Current Product Status Test Count Refresh

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: update the current product status page after the pending-button
  render regression test increased the frontend test count to 197.
- Changed files/modules:
  - `docs/current_product_status.md`
  - `docs/development_log.md`
- Validation:
  - `git diff --check`
    - Result: passed, with only pre-existing local runtime config CRLF
      warnings.
- Problems encountered:
  - None. This is documentation-only.
- Known remaining issues:
  - The status page is manually maintained.
- Recommended follow-up:
  - Keep test counts synchronized after future frontend test additions.

## 2026-07-05 - Runtime Compute Vector Control Smoke Coverage

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: diagnose and guard the reported UI initialization failure where 72
  satellites with compute resource vector fields returned
  `unknown config update keys`; add opt-in compute-vector coverage to the
  runtime control-cycle smoke and widen its default timeout for 1200-node
  control ACKs.
- Changed files/modules:
  - `scripts/smoke_runtime_control_cycle.ps1`
  - `README.md`
  - `docs/development_log.md`
  - `docs/ten_hour_product_enrichment_plan.md`
- Validation:
  - Direct source-level `DemoControlPlane` probe with 72 satellites and
    compute vector fields:
    - Result: passed, `ok=true`, `satellite_count=72`,
      `compute_gpu_tflops_fp32=2.0`.
  - Running backend probe before restart:
    - Result: failed with `unknown config update keys:
      compute_cpu_gflops_fp64, compute_gpu_tflops_fp16,
      compute_gpu_tflops_fp32, compute_memory_gb, compute_npu_tops_int8,
      compute_storage_gb`, confirming the live process had stale control-plane
      code.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sees_launcher.ps1 restart -OpenSurface console -NoBrowser`
    - Result: backend and frontend restarted.
  - Running backend probe after restart:
    - Result: passed, `ok=true`, `last_action=INITIALIZE`,
      `satellite_count=72`, `compute_gpu_tflops_fp32=2.0`,
      `total_gpu_tflops_fp32=144.0`.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_control_cycle.ps1 -JsonSummary`
    - Result: passed for 1200 satellites / 20 users / 1200 compute nodes with
      `include_compute_vector=false`.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_control_cycle.ps1 -SatelliteCount 72 -UserCount 1000 -ComputeNodeCount 72 -IncludeComputeVector -JsonSummary`
    - Result: passed for 72 satellites / 1000 users / 72 compute nodes with
      `include_compute_vector=true`.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_health.ps1 -ExpectedSatelliteCount 72 -ExpectedUserCount 1000 -ExpectedComputeNodeCount 72 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE`
    - Result: passed.
- Problems encountered:
  - The live backend process was stale relative to the current branch code.
  - A first attempt to put compute-vector fields into the default 1200-node
    smoke made the diagnostic too heavy and caused an HTTP timeout. The final
    script keeps the default 1200 smoke lean and uses `-IncludeComputeVector`
    for the 72-node UI-contract check.
  - Existing runtime/generated config files remain locally modified and are
    intentionally excluded from this commit scope.
- Known remaining issues:
  - Browser may need a refresh if it was open before the service restart.
- Recommended follow-up:
  - Run `scripts\smoke_runtime_control_cycle.ps1 -SatelliteCount 72 -UserCount
    1000 -ComputeNodeCount 72 -IncludeComputeVector` after backend restarts to
    confirm the UI initialization payload is accepted.

## 2026-07-05 - Runtime Completion and Live Dashboard KPI Tail

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make live runtime sessions stop at configured `runtime.duration` and
  keep dashboard KPI/resource-pool displays synchronized with the current
  runtime KPI tail instead of freezing at the previous event sample.
- Changed files/modules:
  - `src/leo_twin/runtime/session.py`
  - `src/leo_twin/runtime/advance_loop.py`
  - `src/leo_twin/services/metrics/collector.py`
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/integration/test_runtime_session_control.py`
  - `tests/integration/test_live_runtime_streaming.py`
  - `tests/unit/test_metrics_module.py`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py tests/integration/test_live_runtime_streaming.py tests/unit/test_metrics_module.py`
    - Result: passed, 42 passed.
  - `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 frontend test files / 200 tests passed.
  - `pnpm --dir frontend build`
    - Result: passed.
  - `python -m pytest`
    - Result: failed after 309 passed / 7 failed. The failures were outside
      this task's changed modules and included local runtime/generated config
      drift (`configs/sees_control.yaml`, `configs/generated_full_system_demo.json`)
      plus existing network/scenario expectation mismatches in tests such as
      `test_full_system_pipeline.py`, `test_network_module_parallel.py`, and
      `test_integration_demo_scenario.py`.
- Problems encountered:
  - A first full-pytest attempt timed out at 184 seconds without failure
    details; a second longer run completed and exposed the unrelated failures
    listed above.
  - The initial frontend test command failed because `node` was not on the
    PowerShell PATH. The Codex bundled Node/pnpm paths were loaded and the
    frontend tests/build then passed.
  - Probe files `tmp_probe_generated.json` and `tmp_probe_sees.yaml` were
    created during diagnosis and removed before staging.
  - Existing local runtime config changes remain intentionally unstaged.
- Known remaining issues:
  - The full backend suite still needs a separate baseline cleanup for the
    unrelated config/scenario expectation failures before it can be used as a
    clean all-green gate in this worktree.
  - Network loss/jitter/throughput remain flow-level proxy metrics, not
    packet-level measurements.
- Recommended follow-up:
  - Add a focused baseline-alignment task for the remaining full-pytest
    failures, starting with the generated config defaults versus fixture
    expectations, then the route demand and constellation summary expectation
    drift.

## 2026-07-05 - Live Advance Empty-Gap Progression Fix

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: fix the live runtime issue where event count could freeze while the
  server-side advance loop kept ticking. The runtime now remembers the last
  requested advance target so bounded live ticks can cross intervals with no
  discrete events instead of repeatedly retrying the same time window.
- Changed files/modules:
  - `src/leo_twin/runtime/session.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py tests/integration/test_live_runtime_streaming.py`
    - Result: passed, 24 passed.
  - `python -m pytest tests/unit/test_metrics_module.py`
    - Result: passed, 19 passed.
  - `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 frontend test files / 200 tests passed.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - Runtime status showed `deterministic_replay=false` and `RUNNING`, but
    `tick_count` kept increasing while recent ticks processed zero events and
    the queue still contained future events. This proved the issue was bounded
    live advancement over an empty event interval, not a precomputed replay
    path.
- Known remaining issues:
  - Event count is still discrete by design and will remain flat between
    scheduled events. The frontend progress clock can move smoothly, but new
    event records only appear when the DES reaches the next event time.
  - Existing local runtime config files remain modified and are intentionally
    excluded from the commit scope.
- Recommended follow-up:
  - Add a runtime diagnostic field for `next_queued_event_sim_time` so the UI
    can explain when event count is flat because the next event is in the
    future.

## 2026-07-05 - Runtime Control and Dashboard Detail Usability

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: align live runtime control semantics and dashboard observability after
  120/1200-satellite UI feedback. Running sessions now reject direct speed and
  mode changes; the frontend locks execution parameters while running; target
  satellite selection covers every satellite in the snapshot; the yellow
  runtime pressure notice is dismissible; the dashboard adds scrollable
  per-user business request and per-satellite resource detail tables.
- Changed files/modules:
  - `src/leo_twin/runtime/session.py`
  - `src/leo_twin/services/control/runtime.py`
  - `tests/integration/test_runtime_session_control.py`
  - `tests/integration/test_config_control.py`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/3d/cesium/CesiumGlobe.tsx`
  - `frontend/src/3d/cesium/satelliteFollow.ts`
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `frontend/tests/appSurface.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py tests/integration/test_config_control.py -k "not test_config_loads_correctly"`
    - Result: passed, 24 passed / 1 deselected.
  - `python -m pytest tests/integration/test_runtime_session_control.py tests/integration/test_config_control.py`
    - Result: failed only on `test_config_loads_correctly` because local
      `configs/sees_control.yaml` currently contains runtime scenario state
      with `satellite_count=120` while the test baseline expects 72.
  - `pnpm --dir frontend exec vitest run configPanel.test.ts appSurface.test.ts dataPanel.test.ts satelliteVisuals.test.ts`
    - Result: passed, 4 files / 133 tests.
  - `pnpm --dir frontend test`
    - Result: passed, 25 files / 206 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The local PowerShell PATH did not expose `node` for Vitest. The Codex
    bundled Node/pnpm paths were used for frontend tests and build.
  - The full target backend command is blocked by intentionally unstaged local
    runtime config drift in `configs/sees_control.yaml`; that file was not
    reset or staged.
- Known remaining issues:
  - Backend full-suite validation in this worktree still needs a separate
    config-baseline cleanup task before `test_config_loads_correctly` can pass
    without excluding the known local runtime config assertion.
  - The new dashboard business request table reflects flow-level route/service
    records already emitted by the backend; it does not introduce packet-level
    request simulation.
- Recommended follow-up:
  - Add backend-owned per-user request lifecycle summaries so the dashboard can
    show request state transitions without deriving them from route paths.

## 2026-07-05 - Five-Hour Upgrade Plan and Dashboard Node Detail v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: start the requested five-hour module refinement flow with a committed
  plan and the first bounded frontend observability task. The standalone
  dashboard page is now the vertical scroll container, user status rows cover
  every known user node even when idle, and satellite rows include service
  object and next-hop context derived from existing route snapshots.
- Changed files/modules:
  - `docs/five_hour_module_upgrade_plan.md`
  - `frontend/src/app/App.css`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend test`
    - Result: passed, 25 files / 207 tests.
  - `pnpm --dir frontend exec vitest run dataPanel.test.ts`
    - Result: passed, 1 file / 53 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The existing standalone dashboard used nested overflow with a hidden parent
    container, which could make the page appear not scrollable. The dashboard
    page now owns vertical scrolling while large tables keep local scroll.
- Known remaining issues:
  - User and satellite node details are still derived from existing snapshot
    paths and runtime KPI slices. A follow-up backend summary contract should
    become the source of truth for request lifecycle, queue state, selected
    satellite, and next-hop semantics.
  - Network KPI time variation is not changed in this task; Hour 4 of the plan
    isolates that work as a backend metrics/model task.
- Recommended follow-up:
  - Implement the detailed user-facing scenario configuration contract and add
    backend-owned per-user request lifecycle summaries.

## 2026-07-05 - User Configuration Surface Contract v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a backend-owned configuration surface summary so the product can
  keep a detailed user-facing config file while the frontend exposes only key
  operational fields. The summary is attached to runtime status and generated
  backend summaries, and a non-runtime template config is added under
  `configs/templates/`.
- Changed files/modules:
  - `src/leo_twin/services/configuration_view.py`
  - `configs/templates/sees_user_detailed.example.yaml`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/scenario.py`
  - `frontend/src/core/event_types/index.ts`
  - `tests/unit/test_configuration_view.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `tests/integration/test_config_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_configuration_view.py tests/unit/test_backend_derived_summary.py tests/unit/test_integration_demo_scenario.py tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 26 tests.
  - `pnpm --dir frontend exec vitest run runtimeContractFixture.test.ts configPanel.test.ts`
    - Result: passed, 2 files / 34 tests.
  - `pnpm --dir frontend test`
    - Result: passed, 25 files / 207 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - `python -m pytest tests/unit/test_configuration_view.py tests/integration/test_config_control.py -q`
    initially hit the known local runtime config drift in
    `configs/sees_control.yaml`: `test_config_loads_correctly` expects
    `compute_nodes=10`, while the local uncommitted runtime state currently has
    `compute_nodes=72`. The file was intentionally not reset or staged.
  - `tests/unit/test_integration_demo_scenario.py` still expected the older
    constellation summary without `orbital_velocity_km_s`. The backend summary
    already emits that field and the frontend consumes it, so the test baseline
    was updated.
- Parallel investigation notes:
  - Configuration entry points are `DemoControlPlane.handle_raw_message()`,
    `RuntimeController.initialize()`, `merge_config_update()`, and
    `ConfigPanel` initialization payload construction.
  - KPI flatness is mainly caused by missing flow-level link occupancy and
    release events; a follow-up network task should add deterministic
    non-packet-level link pressure so latency, jitter, loss, throughput, and
    resource curves vary with simulated load.
- Known remaining issues:
  - The frontend still sends a broad initialization payload. A follow-up should
    make the payload sparse so hidden advanced fields from a detailed config
    file are not overwritten by frontend defaults.
  - The default launcher still starts from `configs/integration_demo.yaml`; a
    future task should add an explicit user config path for detailed scenario
    files instead of treating `configs/sees_control.yaml` as a template.
- Recommended follow-up:
  - Implement frontend sparse initialization payloads and a launcher option for
    a user-selected detailed config file.

## 2026-07-05 - Flow-Level Network Pressure KPI Dynamics v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a deterministic, non-packet-level link pressure model inside
  `PositionDrivenNetworkEngine`. Concurrent flow arrivals now reserve demand
  against touched route links, emit `LinkState.utilization`, apply bounded
  queue-delay and loss proxies to the affected route, and release pressure when
  the flow completes. This gives the existing metrics collector a real backend
  source for non-zero and time-varying latency, jitter, loss, throughput, and
  demand pressure indicators.
- Changed files/modules:
  - `src/leo_twin/models/network/position_engine.py`
  - `tests/unit/test_position_driven_network_engine.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_position_driven_network_engine.py -q`
    - Result: passed, 28 tests.
  - `python -m pytest tests/unit/test_position_driven_network_engine.py tests/unit/test_metrics_module.py::test_metrics_collector_reports_dynamic_network_quality_proxy tests/unit/test_metrics_module.py::test_metrics_collector_publishes_backend_kpi_time_series tests/unit/test_metrics_module.py::test_metrics_collector_kpi_time_series_refreshes_current_tail_sample -q`
    - Result: passed, 31 tests.
  - `python -m pytest tests/integration/test_live_runtime_streaming.py::test_http_cursor_batches_return_incremental_events tests/integration/test_runtime_session_control.py::test_demo_adapter_exposes_cursor_batches tests/integration/test_runtime_session_control.py::test_runtime_kpi_series_changes_with_configured_flow_demand -q`
    - Result: passed, 3 tests.
  - `python -m pytest tests/unit/test_position_driven_network_engine.py tests/unit/test_metrics_module.py tests/integration/test_runtime_session_control.py::test_runtime_kpi_series_changes_with_configured_flow_demand tests/integration/test_runtime_session_control.py::test_demo_adapter_exposes_cursor_batches tests/integration/test_live_runtime_streaming.py::test_http_cursor_batches_return_incremental_events -q`
    - Result: passed, 50 tests.
- Problems encountered:
  - The first implementation subtracted existing protocol `loss_rate` from
    route capacity a second time. `DataLinkRuntime` already folds its own
    efficiency/loss behavior into route capacity, so the pressure model now
    only reduces capacity by the newly introduced pressure loss proxy.
  - An attempted integration test command used stale test names and pytest
    reported `not found`; the actual runtime cursor/KPI tests were located and
    rerun successfully.
- Model limits:
  - This remains flow-level simulation, not packet-level queuing.
  - Pressure is tracked on route links touched by active flows and released on
    flow completion; it does not yet model per-link scheduling disciplines,
    retransmission, interference, or RF-layer loss.
  - Completed flows are still retained in the existing `_active_flows` reroute
    cache for compatibility with current tests; cleanup of completed flow
    lifecycle state should be a separate bounded task.
- Recommended follow-up:
  - Add a backend-owned per-user request lifecycle table so the dashboard can
    show queue state, selected satellite, next hop, and flow/service state
    without deriving those fields from route paths.

## 2026-07-05 - Frontend Sparse Initialization Payload v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: align frontend initialization with the new backend configuration
  surface. `ConfigPanel` now builds an initialization payload through
  `initializationControlPayload()`, sending key operational fields while
  omitting file-only advanced fields such as FP64/FP16/memory/storage details,
  physical channel parameters, and routing weights. The full
  `networkControlPayload()` remains available for explicit advanced update
  paths.
- Changed files/modules:
  - `src/leo_twin/services/configuration_view.py`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_configuration_view.py -q`
    - Result: passed, 2 tests.
  - `pnpm --dir frontend exec vitest run configPanel.test.ts`
    - Result: passed, 1 file / 33 tests.
  - `pnpm --dir frontend test`
    - Result: passed, 25 files / 209 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None in implementation. The main design constraint is that the UI still
    visually contains some advanced controls; this commit only prevents
    initialization from overwriting advanced file-only settings by default.
- Known remaining issues:
  - The frontend layout still needs a true key/basic versus advanced grouping.
  - There is not yet a launcher option to boot from an arbitrary user detailed
    config file.
- Recommended follow-up:
  - Add a visible configuration mode split in the control panel and a backend
    startup option for a user-selected detailed config file.

## 2026-07-05 - Backend Runtime Lifecycle Summaries v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add backend-owned per-user request and per-satellite service
  summaries for the standalone dashboard. Runtime status now includes
  `user_request_summary_v1` and `satellite_service_summary_v1`, built from the
  current backend snapshot plus service latency and satellite KPI summaries.
  The DataPanel prefers these backend summaries and falls back to the existing
  snapshot-derived rows when the backend fields are absent.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/unit/test_runtime_observability.py`
  - `tests/integration/test_runtime_session_control.py`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 2 tests.
  - `pnpm --dir frontend exec vitest run dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 2 files / 58 tests.
  - `python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer tests/integration/test_runtime_session_control.py::test_runtime_kpi_series_changes_with_configured_flow_demand tests/integration/test_live_runtime_streaming.py::test_http_cursor_batches_return_incremental_events -q`
    - Result: passed, 4 tests.
  - `pnpm --dir frontend test`
    - Result: passed, 25 files / 211 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None in implementation. The main design choice was to keep the new
    summary builder pure and snapshot-based so it does not add events or alter
    Event Kernel behavior.
- Known remaining issues:
  - The summaries are flow-level lifecycle summaries. They expose waiting route
    counts and service associations but do not implement packet-level queues,
    retransmission, interference, or RF-layer behavior.
  - The frontend table still formats some backend fields into display labels;
    a later UI pass can localize these labels more cleanly when the control
    panel is split into key/basic and advanced sections.
- Recommended follow-up:
  - Add dashboard filters/sticky table headers and a visible source badge for
    backend lifecycle summaries on the user and satellite detail tables.

## 2026-07-05 - Dashboard Detail Table Filtering v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: improve standalone dashboard observability for medium and large
  scenarios by adding a client-side detail filter above the user-node and
  satellite-resource tables. The filter searches user IDs, satellite IDs,
  selected service paths, destinations, next hops, service labels, and compute
  or network status labels while preserving the backend-owned runtime summary
  as the source data.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend exec vitest run dataPanel.test.ts`
    - Result: passed, 1 file / 57 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The implementation is intentionally display-only and does not
    modify runtime control, Event Kernel behavior, backend summaries, or
    streaming protocols.
- Known remaining issues:
  - Filtering is currently client-side over the rows already provided to the
    table. A later scale pass should add backend pagination or virtualized
    rendering for very large detailed tables.
  - This pass does not add new business generation, network, or compute
    fidelity logic.
- Recommended follow-up:
  - Add a visible backend-summary source badge and then implement bounded
    table virtualization or pagination for 1200-satellite inspection.

## 2026-07-05 - Dashboard Runtime Detail Source Badges v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make standalone dashboard detail tables more transparent by showing
  a visible source badge for user-node and satellite-resource details. The
  badge distinguishes backend-owned runtime summaries, backend-enhanced
  snapshot rows, and pure snapshot fallback rows without changing backend
  runtime contracts or Event Kernel behavior.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend exec vitest run dataPanel.test.ts`
    - Result: passed, 1 file / 58 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. This is a display-only observability task layered on existing
    `sourceLabel` values.
- Known remaining issues:
  - Source badges explain table provenance but do not add backend pagination,
    row virtualization, or new simulation fidelity.
- Recommended follow-up:
  - Add bounded pagination or virtualization for very large satellite detail
    tables, then continue with deeper business and network metric dynamics.

## 2026-07-05 - Runtime Pacing UI Consistency v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: align frontend runtime mode semantics with the backend clock model.
  Real-time mode now presents an effective 1x speed, disables speed-factor
  editing, and normalizes initialization payloads to `speed_factor=1`.
  Accelerated mode preserves the configured speed factor. Control-console,
  3D surface, and standalone dashboard speed displays now use the same
  effective-speed helper. Completed runtime states are displayed explicitly as
  completed instead of being folded into a generic stopped/idle label.
- Changed files/modules:
  - `frontend/src/runtime_display.ts`
  - `frontend/src/config_panel/ConfigPanel.tsx`
  - `frontend/src/app/App.tsx`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/configPanel.test.ts`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend exec vitest run configPanel.test.ts appSurface.test.ts dataPanel.test.ts`
    - Result: passed, 3 files / 123 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The backend clock already ignored `speed_factor` in `REAL_TIME` mode; the
    issue was frontend semantic drift. The fix is limited to display and
    initialization payload normalization.
- Known remaining issues:
  - This pass does not change backend auto-completion logic, which is already
    covered by runtime integration tests. A later UX pass can add an explicit
    completion banner and restart guidance.
- Recommended follow-up:
  - Add a small completion notice on the control console and dashboard, then
    continue with time-varying KPI explanation and larger-table virtualization.

## 2026-07-05 - Runtime Completion Notice v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make runtime completion visible on both the 3D control console and
  standalone dashboard. When backend status or lifecycle state is `COMPLETED`,
  the frontend now shows a distinct completion notice with configured
  duration, final simulation time, processed event count, and reset guidance.
  This is a frontend observability change only; backend runtime completion and
  Event Kernel behavior are unchanged.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend exec vitest run appSurface.test.ts`
    - Result: passed, 1 file / 30 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The notice is derived from existing runtime status fields and does
    not introduce new control actions or backend protocol fields.
- Known remaining issues:
  - The notice does not yet provide a one-click restart flow. Users still use
    the existing reset/initialize/start controls.
- Recommended follow-up:
  - Add bounded table virtualization or pagination for large user/satellite
    detail inspection, then continue with time-varying KPI provenance work.

## 2026-07-05 - Dashboard Detail Pagination v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: reduce standalone dashboard detail-table render pressure in medium
  and large scenarios by adding deterministic client-side pagination windows
  for user-node and satellite-resource details. User details render 80 rows per
  page and satellite details render 120 rows per page; filtering resets both
  tables to the first page while preserving the backend-owned row source.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend exec vitest run dataPanel.test.ts`
    - Result: passed, 1 file / 61 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The pagination helper is pure and deterministic; the UI change is
    limited to the standalone dashboard detail tables.
- Known remaining issues:
  - Pagination is client-side over rows already delivered to the frontend. It
    reduces DOM render pressure but does not reduce backend status payload
    size. Backend pagination or virtualized rendering remains a later scale
    task.
- Recommended follow-up:
  - Add backend row-window APIs or virtualized table rendering if 1200+
    satellite inspection still produces payload or rendering pressure.

## 2026-07-05 - Recent Flow KPI Window v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make dashboard network KPI curves less cumulative/static by adding a
  deterministic recent-flow window to backend KPI samples. The metrics
  collector now records `FLOW_COMPLETE` times and emits 60-second recent
  window fields for delivered throughput, completed flow count, average
  latency, loss proxy, and delay variation. The standalone dashboard prefers
  these recent-window fields when present and falls back to the existing
  effective cumulative fields for compatibility.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/unit/test_metrics_module.py`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py::test_metrics_collector_publishes_backend_kpi_time_series tests/unit/test_metrics_module.py::test_metrics_collector_kpi_time_series_refreshes_current_tail_sample tests/unit/test_metrics_module.py::test_metrics_collector_kpi_time_series_accepts_runtime_sim_time_tail tests/unit/test_metrics_module.py::test_metrics_collector_reports_recent_flow_kpi_window -q`
    - Result: passed, 4 tests.
  - `pnpm --dir frontend exec vitest run dataPanel.test.ts`
    - Result: passed, 1 file / 62 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. The implementation is constrained to Metrics Agent observation state
    and frontend chart selection. It does not alter Event Kernel behavior,
    network routing, or packet-level semantics.
- Known remaining issues:
  - Recent-window throughput is still a flow-level proxy based on completed
    flow capacity in the trailing window. It is not packet throughput,
    retransmission loss, or RF jitter.
- Recommended follow-up:
  - Add visible KPI provenance labels beside the dashboard charts so users can
    distinguish recent-flow proxy metrics from packet-level metrics.

## 2026-07-05 - Dashboard KPI Provenance Labels v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make standalone dashboard network KPI chart semantics explicit. The
  network chart now displays source chips for chart window, throughput,
  latency, loss, jitter, and simulation semantics. The labels are derived from
  backend `network_quality_provenance_v1`, metrics summary source labels, and
  recent-flow KPI sample fields. This makes it clear when curves use the
  recent completed-flow window and that loss/jitter are flow-level proxy
  metrics, not packet-level simulation.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend exec vitest run dataPanel.test.ts`
    - Result: passed, 1 file / 64 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None. This is a frontend interpretability change and does not alter
    backend metrics, Event Kernel behavior, or streaming protocols.
- Known remaining issues:
  - The labels explain existing proxy semantics; they do not implement
    packet-level loss, retransmission, or RF jitter.
- Recommended follow-up:
  - Add per-user business request time-series panels and per-satellite
    resource history selection on the standalone dashboard.

## 2026-07-05 - Dashboard Satellite Resource History v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: connect the standalone dashboard to backend
  `satellite_kpi_history_v1` so users can select a satellite and inspect its
  resource-use history over simulation time. The new panel shows backend
  source/provenance text, load and CPU FP32 trend lines, plus latest memory,
  storage, GPU FP32, and NPU INT8 values. This is a frontend observability
  change only; backend runtime services, protocols, and Event Kernel behavior
  are unchanged.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend exec vitest run dataPanel.test.ts`
    - Result: passed, 1 file / 67 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
  - `pnpm --dir frontend test`
    - Result: passed, 25 files / 229 tests.
- Problems encountered:
  - The first local frontend test invocation failed because the shell PATH did
    not expose `node`. The Codex bundled Node.js and pnpm paths were loaded and
    the same tests were rerun successfully.
  - The initial unit-test expected labels used `s`; the existing UI formatter
    emits Chinese `秒`, so the expectation was corrected to match current
    product display semantics.
- Known remaining issues:
  - The panel displays the bounded history window already emitted by the
    backend. It is not a full archival query or backend-paginated history API.
  - Selection is a standard dropdown over backend-provided history series; a
    searchable selector may be needed when the backend exposes hundreds of
    series.
- Recommended follow-up:
  - Add per-user business/request time-series drilldowns and backend row-window
    APIs for large-scale dashboard inspection.

## 2026-07-05 - User Request History Dashboard v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a backend-owned, bounded `user_request_history_v1` runtime status
  field and display it on the standalone dashboard. The control plane now keeps
  a deterministic per-user recent history window derived from backend
  `user_request_summary_v1`; reset and re-initialization clear old history. The
  dashboard lets users select one user and inspect available routes, network
  queue count, latency, target satellite, primary flow, and loss proxy over
  simulation time. Event Kernel behavior is unchanged.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/integration/test_runtime_session_control.py`
  - `tests/integration/test_live_runtime_streaming.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer tests/integration/test_live_runtime_streaming.py::test_reset_replaces_session_and_clears_stream_buffers -q`
    - Result: passed, 3 tests.
  - `pnpm --dir frontend exec vitest run dataPanel.test.ts`
    - Result: passed, 1 file / 70 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The Codex bundled Python runtime does not include `pytest`, so backend
    validation used the system Python 3.14 interpreter already available on the
    workstation.
- Known remaining issues:
  - `user_request_history_v1` is a recent runtime status window, not a full
    archival query API. It samples status when runtime status is requested.
  - Metrics remain flow-level proxies; no packet-level queueing, RF loss, or
    retransmission model was introduced.
- Recommended follow-up:
  - Move user history sampling into a dedicated observability service if the
    dashboard needs history independent of status polling cadence.
  - Add backend row-window APIs or virtualized tables for large user and
    satellite drilldowns.

## 2026-07-05 - Dashboard Document Scroll v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: make the standalone dashboard route use browser document scrolling
  instead of being visually locked by the global full-screen control-console
  layout. The app now annotates `body[data-frontend-surface]`; the dashboard
  surface switches `body`, `#root`, `.app-shell`, and `.dashboard-page` to
  document-flow scrolling while the 3D control surface keeps the existing
  full-screen locked layout.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/appSurface.test.ts`
  - `docs/development_log.md`
- Validation:
  - `pnpm --dir frontend exec vitest run appSurface.test.ts`
    - Result: passed, 1 file / 31 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
  - `pnpm --dir frontend test`
    - Result: passed, 25 files / 233 tests.
- Problems encountered:
  - None. The change is scoped to frontend layout state and CSS.
- Known remaining issues:
  - Large tables still render client-side rows already present in the runtime
    status payload; backend row-window APIs remain a separate scale task.
- Recommended follow-up:
  - Add visual/manual browser checks for dashboard scrolling at desktop and
    mobile viewports once the next dev server restart is requested.

## 2026-07-05 - Detailed User Config Template Notes v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: strengthen the user-facing detailed SEES configuration template with
  explanatory comments for topology scale, satellite-as-compute-node semantics,
  compute resource vectors, traffic demand, flow-level network proxy metrics,
  scale-safe orbit/space-link policy, runtime pacing, and UI key-control
  boundaries. Template values and loader behavior are unchanged; local runtime
  configs are not touched.
- Changed files/modules:
  - `configs/templates/sees_user_detailed.example.yaml`
  - `tests/unit/test_configuration_view.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_configuration_view.py -q`
    - Result: passed, 2 tests.
- Problems encountered:
  - None. Comments are ignored by the deterministic YAML loader.
- Known remaining issues:
  - The default launcher still starts from the runtime/demo config path. A
    separate import/select workflow is needed if users should load arbitrary
    detailed config files from the UI.
- Recommended follow-up:
  - Add a backend endpoint or CLI workflow for selecting a user-provided
    detailed config file without editing local runtime-generated files.

## 2026-07-05 - Network KPI Component Tail v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: extend backend `kpi_time_series_v1` samples with deterministic
  flow-level network KPI component fields already computed by MetricsCollector:
  route capacity/demand, available demand, demand and throughput pressure,
  route latency, route loss, blocking, failed-flow ratio, congestion, demand
  loss, pressure loss, route/flow/pressure delay variation, effective available
  throughput, and delivered flow capacity. The standalone dashboard now displays
  a latest-sample component tail so users can see whether network KPI changes
  come from demand pressure, route loss, or pressure/jitter proxies. Event
  Kernel and network model behavior are unchanged; this is an observation
  contract enhancement.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/unit/test_metrics_module.py`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py::test_metrics_collector_publishes_backend_kpi_time_series tests/unit/test_metrics_module.py::test_metrics_collector_kpi_time_series_refreshes_current_tail_sample tests/unit/test_metrics_module.py::test_metrics_collector_reports_recent_flow_kpi_window -q`
    - Result: passed, 3 tests.
  - `pnpm --dir frontend exec vitest run dataPanel.test.ts`
    - Result: passed, 1 file / 72 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
  - `pnpm --dir frontend test`
    - Result: passed, 25 files / 235 tests.
- Problems encountered:
  - None. The added fields are copied from existing MetricsCollector summaries
    and do not introduce packet-level simulation.
- Known remaining issues:
  - The dashboard still shows flow-level proxy semantics. It does not model
    packet retransmission, RF fading samples, or queueing at packet granularity.
- Recommended follow-up:
  - Add acceptance scenarios proving KPI component tails vary over time for
    different traffic demand and transport profiles.

## 2026-07-05 - Traffic Generation Summary v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: enrich backend `traffic_demand_summary` with deterministic business
  generation semantics: generated flow count, generated compute task count,
  generated output-flow metadata count, source/destination round-robin policy,
  total input/output data volume, system request rate per minute, and average
  per-user request rate per minute when an arrival interval is available. The
  standalone dashboard now includes these backend-derived semantics in the
  traffic display note. Traffic generation behavior and Event Kernel behavior
  are unchanged.
- Changed files/modules:
  - `src/leo_twin/services/derived_summary.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/unit/test_backend_derived_summary.py`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 8 tests.
  - `pnpm --dir frontend exec vitest run dataPanel.test.ts`
    - Result: passed, 1 file / 73 tests.
  - `pnpm --dir frontend build`
    - Result: passed.
  - `pnpm --dir frontend test`
    - Result: passed, 25 files / 236 tests.
- Problems encountered:
  - None. This is a backend-derived summary and frontend explanation change;
    it does not add packet-level traffic or new config fields.
- Known remaining issues:
  - The product still supports one configured traffic profile at a time through
    the current SEES config. Mixed per-user service portfolios remain a later
    traffic model v2 task.
- Recommended follow-up:
  - Add explicit service-mix configuration fields and deterministic per-user
    demand summaries for DATA_TRANSFER, TELEMETRY, BULK_DOWNLINK, and
    COMPUTE_SERVICE mixes.

## 2026-07-05 - Traffic Service Mix Contract v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a deterministic backend traffic service-mix contract. New
  `TrafficServiceMixItem` and `TrafficServiceMixConfig` types allocate a total
  request count across weighted DATA_TRANSFER, TELEMETRY, BULK_DOWNLINK, and
  COMPUTE_SERVICE items using largest-remainder allocation with deterministic
  tie-breaking, then expand into existing `TrafficDemandProfile` values. The
  generated batch reuses the current flow-level TrafficDemandModel, including
  correlated compute-service input flow, task, and output-flow metadata. This
  does not change SEES config loading, demo defaults, Event Kernel behavior, or
  packet-level semantics.
- Changed files/modules:
  - `src/leo_twin/models/traffic/demand.py`
  - `src/leo_twin/models/traffic/__init__.py`
  - `tests/unit/test_traffic_demand_model.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_traffic_demand_model.py -q`
    - Result: passed, 8 tests.
  - `python -m pytest tests/unit/test_traffic_demand_model.py tests/unit/test_integration_demo_scenario.py tests/integration/test_compute_service_lifecycle.py -q`
    - Result: passed, 23 tests.
- Problems encountered:
  - None. The new contract is additive and reuses existing demand generation.
- Known remaining issues:
  - The SEES YAML control-plane schema still exposes a single traffic profile.
    Wiring this service mix into user-facing config should be a separate task.
- Recommended follow-up:
  - Add SEES config service-mix fields and backend-derived service-mix summary
    once the contract is stable.

## 2026-07-05 - SEES Traffic Service Mix Config Summary v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: wire the deterministic traffic service-mix contract into user-facing
  configuration and backend-derived summaries without changing runtime event
  behavior. `TrafficModel` now accepts flat service-mix weight fields for
  DATA_TRANSFER, TELEMETRY, BULK_DOWNLINK, and COMPUTE_SERVICE. When all
  weights are zero, the backend preserves the existing single `traffic_class`
  behavior. The derived traffic summary now reports service-mix mode, raw
  weights, normalized weights, active service classes, and deterministic
  request-count allocation. Integration demo config conversion and frontend
  data-panel display consume the backend fields.
- Changed files/modules:
  - `src/leo_twin/schema/config.py`
  - `src/leo_twin/schema/config_loader.py`
  - `src/leo_twin/services/derived_summary.py`
  - `src/leo_twin/services/scenario_builder.py`
  - `examples/integration_demo/config.py`
  - `examples/integration_demo/scenario.py`
  - `configs/templates/sees_user_detailed.example.yaml`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/unit/test_backend_derived_summary.py`
  - `tests/unit/test_configuration_view.py`
  - `tests/unit/test_scenario_builder.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `tests/integration/test_config_control.py`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_backend_derived_summary.py tests/unit/test_configuration_view.py tests/unit/test_scenario_builder.py tests/unit/test_integration_demo_scenario.py tests/integration/test_config_control.py -k "not default_generated_scenario_config_file_loads and not config_loads_correctly" -q`
    - Result: passed, 44 tests.
  - `python -m pytest tests/unit/test_backend_derived_summary.py tests/unit/test_configuration_view.py tests/unit/test_scenario_builder.py tests/unit/test_integration_demo_scenario.py tests/integration/test_config_control.py -q`
    - Result: 44 passed, 2 failed due existing local runtime config drift in
      `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`.
      Those files are explicitly excluded from this task and were not modified
      or staged.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 236 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - The normal shell could not find `node`, so frontend validation was rerun
    using the Codex bundled Node/Pnpm path.
  - Two full target backend tests still read local runtime-generated config
    files whose values differ from the repository baseline; per project rule,
    those files were left untouched and unstaged.
- Known remaining issues:
  - The live traffic generator still needs a separate task to consume mixed
    service weights for actual runtime demand generation. This task exposes and
    validates the configuration/summary contract only.
- Recommended follow-up:
  - Connect service-mix weights to deterministic live user demand generation,
    then expose per-user active business state and per-satellite service-load
    summaries in the standalone dashboard.

## 2026-07-05 - Cesium Space Polyline Render Safety v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: fix a frontend Cesium render stop reported as
  `DeveloperError: Expected value to be greater than or equal to 0.0125`.
  The stack trace showed `PolylineGeometry` / `EllipsoidGeodesic`, which means
  space links or routes were being interpreted as ellipsoid geodesic arcs. The
  3D renderer now marks satellite links, business routes, and orbit tracks as
  `ArcType.NONE`, so they render as direct space polylines instead of surface
  arcs. Event Kernel behavior, backend simulation, and country overlays are
  unchanged.
- Changed files/modules:
  - `frontend/src/3d/link_renderer/linkEntities.ts`
  - `frontend/src/3d/orbit_renderer/satelliteEntities.ts`
  - `frontend/tests/satelliteVisuals.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- satelliteVisuals.test.ts`
    - Result: passed, 25 files / 259 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Vite still reports the existing DataPanel chunk-size
      warning at about 502 kB after minification.
  - `git diff --check frontend/src/3d/link_renderer/linkEntities.ts frontend/src/3d/orbit_renderer/satelliteEntities.ts frontend/tests/satelliteVisuals.test.ts docs/development_log.md`
    - Result: passed.
- Problems encountered:
  - The browser stack did not include the application entity id, so the fix was
    derived from the Cesium worker path and from the fact that satellite-space
    lines can connect near-antipodal positions.
  - The first local frontend test invocation failed before running tests because
    `node` was not on PATH. The command was rerun with the bundled Node and
    Pnpm paths prepended.
- Known remaining issues:
  - Country borders still use Cesium's default surface arc behavior. No
    near-antipodal Natural Earth segment was identified as the reported failure
    path in this task.
- Recommended follow-up:
  - Add a Playwright smoke test for large-scale 3D rendering once the local dev
    server lifecycle is stabilized.

## 2026-07-05 - Integration Demo Service Mix Generation v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: connect explicit service-mix weights from `DemoConfig` to the
  integration demo flow-level demand generator. Default zero-weight configs
  keep the existing single `traffic_class` generation path. When one or more
  weights are positive, the demo now uses the existing
  `TrafficServiceMixConfig` / `generate_traffic_service_mix` contract to build
  deterministic DATA_TRANSFER, TELEMETRY, BULK_DOWNLINK, and COMPUTE_SERVICE
  request records. Per-class defaults keep compute traffic user-to-compute,
  telemetry/downlink satellite-to-ground, and data transfer user-to-service.
  Event Kernel behavior and packet-level semantics are unchanged.
- Changed files/modules:
  - `examples/integration_demo/scenario.py`
  - `tests/unit/test_integration_demo_scenario.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_integration_demo_scenario.py tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 24 tests.
  - `python -m pytest tests/unit/test_traffic_demand_model.py tests/unit/test_backend_derived_summary.py tests/unit/test_integration_demo_scenario.py tests/unit/test_configuration_view.py tests/unit/test_scenario_builder.py tests/integration/test_config_control.py -k "not default_generated_scenario_config_file_loads and not config_loads_correctly" -q`
    - Result: passed, 53 tests.
- Problems encountered:
  - The repository still has two local runtime config files whose values differ
    from test baselines. They were left untouched and unstaged.
- Known remaining issues:
  - The service-mix generator is still flow-level and abstract. It does not
    model packets, retransmissions, RF propagation, or packet queues.
  - The summary reports aggregate mix counts; per-user active request state and
    per-satellite service-load panels remain separate observability tasks.
- Recommended follow-up:
  - Emit deterministic per-user business state and per-satellite service-load
    summaries into the dashboard snapshot stream.

## 2026-07-05 - Runtime Business Observability Semantics v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: enrich backend-owned runtime observability summaries for the
  standalone data panel. User request rows now include active business type,
  backend business label, and request state. Satellite service rows now include
  service-user count, primary service user, next-hop count, primary next hop,
  compute-service route count, and network-service route count. The data panel
  consumes these backend fields inside the existing user and satellite tables
  without changing overall layout. Event Kernel behavior and packet-level
  semantics are unchanged.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `tests/unit/test_runtime_observability.py`
  - `tests/integration/test_runtime_session_control.py`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 2 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 236 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed.
- Problems encountered:
  - None in scope. Existing local runtime config drift remains untouched.
- Known remaining issues:
  - Request states are deterministic route/service-history labels; they are not
    packet-level queue states.
  - Satellite business counts are route-level counts. They do not represent RF
    beam scheduling, antenna beams, or packet queues.
- Recommended follow-up:
  - Add time-varying user/satellite observability charts fed by these semantic
    fields, then connect mixed traffic demand to per-user request timelines.

## 2026-07-05 - KPI Time-Series Initial Baseline v1

- Branch: `feature/T164-dashboard-observability-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: improve live dashboard KPI time-series usability when the runtime has
  only one backend KPI sample after simulation time has already advanced. The
  MetricsCollector now prepends a deterministic `sim_time=0` zero-demand
  baseline sample for single-sample series, so throughput, loss proxy, delay
  variation, and compute resource charts can show a truthful initial-to-current
  transition instead of a single static point. Existing multi-sample series are
  unchanged. This is a metrics observation change only; Event Kernel, network
  model behavior, and packet-level semantics are unchanged.
- Changed files/modules:
  - `src/leo_twin/services/metrics/collector.py`
  - `tests/unit/test_metrics_module.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_metrics_module.py::test_metrics_collector_kpi_time_series_prepends_initial_baseline_for_single_sample tests/unit/test_metrics_module.py::test_metrics_collector_publishes_backend_kpi_time_series tests/unit/test_metrics_module.py::test_metrics_collector_kpi_time_series_refreshes_current_tail_sample tests/unit/test_metrics_module.py::test_metrics_collector_kpi_time_series_accepts_runtime_sim_time_tail tests/unit/test_metrics_module.py::test_metrics_collector_reports_recent_flow_kpi_window tests/integration/test_runtime_session_control.py::test_runtime_kpi_series_changes_with_configured_flow_demand tests/integration/test_runtime_session_control.py::test_runtime_kpi_series_exposes_initial_baseline_for_single_live_sample -q`
    - Result: passed, 7 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 236 tests.
- Problems encountered:
  - A probe showed that high-pressure mixed traffic can legitimately expose
    only one live KPI sample early in the run. The fix adds a deterministic
    initial baseline instead of inventing random jitter.
- Known remaining issues:
  - This does not make every scenario highly dynamic. If the configured traffic
    demand is low and routes remain stable, loss and delay variation proxies may
    still remain zero, which is valid for the current flow-level abstraction.
- Recommended follow-up:
  - Add a user-facing "network stress scenario" preset or acceptance config that
    combines mixed demand, higher flow demand, and transport loss to exercise
    throughput, latency, loss proxy, and delay-variation charts over time.

## 2026-07-05 - Service Placement Model v2

- Branch: `feature/T170-service-placement-model-v2`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a product-level, deterministic communication-compute service
  placement contract and pure model for selecting satellite-hosted compute
  nodes. The model chooses by minimum estimated finish time with deterministic
  tie-breaks, consumes explicit queue state, reports queue delay and execution
  delay, and exposes canonical rejection reasons. Backend-derived summaries now
  include `service_placement_contract_v2`, and frontend runtime contract types
  accept the new backend-owned semantics. Event Kernel behavior, packet-level
  simulation, and runtime frontend layout are unchanged.
- Changed files/modules:
  - `src/leo_twin/schema/service_placement_contract.py`
  - `src/leo_twin/models/compute/placement.py`
  - `src/leo_twin/schema/__init__.py`
  - `src/leo_twin/models/compute/__init__.py`
  - `src/leo_twin/services/derived_summary.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `tests/unit/test_service_placement_model_v2.py`
  - `tests/unit/test_compute_resource_contract_v2.py`
  - `docs/service_placement_model_v2.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_service_placement_model_v2.py tests/unit/test_compute_resource_contract_v2.py tests/unit/test_backend_derived_summary.py -q`
    - Result: passed, 20 tests.
  - `python -m pytest tests/unit/test_compute_scheduling_runtime.py tests/unit/test_network_aware_compute.py -q`
    - Result: passed, 15 tests.
  - `python -m pytest tests/integration/test_config_control.py::test_initialize_writes_config_and_start_gates_streams tests/integration/test_config_control.py::test_frontend_control_messages_are_processed -q`
    - Result: passed, 2 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 261 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
- Problems encountered:
  - Initial queue-state unit test expected a queued node when two candidates had
    identical finish times. The contract tie-breaks by earlier `start_time`, so
    the test data was corrected to make the queued node genuinely finish first.
  - Existing local runtime config drift remains untouched and unstaged.
- Known remaining issues:
  - `RouteAwareComputeEngine` still has a local node-selection helper. A later
    localized task should replace that helper with `place_compute_service()`
    once runtime regression tests are prepared.
  - Placement remains a deterministic flow-level abstraction. It does not model
    packets, RF behavior, preemption, service migration, power, or thermal
    constraints.
- Recommended follow-up:
  - Wire Service Placement Model v2 into the route-aware compute runtime and
    emit per-task placement decisions into the dashboard observability stream.

## 2026-07-05 - Route-Aware Service Placement Runtime v1

- Branch: `feature/T171-route-aware-placement-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: connect `RouteAwareComputeEngine` to Service Placement Model v2. The
  runtime now keeps the existing deterministic workload ordering, then calls
  `place_compute_service()` for node placement using route candidate nodes and
  explicit node `available_at` queue state. Service latency history now carries
  backend-owned placement metadata, and user request summaries pass it through
  when available. Frontend contract types and fixture tests were updated, but
  frontend layout was not changed. Event Kernel behavior and packet-level
  semantics are unchanged.
- Changed files/modules:
  - `src/leo_twin/models/compute/network_aware.py`
  - `src/leo_twin/services/metrics/collector.py`
  - `src/leo_twin/services/runtime_observability.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `tests/unit/test_network_aware_compute.py`
  - `tests/integration/test_compute_service_lifecycle.py`
  - `tests/unit/test_runtime_observability.py`
  - `docs/service_placement_model_v2.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_network_aware_compute.py tests/integration/test_compute_service_lifecycle.py tests/unit/test_metrics_module.py::test_service_latency_history_includes_sorted_component_timeline tests/unit/test_runtime_observability.py::test_runtime_lifecycle_summaries_are_deterministic_and_backend_owned tests/unit/test_service_placement_model_v2.py tests/unit/test_compute_scheduling_runtime.py -q`
    - Result: passed, 24 tests.
  - `python -m json.tool frontend/tests/fixtures/runtimeStatus.contract.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 261 tests.
- Problems encountered:
  - Service history tests were intentionally updated because runtime metrics now
    include placement metadata. Legacy metric samples without placement tags
    remain compatible and do not emit empty placement fields.
  - Existing local runtime config drift remains untouched and unstaged.
- Known remaining issues:
  - The dashboard layout does not yet display the new placement fields in
    visible user/satellite rows.
  - Placement still uses flow-level deterministic queue state only. It does not
    model packet queues, preemption, migration, power, or thermal constraints.
- Recommended follow-up:
  - Add dashboard table columns/detail drawer fields for selected compute node,
    placement status, bottleneck resource, and candidate count.

## 2026-07-05 - Dashboard Placement Fields v1

- Branch: `feature/T172-dashboard-placement-fields-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: expose backend-owned service placement semantics in the standalone data
  panel. User business rows now include a placement-node column fed by
  `user_request_summary_v1` or service latency history fallback data. Per-service
  latency trace rows now display placement status, selected compute node,
  bottleneck resource, and capable/total candidate counts. Detail row filtering
  also searches placement labels. This is a frontend semantic-display task only;
  no Event Kernel, backend model, packet-level simulation, or dashboard layout
  redesign was introduced.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 261 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
  - `python -m pytest tests/unit/test_runtime_observability.py::test_runtime_lifecycle_summaries_are_deterministic_and_backend_owned tests/integration/test_compute_service_lifecycle.py -q`
    - Result: passed, 2 tests.
- Problems encountered:
  - While adding tests, an initial service-history fixture was inserted into a
    similarly shaped but unrelated `buildDataPanelSummary()` test. The fixture
    was removed and re-added to the intended detail-row filter test.
  - Existing local runtime config drift remains untouched and unstaged.
- Known remaining issues:
  - The data panel shows placement summaries in compact table text. A later UI
    task should add a richer selected-user or selected-satellite detail drawer
    with full placement candidates and queue details.
  - Placement remains the deterministic flow-level abstraction from Service
    Placement Model v2; no packet queues, migration, power, or thermal effects
    are displayed.
- Recommended follow-up:
  - Add a selected user/satellite detail drawer that expands placement
    candidates, queue delay, execution delay, and compute resource vector usage.

## 2026-07-05 - Dashboard Detail Inspector v1

- Branch: `feature/T173-dashboard-detail-inspector-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a selected user/satellite detail inspector to the standalone data
  panel using existing backend/runtime fields. User and satellite detail rows are
  now selectable, the current page falls back to its first visible row when no
  selection is active, and the inspector exposes service placement, route,
  queue, next-hop, compute resource, task, and network status summaries without
  changing backend models, Event Kernel behavior, or frontend routing.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 264 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
  - `python -m pytest tests/integration/test_compute_service_lifecycle.py -q`
    - Result: passed, 1 test.
- Problems encountered:
  - The default PowerShell process did not have the bundled Node runtime on
    `PATH`, so the frontend validation was rerun with the repository's bundled
    Node/Pnpm paths.
  - Existing local runtime config drift remains untouched and unstaged.
- Known remaining issues:
  - The inspector is still a compact summary over the currently streamed table
    rows. It does not yet expose full placement candidate lists, per-task queue
    timelines, or a separate detail drawer fed by a dedicated backend detail
    endpoint.
- Recommended follow-up:
  - Add a backend-owned node detail stream or query endpoint for full
    per-user/per-satellite placement candidates, queue history, and resource
    timeline data, then bind it into an expandable dashboard drawer.

## 2026-07-05 - Node Detail Summary API v1

- Branch: `feature/T174-node-detail-summary-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add backend-owned `node_detail_summary_v1` to runtime status. The
  summary is derived deterministically from existing
  `user_request_summary_v1` and `satellite_service_summary_v1` rows, and
  provides user/satellite detail-card fields for the dashboard inspector.
  DataPanel now prefers these backend fields and falls back to local row
  summaries when an older runtime status does not provide the new contract.
  Event Kernel, simulation models, packet-level semantics, frontend routing,
  and layout architecture are unchanged.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `tests/unit/test_runtime_observability.py`
  - `tests/integration/test_runtime_session_control.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 3 tests.
  - `python -m json.tool frontend/tests/fixtures/runtimeStatus.contract.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 265 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
- Problems encountered:
  - A first integration-test command targeted a non-existent test name. The
    assertion was added to the existing runtime status/control-plane integration
    test and rerun successfully.
  - Existing local runtime config drift remains untouched and unstaged.
- Known remaining issues:
  - `node_detail_summary_v1` is currently embedded in `/runtime/status` and
    limited to the visible summary windows. It is not yet a cursor-paged
    dedicated node-detail endpoint and does not expose full placement candidate
    lists or queue timelines.
- Recommended follow-up:
  - Add `/runtime/details/nodes` or an equivalent cursor-readable detail stream
    for full per-node placement candidates, queue history, and resource
    timeline data without bloating `/runtime/status`.

## 2026-07-05 - Node Detail Card Endpoint v1

- Branch: `feature/T175-node-detail-card-endpoint-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a dedicated cursor-readable `/runtime/details/nodes` endpoint for
  backend-owned user/satellite detail cards. The endpoint returns a deterministic
  combined node-card window ordered by users first and satellites second, while
  existing `/runtime/status`, `/runtime/details/users`, and
  `/runtime/details/satellites` remain compatible. Frontend API contracts now
  include `loadRuntimeNodeDetails()` for future dashboard drawers, but no
  frontend layout or rendering architecture was changed.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/app/api.ts`
  - `frontend/tests/api.test.ts`
  - `tests/unit/test_runtime_observability.py`
  - `tests/integration/test_live_runtime_streaming.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py tests/integration/test_live_runtime_streaming.py::test_runtime_detail_pages_return_deterministic_windows tests/integration/test_runtime_session_control.py::test_demo_server_stream_query_parses_cursor_options -q`
    - Result: passed, 4 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 265 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
- Problems encountered:
  - Existing API test mocks were adjusted so user, satellite, and node detail
    responses match the actual request order.
  - Existing local runtime config drift remains untouched and unstaged.
- Known remaining issues:
  - `/runtime/details/nodes` returns current detail-card fields only. It still
    does not expose full placement candidate lists, per-task queue timelines, or
    resource history curves per selected node.
- Recommended follow-up:
  - Bind `loadRuntimeNodeDetails()` into a dashboard detail drawer with virtual
    scrolling and add a richer backend node-detail payload for placement
    candidate lists and resource timeline slices.

## 2026-07-05 - Dashboard Node Detail Binding v1

- Branch: `feature/T176-dashboard-node-detail-binding-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: bind the dedicated `/runtime/details/nodes` detail-card endpoint into
  the frontend dashboard data path. `App` now refreshes user, satellite, and
  node detail pages together using partial-failure tolerant loading, so older
  backends can still provide user/satellite pages while node details fall back
  to `runtimeStatus.node_detail_summary_v1`. `DataPanel` now prefers the
  dedicated node detail page for selected user/satellite inspector cards and
  falls back to runtime status when the page is unavailable.
- Changed files/modules:
  - `frontend/src/app/App.tsx`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts api.test.ts appSurface.test.ts`
    - Result: passed, 25 files / 265 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
- Problems encountered:
  - TypeScript required the test node-detail page to be non-null before passing
    it into the page-to-summary helper; the test was made explicit with a
    non-null assertion.
  - Existing local runtime config drift remains untouched and unstaged.
- Known remaining issues:
  - The UI still renders compact inspector cards. It does not yet provide a
    full drawer, virtualized all-node table, placement candidate list, or
    per-node resource timeline drill-down.
- Recommended follow-up:
  - Build a dashboard node-detail drawer that uses the node page cursor model
    for virtual scrolling and then extend backend cards with candidate and
    queue-history detail sections.

## 2026-07-05 - Dashboard Node Detail Drawer v1

- Branch: `feature/T177-dashboard-node-detail-drawer-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a full-width selected-node detail drawer to the standalone
  dashboard data panel. The existing compact user/satellite inspector cards
  remain for quick scanning, while the new drawer shows the same backend-owned
  selected user and satellite fields in a scrollable, wrapping layout so long
  route paths, service placement strings, and network/resource labels are not
  visually truncated. No backend model, Event Kernel, route logic, or frontend
  routing architecture was changed.
- Changed files/modules:
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/dataPanel.test.ts`
  - `docs/development_log.md`
- Validation:
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts`
    - Result: passed, 25 files / 266 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
- Problems encountered:
  - None in implementation. Existing local runtime config drift remains
    untouched and unstaged.
- Known remaining issues:
  - The drawer still displays the selected user and selected satellite cards
    from the current table windows. It is not yet a virtualized all-node drawer
    with cursor navigation, placement candidate lists, or per-node timeline
    charts.
- Recommended follow-up:
  - Add cursor navigation and search over `/runtime/details/nodes` directly
    from the drawer, then extend backend node cards with candidate and
    queue-history detail sections.

## 2026-07-05 - Backend Node Detail Sections v1

- Branch: `feature/T178-node-detail-sections-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add backend-owned semantic `sections` to user and satellite node
  detail cards while keeping flat `fields` for backward compatibility. User
  cards are grouped into identity, business path, and compute/queue placement
  sections. Satellite cards are grouped into service/routing, compute
  resources, and network state sections. The dashboard detail drawer now
  renders sections when available and falls back to flat fields for older
  runtime payloads. Event Kernel behavior, simulation models, route logic, and
  packet-level semantics remain unchanged.
- Changed files/modules:
  - `src/leo_twin/services/runtime_observability.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/unit/test_runtime_observability.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_observability.py -q`
    - Result: passed, 2 tests.
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 1 test.
  - `python -m json.tool frontend/tests/fixtures/runtimeStatus.contract.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 266 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
- Problems encountered:
  - None in implementation. Existing local runtime config drift remains
    untouched and unstaged.
- Known remaining issues:
  - Sections group currently available summary fields only. They do not yet
    contain full placement candidate lists, queue history samples, or per-node
    resource timeline series.
- Recommended follow-up:
  - Add backend section payloads for placement candidates and queue/resource
    timelines, then expose cursor navigation/search directly in the dashboard
    drawer.

## 2026-07-05 - Runtime Reproducibility Manifest v1

- Branch: `feature/T179-runtime-reproducibility-manifest-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a backend-owned runtime reproducibility manifest to the live demo
  runtime status. The manifest records deterministic hashes for scenario,
  control config, generated config, runtime state, metrics summary, and the
  manifest itself. It also declares the expected text artifacts
  `config_snapshot.json`, `events.jsonl`, `metrics.csv`, and `summary.json`
  without changing Event Kernel behavior or live streaming progression. The
  dashboard status contract now exposes this field and renders a compact
  session/hash summary in the standalone data panel.
- Changed files/modules:
  - `src/leo_twin/services/runtime_reproducibility.py`
  - `examples/integration_demo/control_plane.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/src/app/App.css`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `tests/unit/test_runtime_reproducibility.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/unit/test_runtime_reproducibility.py -q`
    - Result: passed, 2 tests.
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer -q`
    - Result: passed, 1 test.
  - `python -m json.tool frontend/tests/fixtures/runtimeStatus.contract.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 267 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
- Problems encountered:
  - The default shell did not have `node` on `PATH`; validation was rerun with
    the bundled Codex Node/Pnpm paths.
  - Existing local runtime config drift remains untouched and unstaged:
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`.
- Known remaining issues:
  - Live `/runtime/status` now declares reproducibility hashes and artifact
    availability, but the demo server still does not provide a one-click
    downloadable run package endpoint for `events.jsonl`, `metrics.csv`,
    `summary.json`, and config snapshots.
- Recommended follow-up:
  - Add result package export v1 with an explicit `/runtime/export` or CLI
    path that writes the manifest plus text artifacts into a deterministic run
    directory.

## 2026-07-05 - Runtime Result Package Export v1

- Branch: `feature/T180-runtime-result-package-export-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a live runtime result-package export path for the integration demo
  backend. `DemoControlPlane.export_runtime_package()` now writes a
  deterministic package directory containing `manifest.json`,
  `config_snapshot.json`, `events.jsonl`, `metrics.csv`, and `summary.json`,
  while preserving any existing segmented event-log files produced by the
  metrics collector. The demo HTTP server exposes this through
  `GET /runtime/export`. Event Kernel behavior, live stream progression, and
  frontend architecture remain unchanged.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_adapter_exports_runtime_result_package -q`
    - Result: passed, 1 test.
  - `python -m pytest tests/unit/test_runtime_reproducibility.py tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer tests/integration/test_runtime_session_control.py::test_demo_adapter_exposes_cursor_batches tests/integration/test_runtime_session_control.py::test_demo_adapter_exports_runtime_result_package -q`
    - Result: passed, 5 tests.
- Problems encountered:
  - The metrics collector may also write segmented files such as
    `events-000001.jsonl`; the export test now requires the core package files
    and permits those existing supplemental event segments.
  - Existing local runtime config drift remains untouched and unstaged:
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`.
- Known remaining issues:
  - `/runtime/export` currently writes to the backend filesystem and returns
    file paths/hashes. It does not yet stream a zip archive or provide frontend
    download controls.
- Recommended follow-up:
  - Add a frontend export action plus a backend archive/download response that
    packages the deterministic result directory without exposing arbitrary
    filesystem paths.

## 2026-07-05 - Runtime Export Download v1

- Branch: `feature/T181-runtime-export-download-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a browser-downloadable deterministic runtime export archive.
  `DemoControlPlane.export_runtime_archive()` now wraps the existing result
  package in a ZIP file with stable entry ordering and fixed ZIP metadata, and
  the demo server exposes it through `GET /runtime/export/archive` with
  `application/zip` and `Content-Disposition`. The standalone dashboard adds a
  `导出复盘包` action that links to the archive endpoint through the existing
  `/runtime` proxy. Event Kernel behavior, live stream progression, and
  simulation models remain unchanged.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/app/api.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/api.test.ts`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_adapter_exports_runtime_result_package tests/integration/test_runtime_session_control.py::test_demo_adapter_exports_deterministic_runtime_archive -q`
    - Result: passed, 2 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts`
    - Result: passed, 25 files / 268 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
- Problems encountered:
  - Repeated archive exports initially produced different ZIP hashes because
    `config_snapshot.json` included volatile runtime diagnostics
    (`profiling_summary`, `backpressure_summary`, and
    `stream_diagnostics_v1`). The export snapshot now records a stable status
    policy and excludes those fields while keeping manifest/config/metrics
    outputs deterministic.
  - Existing local runtime config drift remains untouched and unstaged:
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`.
- Known remaining issues:
  - The browser action is a direct download link. It does not yet show
    frontend progress, success/failure toast feedback, or export history.
- Recommended follow-up:
  - Add export UX feedback and a small `/runtime/export/history` summary so
    users can see the latest generated packages without inspecting backend
    logs or filesystem paths.

## 2026-07-05 - Runtime Export History v1

- Branch: `feature/T182-runtime-export-history-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add backend-owned recent runtime export history and surface it in the
  dashboard. `DemoControlPlane` now records the current session's recent
  package/archive exports with package id, export type, manifest hash,
  simulation time, event count, and archive metadata when available. The
  summary is exposed in runtime status as `runtime_export_history_v1` and via
  `GET /runtime/export/history`. The standalone dashboard renders the latest
  export as a compact runtime card. Event Kernel behavior, live advancement,
  simulation models, and result package formats remain unchanged.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/app/api.ts`
  - `frontend/src/dashboard/data_panel/DataPanel.tsx`
  - `frontend/tests/api.test.ts`
  - `frontend/tests/dataPanel.test.ts`
  - `frontend/tests/fixtures/runtimeStatus.contract.json`
  - `frontend/tests/runtimeContractFixture.test.ts`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - `python -m json.tool frontend/tests/fixtures/runtimeStatus.contract.json`
    - Result: passed.
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_server_adapter_uses_runtime_status_and_control_layer tests/integration/test_runtime_session_control.py::test_demo_adapter_reports_runtime_export_history tests/integration/test_runtime_session_control.py::test_demo_adapter_exports_deterministic_runtime_archive -q`
    - Result: passed, 3 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts dataPanel.test.ts runtimeContractFixture.test.ts`
    - Result: passed, 25 files / 270 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
- Problems encountered:
  - Adding export history to runtime status made repeated archive exports
    unstable until `runtime_export_history_v1` was excluded from
    `config_snapshot.json`'s stable export-status snapshot. Runtime status still
    exposes the history; the exported package snapshot now remains stable.
  - Existing local runtime config drift remains untouched and unstaged:
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`.
- Known remaining issues:
  - Export history is in-memory and scoped to the current backend process and
    session. It is not yet persisted across backend restarts.
- Recommended follow-up:
  - Add persisted run catalog v1 under `artifacts/runtime_exports`, with a
    deterministic index file so users can review previous runs after restart.

## 2026-07-05 - Runtime Export Catalog v1

- Branch: `feature/T183-runtime-export-catalog-v1`
- Commit: pending commit note; final hash is reported after commit creation.
- Scope: add a persisted deterministic runtime export catalog under
  `artifacts/runtime_exports/runtime_export_catalog_v1.json`. Package and
  archive exports now update the catalog with package id, export type,
  manifest hash, simulation time, event count, file hashes, relative package
  directory, and archive metadata when available. The demo backend exposes the
  catalog via `GET /runtime/export/catalog`, and the frontend API layer has a
  typed `loadRuntimeExportCatalog()` helper for future catalog UI work. Event
  Kernel behavior, live streaming, model semantics, and result package files
  remain unchanged.
- Changed files/modules:
  - `examples/integration_demo/control_plane.py`
  - `examples/integration_demo/server.py`
  - `frontend/src/core/event_types/index.ts`
  - `frontend/src/app/api.ts`
  - `frontend/tests/api.test.ts`
  - `tests/integration/test_runtime_session_control.py`
  - `docs/integration_demo.md`
  - `docs/development_log.md`
- Validation:
  - `python -m pytest tests/integration/test_runtime_session_control.py::test_demo_adapter_persists_runtime_export_catalog tests/integration/test_runtime_session_control.py::test_demo_adapter_reports_runtime_export_history tests/integration/test_runtime_session_control.py::test_demo_adapter_exports_deterministic_runtime_archive -q`
    - Result: passed, 3 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend test -- api.test.ts`
    - Result: passed, 25 files / 271 tests.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend exec tsc --noEmit -p tsconfig.json`
    - Result: passed.
  - Bundled Node/Pnpm:
    `pnpm --dir frontend build`
    - Result: passed. Existing DataPanel chunk-size warning remains.
- Problems encountered:
  - Archive exports create both the base package files and the ZIP archive, so
    the persisted catalog intentionally records both `PACKAGE` and `ARCHIVE`
    entries for the same package id.
  - The first catalog implementation returned Python tuples while the persisted
    JSON naturally returned lists. The catalog document is now normalized to
    JSON-compatible payloads before hashing and returning.
  - Existing local runtime config drift remains untouched and unstaged:
    `configs/generated_full_system_demo.json` and `configs/sees_control.yaml`.
- Known remaining issues:
  - The frontend can fetch the catalog through the API helper, but there is not
    yet a dedicated catalog table or persisted-run browser in the dashboard.
- Recommended follow-up:
  - Add a dashboard export catalog view with a compact table of prior packages,
    archive hashes, simulation time, and package ids.
