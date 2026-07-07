# Benchmark Scenario Matrix v1

Date: 2026-07-06
Branch: `feature/T217-benchmark-scenario-matrix-v1`

`benchmark_scenario_matrix_v1` is the backend-owned source of truth for the
current product acceptance benchmark set. It does not create new simulation
behavior. It resolves the shipped acceptance YAML files through the normal SEES
configuration loader and records deterministic expectations for scale,
fidelity, traffic, compute, and artifact generation.

## Matrix Source

Python API:

```python
from leo_twin.services.benchmark_scenarios import (
    benchmark_scenario_matrix_v1_to_dict,
)

matrix = benchmark_scenario_matrix_v1_to_dict()
```

Matrix id:

```text
leo_twin.benchmark_scenario_matrix.v1
```

## Baseline Scenarios

| Scenario | Config | Purpose | Expected fidelity |
| --- | --- | --- | --- |
| `small_demo_72sat` | `configs/acceptance/small_demo_72sat.yaml` | detailed control-plane and dashboard semantic baseline | orbit `PER_SATELLITE`, metrics `DETAILED`, ISL `DETAILED_SMALL_SCALE` |
| `medium_demo_300sat` | `configs/acceptance/medium_demo_300sat.yaml` | scale transition baseline for batch orbit updates | orbit `BATCH`, metrics `DETAILED`, ISL `BOUNDED_CANDIDATE` |
| `scale_demo_1200sat_short` | `configs/acceptance/scale_demo_1200sat_short.yaml` | large-scale live-control responsiveness baseline | orbit `BATCH`, metrics `AGGREGATED`, ISL `BOUNDED_CANDIDATE` |

## Expected Ranges

Each scenario exposes exact numeric guardrails derived from its YAML config:

- `satellite_count`
- `user_count`
- `compute_node_count`
- `runtime_duration_s`
- `orbit_update_interval_s`
- `plane_count`
- `flow_interval_s`
- `task_interval_s`
- `flow_demand_capacity_mbps`
- `task_compute_demand`
- `task_data_size_mb`
- `max_space_link_candidates_per_satellite`
- `batch_space_link_update_limit`

These ranges are acceptance guardrails, not claims of physical accuracy. They
are intended to catch unintended drift in shipped benchmark inputs and backend
derived semantics.

## Runtime Status Expectations

Each benchmark also exposes `runtime_status_expectation`. The current required
fields include:

- `fidelity_summary`
- `metrics_summary`
- `network_kpi_provenance_v2`
- `network_kpi_credibility_v1`
- `network_kpi_benchmark_validation_v1`
- `route_explanation_summary_v1`
- `route_provenance_trust_summary_v1`
- `reproducibility_manifest_v1`

The network KPI benchmark expectation requires
`network_kpi_benchmark_validation_v1` to be derived from
`network_kpi_provenance_v2` and `metrics_summary`, use the
`FLOW_LEVEL_PROXY_RUNTIME_GUARDRAILS` profile, forbid packet-level simulation,
and report zero failed checks for standard runtime acceptance. `WARN` remains
allowed because these guardrails are product-level flow-proxy checks, not
physical RF or packet-level validation.

The route trust expectation requires `route_provenance_trust_summary_v1` to be
derived from `route_explanation_summary_v1`, use the
`FLOW_LEVEL_ROUTE_PROXY` model, forbid packet-level simulation, forbid all-pairs
route/link computation, and assess at least one route after the benchmark
runtime advances.

## Acceptance Command

Each scenario records the command shape used for product acceptance:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_product_acceptance.ps1 -AcceptanceConfig configs/acceptance/small_demo_72sat.yaml
```

The config path changes per scenario.

For a disposable local run that restarts services, applies one or more selected
benchmark YAMLs through backend `/control`, then restores local runtime config
drift, use:

```powershell
.\disposable_acceptance_leo_twin.bat -PlanOnly -JsonSummary
.\scripts\run_disposable_acceptance.ps1 -SkipBuild
.\scripts\run_disposable_acceptance.ps1 -SkipBuild -AcceptanceConfig configs\acceptance\scale_demo_1200sat_short.yaml
```

The harness delegates the actual product checks back to
`scripts\verify_product_acceptance.ps1`; it does not define a second acceptance
standard.

## Scope Boundaries

The benchmark matrix keeps the same hard product constraints as the rest of
SEES:

- Event Kernel behavior is not modified.
- STK, EXATA, AFSIM, and DDS are forbidden.
- Packet-level simulation is not introduced.
- Benchmarks use deterministic flow-level abstractions.
- Large-scale fidelity degradation is reported by backend policy, not inferred
  by the frontend.

## Required Result Artifacts

Future result-package work should bind benchmark runs to these artifacts:

- config snapshot
- `events.jsonl`
- `metrics.csv`
- `summary.json`
- runtime log
