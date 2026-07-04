# LEO-Twin Development Log

This file records completed development tasks, committed changes, validation
results, and issues encountered during implementation. Every future completed
task must update this log in the same commit as the code or documentation
change.

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

## 2026-07-04 - Scale Firebreak v1

- Branch: `feature/T163-frontend-dashboard-compute-v2`
- Commit: pending in this task
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
