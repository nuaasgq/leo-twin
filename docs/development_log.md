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
- Commit: pending commit
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
