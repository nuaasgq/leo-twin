# Traffic Arrival Profiles v2

Date: 2026-07-06
Branch: `feature/T253-traffic-arrival-profiles-v2`

## Goal

Implement deterministic arrival profiles for user business demand. This builds
on `leo_twin.service_request_contract.v2` and keeps existing `PERIODIC`
traffic generation compatible.

## Supported Profiles

`TrafficArrivalProfile` now supports:

- `PERIODIC`: existing fixed interval behavior.
- `BURST`: groups requests into deterministic bursts with configurable
  `burst_size` and `burst_spacing`.
- `DIURNAL`: varies inter-arrival spacing over a configured period using
  `diurnal_peak_time` and `diurnal_amplitude`.
- `REGION_WEIGHTED`: uses seeded deterministic weighted source/destination
  selection through `source_region_weights` and `destination_region_weights`.

All profiles are deterministic for identical configuration and seed.

## Runtime Boundaries

This task changes only traffic demand generation. It does not change Event
Kernel ordering, network routing, compute placement, metrics formulas, or
frontend rendering.

## Compatibility

Existing `TrafficDemandProfile` instances keep `PERIODIC` as the default. If no
weights are supplied, source and destination selection remains round-robin.

## Verification

Unit tests cover:

- unchanged periodic behavior;
- burst arrival grouping;
- deterministic diurnal time variation;
- seeded weighted source/destination selection;
- validation of burst, diurnal, and weight parameters.
