# Dashboard Model Assumptions Panel v1

## Purpose

Model assumptions panel v1 makes backend-declared model boundaries visible in
the standalone dashboard. It consolidates model assumptions, scale fidelity
warnings, KPI credibility, and configuration boundary labels into one product
surface.

The panel is display-only. It does not change simulation behavior.

## Data Sources

- `backend_summary.model_assumptions`
- `runtimeStatus.fidelity_summary`
- `runtimeStatus.network_kpi_credibility_v1`
- `backend_summary.configuration_explanation_v2`

## Display Content

The panel shows:

- backend model assumptions
- selected large-scale fidelity policy
- fidelity warnings such as batched orbit updates or bounded ISL candidates
- KPI credibility status and caveats
- forbidden integration / packet-level boundary text from backend
  configuration explanation

T274 adds a neighboring model trust evidence workspace. It does not replace the
assumptions panel; it summarizes the assumptions panel, KPI credibility, KPI
formula provenance, reproducibility manifest, export diagnostics, and runtime
status into deterministic evidence rows so missing proof is visible instead of
silently hidden.

## Model Boundary

- The frontend does not invent model assumptions locally.
- No Event Kernel behavior changes are introduced.
- No packet-level simulation is introduced.
- No STK, EXATA, AFSIM, or DDS integration is introduced.
- The panel explains existing backend semantics and runtime policy only.

## Follow-Up

- Add copy/export support for model assumptions in result packages.
- Link each assumption to the future model verification report.
- Split KPI credibility details into a drill-down panel when the network model
  gains more provenance fields.
- Add route explanation evidence once route provenance has a backend trust
  summary.
