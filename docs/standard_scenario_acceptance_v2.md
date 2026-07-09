# Standard Scenario Acceptance v2

Date: 2026-07-09
Branch: `feature/T447-standard-scenario-acceptance-v2`

`standard_scenario_acceptance_v2` is a backend-owned runtime evidence object for
the shipped industrial v2 demo baselines:

- `small_demo_72sat`
- `medium_demo_300sat`
- `scale_demo_1200sat_short`

The evidence is derived from the existing benchmark scenario matrix, the active
SEES configuration, generated backend summaries, and runtime status fields. It
does not advance the simulation, replay events, recompute network routes, modify
the Event Kernel, or use packet-level simulation.

## Runtime Status Field

The integration demo status now includes:

```text
standard_scenario_acceptance_v2
```

Key fields:

- `current_scenario_id`
- `nearest_scenario_id`
- `matched_standard_scenario`
- `match_status`
- `acceptance_status`
- `gate_checks`
- `scenario_results`
- `missing_runtime_status_fields`
- `result_package_evidence_filenames`
- `acceptance_hash`

For an exact standard scenario match with complete runtime evidence,
`acceptance_status` is `PASS`. Custom or partial scenarios remain runnable but
are marked `WARN` rather than being misrepresented as a standard benchmark.

## Result Package Artifact

Runtime export packages now include:

```text
standard_scenario_acceptance_v2.json
```

The file copies `config_snapshot.status.standard_scenario_acceptance_v2` as a
standalone runtime-status evidence snapshot. It is listed in the result package
contract, artifact browser, reproducibility boundary optional evidence, and
scenario review order.

## Boundaries

- Event Kernel behavior is unchanged.
- The evidence uses deterministic flow-level acceptance guardrails only.
- No DDS, STK, EXATA, AFSIM, RF model, or packet-level simulation is introduced.
- Frontend inference is not required for the standard scenario match.
