# Operator Diagnostics Bundle v1

Date: 2026-07-06
Branch: `feature/T223-operator-diagnostics-bundle-v1`

Operator diagnostics bundle v1 collects the local evidence needed to debug a
running SEES desktop session. It is a delivery/operations feature; it does not
change simulation models or Event Kernel behavior.

## Commands

From the repository root:

```powershell
.\diagnostics_leo_twin.bat
.\scripts\collect_operator_diagnostics.ps1
.\scripts\collect_operator_diagnostics.ps1 -JsonSummary
```

Default output root:

```text
artifacts\operator_diagnostics
```

Each run creates:

```text
artifacts\operator_diagnostics\operator-diagnostics-YYYYMMDD-HHMMSS
```

## Bundle Contents

The collector writes:

- `launcher_health.json`
- `runtime_status.json`
- `version_info.json`
- `user_config_export.json`
- `runtime_export_catalog.json`
- `diagnostics_manifest.json`
- copied launcher logs under `logs\`

If a backend endpoint is unavailable, the collector writes a
`DIAGNOSTIC_SECTION_ERROR` payload for that section and marks the bundle as
partial or invalid in the manifest.

## Manifest Contract

The Python service contract is:

```text
leo_twin.operator_diagnostics_bundle.v1
```

It records:

- bundle directory;
- bundle status: `COMPLETE`, `PARTIAL`, `INVALID`, or `EMPTY`;
- section presence and validity;
- log file records;
- recommended next actions;
- product constraints.

## Expected Use

When a user reports startup, frontend, runtime, export, or dashboard issues,
ask them to run:

```powershell
.\diagnostics_leo_twin.bat
```

Then inspect the generated `diagnostics_manifest.json` first. The manifest
points to the collected runtime status, version info, config export, export
catalog, launcher health, and logs.

## Scope Boundaries

- No packet-level traces are collected.
- No external simulator artifacts are expected.
- Runtime/local config files are copied only into the diagnostics artifact; they
  are not intended to be committed.
