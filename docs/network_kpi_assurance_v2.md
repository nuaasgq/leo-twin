# Network KPI Assurance v2

`network_kpi_assurance_v2` is a backend-owned product summary for network KPI
trust, movement, and display readiness.

## Sources

- `network_kpi_provenance_v2`
- `network_kpi_credibility_v1`
- `network_kpi_calibration_v1`
- `network_kpi_dynamic_status_v1`
- `network_kpi_formula_evidence_v1`
- `network_kpi_variation_explanation_v1`
- `metrics_summary`

The summary joins existing evidence. It does not recompute throughput, latency,
loss, or delay-variation formulas.

## Assurance Status

- `TIME_VARYING_FLOW_PROXY_READY`: KPI time series moves and formula evidence is
  present.
- `TIME_VARYING_PARTIAL_EVIDENCE`: KPI time series moves, but formula evidence is
  partial.
- `FLAT_UNDER_ACTIVITY_EXPLAINED`: business activity exists, but the KPI proxy
  inputs are flat or zero and the backend explains why.
- `FLAT_NO_ACTIVITY_EXPLAINED`: KPI proxy samples are flat because no active
  demand context is observed.
- `NEEDS_MORE_RUNTIME_SAMPLES`: more samples are required before movement can be
  assessed.
- `MISSING_BACKEND_EVIDENCE`: one or more KPI rows lack backend evidence.
- `INVALID_PACKET_LEVEL_EVIDENCE`: packet-level evidence was marked present,
  which is outside the current product contract.

## Frontend Contract

Frontend consumers should use:

- `assurance_status`
- `recommended_next_action`
- `items[].display_policy`
- `items[].variation_status`
- `items[].assurance_item_status`
- `items[].flat_reason`
- `items[].zero_value_note`
- `items[].user_explanation`
- `assurance_hash`

`frontend_inference_required` is `false`. The frontend should not infer KPI
trust status locally when this backend field is available.

## Boundaries

- The current model remains deterministic and flow-level.
- Loss proxy is not packet loss.
- Delay-variation proxy is not packet jitter.
- Packet-level queues, retransmissions, RF propagation, antenna patterns, and
  external simulators are not modeled.
- Event Kernel behavior is unchanged.
