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
- `GET /scenario/user-config/schema`
- `GET /scenario/user-config/templates`
- `GET /scenario/user-config/export`
- `POST /scenario/user-config/validate`

Important contract fields:

- `version`: currently `v2`
- `schema_id`: `sees.user_configuration.v2`
- `unknown_key_policy`: `REJECT`
- `defaulting_policy`: `OMITTED_FIELDS_USE_BACKEND_DEFAULTS`
- `frontend_policy`: `CONTROL_PANEL_KEY_FIELDS_ONLY`
- `fields`: deterministic ordered field schemas
- `templates`: executable user template references
- `examples`: accepted/rejected validation examples

The HTTP endpoints are read-only:

- `/scenario/user-config/schema` returns the current backend-derived schema v2,
  including defaults and current values.
- `/scenario/user-config/templates` returns the approved executable template
  catalog and the control command needed to load a template.
- `/scenario/user-config/export` returns the current effective `SEESConfig`
  JSON mapping, a stable config hash, validation status, and supported import
  paths.
- `/scenario/user-config/validate` accepts a JSON mapping and returns a
  validate-only `USER_CONFIGURATION_VALIDATION_REPORT` with normalized config
  and stable hash when accepted. It does not apply the config by itself. When
  accepted, the report includes an explicit `apply_command` that names
  `normalized_config` as the safe `CONFIG_UPDATE` payload source and a
  deterministic `change_summary` comparing the current effective config with
  the accepted normalized candidate. It also includes `apply_readiness`, a
  backend runtime-state summary describing whether the config can be applied
  now, the current controller/session lifecycle state, recommended operator
  action, and session/stream side effects.

Configuration import remains an explicit control-plane action. Validated full
or partial mappings use `CONFIG_UPDATE`, template loading uses `LOAD_TEMPLATE`,
and package restore uses `RESTORE_EXPORT_PACKAGE`. The read-only endpoints do
not write config files, initialize sessions, or mutate the runtime.

The standalone dashboard consumes the same read-only endpoints. It shows a
compact contract summary plus a schema field browser grouped by backend
sections, including key control-panel fields and detailed file-only fields, so
users can understand which settings belong in the UI and which belong in the
full YAML/JSON configuration file.

Backend-generated scenario summaries also expose
`backend_summary.configuration_explanation_v2`. This read-only object maps the
accepted configuration surfaces and sections (`scenario`, `traffic`, `network`,
`compute`, `runtime`, and `ui`) to current backend model semantics, current
available values, deterministic/reproducibility policies, and explicit excluded
capabilities such as packet-level simulation or external simulator integration.
The frontend should use this object for product explanations rather than
inferring model meaning locally.

The standalone dashboard renders a compact `configuration_explanation_v2`
section in the auxiliary model analysis area. It summarizes configuration
surfaces, deterministic policy, model boundaries, and per-section current
values directly from the backend object.

The dashboard user configuration panel also includes a JSON mapping preflight
box. It calls `/scenario/user-config/validate`, displays accepted/rejected
validation results, normalized config hash, backend error messages, and the
backend-declared apply command. The dashboard only enables "apply" after a
successful preflight, and it sends the backend-normalized config rather than the
raw editor text. Applying a config reinitializes the session and reconnects
runtime streams through the existing control plane.

The validation `change_summary` is backend-owned. It includes:

- `baseline`: the current effective `SEESConfig`;
- `candidate`: the normalized user config after backend defaults are applied;
- `changed_field_count`: total changed leaf fields;
- `section_counts`: deterministic root-section counts such as `scenario` or
  `runtime`;
- `changes`: a sorted bounded preview of changed field paths, current values,
  candidate values, and change types;
- `hidden_change_count`: fields omitted from the bounded preview.

The standalone dashboard renders this backend diff in the preflight result
card. It shows the total changed field count, section counts, hidden preview
count when applicable, and a bounded list of changed field paths before the
user can press "应用配置".

`apply_readiness` is also backend-owned. The dashboard renders it in the
preflight card so users can see when applying will reinitialize an existing or
running session, whether extra confirmation is recommended, and what will
happen to stream buffers.

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
