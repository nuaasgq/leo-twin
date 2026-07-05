# User Configuration Schema v2

Date: 2026-07-05
Schema id: `sees.user_configuration.v2`

## Purpose

User Configuration Schema v2 is the backend-owned contract for SEES scenario
configuration. It separates:

- key controls shown by the frontend control panel;
- the full detailed YAML/JSON configuration file used by advanced users;
- deterministic validation and defaulting rules;
- executable, commented templates.

The frontend should not infer business or model semantics from field names. It
should use backend summaries, schema fields, and model-assumption objects.

## Scope

The schema covers every leaf field in `SEESConfig`:

- `scenario`: constellation scale, onboard compute resources, workload
  smoothing, orbit, and traffic demand;
- `network`: flow-level protocol, routing, channel abstraction, and ISL
  fidelity inputs;
- `runtime`: mode, speed factor, deterministic seed, and duration;
- `ui`: initial visualization preferences.

The schema is intentionally not a high-fidelity simulator configuration. The
project still forbids STK, EXATA, AFSIM, DDS, packet-level simulation, RF
propagation modeling, and antenna pattern modeling.

## Backend Contract

The backend exposes the schema through:

- `build_user_configuration_schema_v2(config)`
- `validate_user_configuration_mapping_v2(raw)`
- `configuration_surface_summary.user_config_schema_v2`

Important contract fields:

- `version`: currently `v2`
- `schema_id`: `sees.user_configuration.v2`
- `unknown_key_policy`: `REJECT`
- `defaulting_policy`: `OMITTED_FIELDS_USE_BACKEND_DEFAULTS`
- `frontend_policy`: `CONTROL_PANEL_KEY_FIELDS_ONLY`
- `fields`: deterministic ordered field schemas
- `templates`: executable user template references
- `examples`: accepted/rejected validation examples

Each field schema includes:

- path
- section
- label
- description
- value type
- default value
- current value
- UI/editing surface
- enum values when applicable
- numeric constraints when applicable
- validation rules
- unit when applicable

## Accepted Minimal Example

```yaml
scenario:
  satellite_count: 72
  compute_nodes: 72
runtime:
  duration: 600
  seed: 20260703
```

Omitted fields are filled from backend defaults. The normalized effective config
is deterministic.

## Rejected Example

```yaml
scenario:
  satellite_count: 72
  unsupported_compute_gpu: 1.0
```

This must be rejected with an unknown-key validation error. Silent fallback is
not allowed.

## Commented Templates

YAML comments are not preserved after parsing, so user-facing comments live in
executable templates:

- `configs/templates/sees_user_detailed.example.yaml`
- `configs/templates/sees_user_dynamic_observability.example.yaml`
- `configs/templates/sees_user_network_stress_120.example.yaml`
- `configs/templates/sees_user_large_scale_1200.example.yaml`

These templates are the recommended starting point for users who need more than
the frontend key controls.

## Determinism

The same accepted configuration and `runtime.seed` must produce the same
scenario structure and runtime behavior. Schema v2 does not change model
behavior; it makes the accepted configuration surface explicit and testable.
