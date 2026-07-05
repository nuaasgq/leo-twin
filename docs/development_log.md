# LEO-Twin Development Log

This file records completed development tasks, committed changes, validation
results, and issues encountered during implementation. Every future completed
task must update this log in the same commit as the code or documentation
change.

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
