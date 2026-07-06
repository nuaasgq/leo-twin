# Model Verification Report Template v1

Date: 2026-07-06
Branch: `feature/T218-model-verification-report-template-v1`

`model_verification_report_template_v1` defines the review structure for SEES
benchmark model verification. It consumes the benchmark scenario matrix and
existing product contracts. It does not run a simulation and does not add new
model behavior.

## Template Source

Python API:

```python
from leo_twin.services.model_verification_report import (
    model_verification_report_template_v1_to_dict,
)

template = model_verification_report_template_v1_to_dict()
```

Template id:

```text
leo_twin.model_verification_report_template.v1
```

Benchmark matrix dependency:

```text
leo_twin.benchmark_scenario_matrix.v1
```

## Report Sections

Each scenario report includes:

- scenario identity;
- configuration boundary conditions;
- determinism plan;
- formula checks;
- expected outputs;
- evidence checklist;
- known limitations;
- review decision.

## Formula Checks

Network KPI checks are derived from `network_model_contract_v2`:

- congestion pressure proxy;
- effective throughput;
- effective latency;
- effective loss proxy;
- effective delay-variation proxy;
- route blocking ratio.

The template records each metric's runtime summary key, layer, unit, source
fields, formula summary, zero-value semantics, and verification method.

Compute service-time checks are derived from `compute_resource_contract_v2`.
The current estimator is:

```text
MAX_ACTIVE_RESOURCE_LANE_TIME
```

The report template requires queue delay and execution delay to be checked
against the deterministic bottleneck resource estimator and configured compute
resource vector.

## Scenario Boundaries

For each benchmark scenario, the template records:

- satellite count;
- user count;
- compute node count;
- runtime duration;
- deterministic seed;
- orbit update interval;
- orbit plane count;
- application protocol;
- traffic class;
- traffic destination type;
- orbit update mode;
- metrics mode;
- space link mode;
- scale limit reason.

The 1200-satellite benchmark is expected to report `BATCH` orbit updates,
`AGGREGATED` metrics, and `BOUNDED_CANDIDATE` space-space links.

## Expected Evidence

Each scenario should collect:

- config loading result;
- backend summary determinism result;
- live runtime smoke result;
- route trust acceptance result comparing `route_provenance_trust_summary_v1`
  with `route_explanation_summary_v1`;
- artifact manifest for config snapshot, `events.jsonl`, `metrics.csv`, and
  `summary.json`.

## Review Decision Values

- `PASS`
- `PASS_WITH_LIMITATIONS`
- `FAIL_MODEL_DRIFT`
- `FAIL_NON_DETERMINISTIC`
- `FAIL_SCOPE_VIOLATION`

## Scope Boundaries

The report template preserves the project constraints:

- Event Kernel behavior is unchanged.
- STK, EXATA, AFSIM, and DDS remain forbidden.
- Packet-level simulation is not introduced.
- Network KPIs remain flow-level proxies.
- Compute timing remains deterministic capacity-vector estimation, not real
  code execution.
