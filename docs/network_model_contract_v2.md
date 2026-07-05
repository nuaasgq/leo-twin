# Network Model Contract v2

Date: 2026-07-05
Contract id: `leo_twin.network_model_contract.v2`

## Purpose

Network Model Contract v2 defines the product semantics of the SEES network
model before further KPI work. It explains how the current simulator separates
application demand, transport abstraction, routing/topology, data-link effects,
physical terminal inputs, and channel abstraction.

This is a contract and documentation task. It does not change Event Kernel
behavior, route computation, link updates, or metric formulas.

## Fidelity Boundary

The current network model remains:

- deterministic;
- event-driven;
- flow-level;
- route/link-state based;
- configuration-driven.

It explicitly does not implement:

- packet-level simulation;
- external network simulators;
- EXATA, GloMoSim, STK, AFSIM, or DDS;
- RF propagation field solving;
- antenna pattern simulation;
- TCP retransmission state machines;
- frame-level MAC scheduling.

## Layer Contract

The canonical product stack is:

1. Application
2. Transport
3. Network / routing
4. Data link
5. Physical terminal abstraction
6. Channel abstraction

Each layer has a deterministic responsibility, input contracts, output
contracts, state sources, and excluded semantics. The authoritative runtime
contract is exposed by:

```python
network_model_contract_v2_to_dict()
```

Generated scenario summaries include the same object under:

```text
backend_summary.network_model_contract_v2
```

## KPI Contract

The v2 contract defines source semantics for these user-facing KPI families:

- effective throughput;
- effective latency;
- effective loss proxy;
- effective delay-variation proxy;
- route blocking ratio;
- congestion pressure proxy.

Every KPI contract includes:

- runtime summary key;
- display name;
- owning layer;
- unit;
- source fields;
- formula summary;
- interpretation;
- zero-value semantics;
- `packet_level_metric: false`.

This makes clear that loss and delay variation are flow-level proxies. They are
not packet loss or packet inter-arrival jitter.

## Configured Protocol Profile

Backend-derived summaries attach the current configured protocol names:

```text
configured_protocol_profile.application_protocol
configured_protocol_profile.transport_protocol
configured_protocol_profile.routing_protocol
configured_protocol_profile.datalink_mac_protocol
```

Frontend components should use this backend field instead of inferring protocol
semantics locally.

## Next Step

V2-021 should add a KPI provenance contract that binds these semantic fields to
the existing runtime status and dashboard displays. V2-022 can then improve the
time-varying formula inputs without changing the Event Kernel.
