# Template Catalog Metadata v2

Date: 2026-07-06
Branch: `feature/T251-template-catalog-metadata-v2`

## Goal

Make user-facing scenario templates explainable before an operator loads them.
The template catalog should describe not only the executable YAML path, but also
the scenario scale, expected KPI behavior, and fidelity mode represented by
each template.

## Backend Contract

Each backend-approved template profile now includes:

- `id`
- `label`
- `path`
- `purpose`
- `scale`
- `expected_kpi_behavior`
- `fidelity_mode`
- `recommended_use`

The fields are exposed through:

- `backend_summary.configuration_surface_summary.template_profiles`
- `GET /scenario/user-config/templates`
- `GET /scenario/user-config/schema` template references

The catalog remains read-only. Loading a template still uses the existing
`LOAD_TEMPLATE` runtime control command and is still allowed only before
runtime initialization.

## Frontend Behavior

The control panel continues to show the same detailed-template list and load
button. It now consumes the backend metadata and includes scale, fidelity mode,
expected KPI behavior, and recommended use in the template detail text. The
frontend does not infer these semantics locally.

## Boundaries

- No Event Kernel changes.
- No simulation model behavior changes.
- No packet-level simulation.
- No frontend architecture rewrite.
- No generated runtime config files are part of this task.
