from __future__ import annotations

import gc

from leo_twin.services.scenario_builder import (
    FullSystemScenarioBuilderConfig,
    GeneratedFullSystemScenario,
    build_full_system_scenario,
)


def test_generated_scenario_builder_handles_10k_satellite_100k_user_config() -> None:
    config = FullSystemScenarioBuilderConfig(
        seed=20260704,
        satellite_count=10_000,
        user_count=100_000,
        compute_node_count=64,
        flow_count=256,
        orbit_plane_count=100,
    )

    first = build_full_system_scenario(config)
    first_signature = _scenario_signature(first)
    assert len(first.orbit_elements) == 10_000
    assert len(first.ground_endpoints) == 100_000
    assert len(first.compute_nodes) == 64
    assert len(first.flows) == 256
    assert len(first.tasks) == 256

    del first
    gc.collect()

    second = build_full_system_scenario(config)

    assert _scenario_signature(second) == first_signature


def _scenario_signature(scenario: GeneratedFullSystemScenario) -> tuple[object, ...]:
    first_satellite = scenario.orbit_elements[0]
    last_satellite = scenario.orbit_elements[-1]
    first_user = scenario.ground_endpoints[0]
    last_user = scenario.ground_endpoints[-1]
    first_flow = scenario.flows[0]
    last_flow = scenario.flows[-1]
    return (
        first_satellite.satellite_id,
        round(first_satellite.raan_deg, 6),
        round(first_satellite.mean_anomaly_deg, 6),
        last_satellite.satellite_id,
        round(last_satellite.raan_deg, 6),
        round(last_satellite.mean_anomaly_deg, 6),
        first_user.endpoint_id,
        tuple(round(value, 6) for value in first_user.position),
        last_user.endpoint_id,
        tuple(round(value, 6) for value in last_user.position),
        first_flow,
        last_flow,
    )
