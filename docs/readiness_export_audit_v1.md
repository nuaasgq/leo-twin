# Readiness Export Audit v1

Date: 2026-07-09

## Scope

This task persists two backend-owned runtime status summaries into runtime
result packages:

- `v2_executable_readiness_v1.json`
- `traffic_business_activity_window_v1.json`

Both artifacts are standalone export artifacts derived from
`config_snapshot.status`. They do not recompute readiness, regenerate traffic,
replay events, or introduce packet-level simulation.

## Exported Evidence

`v2_executable_readiness_v1.json` contains:

- the original `v2_executable_readiness_v1` status object;
- gate counts and failed gate ids;
- executable-ready status;
- packet-level and frontend-inference boundary flags;
- operator next action;
- deterministic evidence and artifact hashes.

`traffic_business_activity_window_v1.json` contains:

- the original `traffic_business_activity_window_v1` status object;
- current simulation time;
- active, recent, pending, idle, and window user counts;
- bounded activity-window item count;
- deterministic state-count rows;
- deterministic evidence and artifact hashes.

## Audit Surfaces

The new artifacts are included in:

- result package recommended file contract;
- artifact browser index;
- review summary;
- diagnostics bundle;
- scenario review bundle;
- long-term package audit index;
- scenario review recommended order and evidence hash resolution.

## Boundaries

The export path is read-only over runtime status:

- no Event Kernel behavior change;
- no model recomputation;
- no event replay;
- no packet-level simulation;
- no external simulator artifacts.

## Validation

- `python -m py_compile examples/integration_demo/control_plane.py src/leo_twin/services/result_package_contract.py`: passed.
- `pytest tests/unit/test_result_package_contract_v1.py tests/integration/test_result_package_export_v1.py`: 44 passed.
- `pytest tests/integration/test_runtime_session_control.py::test_demo_adapter_exports_runtime_result_package tests/integration/test_runtime_session_control.py::test_demo_adapter_serves_persisted_runtime_export_artifacts`: 2 passed.
