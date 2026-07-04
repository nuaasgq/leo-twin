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
- Commit: pending in this task
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
