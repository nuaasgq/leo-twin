from __future__ import annotations

import json

import pytest

from leo_twin.services.scenario_builder import (
    FullSystemScenarioBuilderConfig,
    build_full_system_scenario,
    load_full_system_scenario_builder_config,
    scenario_builder_backend_summary,
    scenario_builder_config_from_sees_config,
    scenario_builder_config_from_mapping,
    scenario_builder_config_to_mapping,
    write_full_system_scenario_builder_config,
)
from leo_twin.schema.config import (
    NetworkProfile,
    OrbitParameters,
    RuntimeConfig,
    SEESConfig,
    ScenarioConfig,
    TrafficModel,
)
from leo_twin.schema import ApplicationProtocol, RoutingProtocol, TransportProtocol


def test_full_system_scenario_builder_generates_requested_counts() -> None:
    config = FullSystemScenarioBuilderConfig(
        seed=7,
        satellite_count=8,
        user_count=12,
        compute_node_count=3,
        flow_count=5,
        orbit_plane_count=4,
    )

    scenario = build_full_system_scenario(config)

    assert len(scenario.orbit_elements) == 8
    assert len(scenario.ground_endpoints) == 12
    assert len(scenario.compute_nodes) == 3
    assert len(scenario.flows) == 5
    assert len(scenario.tasks) == 5
    assert scenario.orbit_elements[0].satellite_id == "sat-00000"
    assert scenario.ground_endpoints[0].endpoint_id == "user-00000"
    assert scenario.compute_nodes[-1].node_id == "sat-00002"
    assert {node.node_id for node in scenario.compute_nodes} <= {
        element.satellite_id for element in scenario.orbit_elements
    }


def test_full_system_scenario_builder_is_deterministic() -> None:
    config = FullSystemScenarioBuilderConfig(
        seed=99,
        satellite_count=6,
        user_count=4,
        compute_node_count=2,
        flow_count=4,
        orbit_plane_count=3,
    )

    assert build_full_system_scenario(config) == build_full_system_scenario(config)


def test_full_system_scenario_builder_seed_changes_initial_phase() -> None:
    base = FullSystemScenarioBuilderConfig(
        seed=1,
        satellite_count=4,
        user_count=4,
        compute_node_count=2,
        flow_count=2,
        orbit_plane_count=2,
    )
    shifted = FullSystemScenarioBuilderConfig(
        seed=2,
        satellite_count=4,
        user_count=4,
        compute_node_count=2,
        flow_count=2,
        orbit_plane_count=2,
    )

    first = build_full_system_scenario(base)
    second = build_full_system_scenario(shifted)

    assert first.orbit_elements[0].raan_deg != second.orbit_elements[0].raan_deg
    assert first.orbit_elements[0].mean_anomaly_deg != second.orbit_elements[0].mean_anomaly_deg
    assert first.ground_endpoints[0].position != second.ground_endpoints[0].position


def test_full_system_scenario_builder_aligns_flows_and_tasks() -> None:
    config = FullSystemScenarioBuilderConfig(
        satellite_count=4,
        user_count=3,
        compute_node_count=2,
        flow_count=6,
        orbit_plane_count=2,
        demand_capacity=2.5,
        task_compute_demand=12.0,
        task_data_size=4.0,
    )

    scenario = build_full_system_scenario(config)

    assert tuple(flow.flow_id for flow in scenario.flows) == tuple(
        task.task_id for task in scenario.tasks
    )
    assert tuple(flow.source_id for flow in scenario.flows) == tuple(
        task.source_id for task in scenario.tasks
    )
    assert tuple(flow.target_id for flow in scenario.flows) == (
        "sat-00000",
        "sat-00001",
        "sat-00000",
        "sat-00001",
        "sat-00000",
        "sat-00001",
    )
    assert scenario.flows[0].demand_capacity == 2.5
    assert scenario.tasks[0].compute_demand == 12.0
    assert scenario.tasks[0].data_size == 4.0


def test_full_system_scenario_builder_rejects_invalid_config() -> None:
    with pytest.raises(ValueError, match="orbit_plane_count"):
        FullSystemScenarioBuilderConfig(
            satellite_count=2,
            user_count=2,
            compute_node_count=1,
            orbit_plane_count=3,
        )

    with pytest.raises(ValueError, match="flow_count"):
        FullSystemScenarioBuilderConfig(flow_count=-1)

    with pytest.raises(ValueError, match="compute_scheduling_policy"):
        FullSystemScenarioBuilderConfig(compute_scheduling_policy="RANDOM")

    with pytest.raises(ValueError, match="orbit_propagation_model"):
        FullSystemScenarioBuilderConfig(orbit_propagation_model="SGP4")


def test_scenario_builder_config_from_mapping_rejects_unknown_fields() -> None:
    with pytest.raises(ValueError, match="unknown scenario builder fields"):
        scenario_builder_config_from_mapping({"satellite_count": 4, "unexpected": 1})


def test_load_full_system_scenario_builder_config_from_json(tmp_path) -> None:
    config_path = tmp_path / "scenario.json"
    config_path.write_text(
        json.dumps(
            {
                "seed": 5,
                "satellite_count": 4,
                "user_count": 8,
                "compute_node_count": 2,
                "flow_count": 3,
                "orbit_plane_count": 2,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    config = load_full_system_scenario_builder_config(config_path)

    assert config.seed == 5
    assert config.satellite_count == 4
    assert config.user_count == 8
    assert config.compute_node_count == 2
    assert config.flow_count == 3
    assert config.compute_scheduling_policy == "FIFO"
    assert config.orbit_plane_count == 2
    assert config.orbit_plane_count_explicit is True
    assert config.constellation_profile == "CUSTOM_WALKER"
    assert config.orbit_propagation_model == "KEPLERIAN"
    assert config.earth_rotation_rate_rad_s == 0.0
    assert config.space_link_max_range_km == 0.0
    assert config.space_link_capacity == 100.0
    assert config.space_link_cell_size_km == 0.0
    assert config.space_link_mode is None
    assert config.max_space_link_candidates_per_satellite == 4
    assert config.batch_space_link_update_limit == 999
    assert config.max_range_km == 2000.0
    assert config.application_protocol == "TASK_OFFLOAD_FLOW"
    assert config.transport_protocol == "TCP"
    assert config.transport_loss_rate == 0.0
    assert config.transport_congestion_window_segments == 0
    assert config.routing_protocol == "LINK_STATE"
    assert config.routing_latency_weight == 1.0
    assert config.routing_inverse_capacity_weight == 0.0
    assert config.routing_hop_weight == 0.0
    assert config.carrier_frequency_hz == 20_000_000_000.0
    assert config.channel_bandwidth_hz == 100_000_000.0
    assert config.rain_rate_mm_h == 0.0
    assert config.antenna_diameter_m == 0.45
    assert config.antenna_aperture_efficiency == 0.65
    assert config.transmit_power_dbw == 20.0
    assert config.system_loss_db == 1.0
    assert config.noise_temperature_k == 290.0


def test_write_full_system_scenario_builder_config_round_trips(tmp_path) -> None:
    config = FullSystemScenarioBuilderConfig(
        seed=6,
        satellite_count=5,
        user_count=7,
        compute_node_count=2,
        flow_count=3,
        orbit_plane_count=1,
        orbit_propagation_model="J2_SECULAR",
    )
    config_path = tmp_path / "generated.json"

    write_full_system_scenario_builder_config(config_path, config)

    assert load_full_system_scenario_builder_config(config_path) == config
    assert json.loads(config_path.read_text(encoding="utf-8")) == (
        scenario_builder_config_to_mapping(config)
    )


def test_full_system_scenario_builder_auto_allocates_starlink_like_planes() -> None:
    config = scenario_builder_config_from_mapping(
        {
            "satellite_count": 1584,
            "user_count": 10,
            "compute_node_count": 4,
            "flow_count": 4,
            "constellation_profile": "STARLINK_SHELL_1_LIKE",
        }
    )

    scenario = build_full_system_scenario(config)

    assert config.orbit_plane_count_explicit is False
    assert scenario.constellation_summary["profile"] == "STARLINK_SHELL_1_LIKE"
    assert scenario.constellation_summary["plane_count"] == 72
    assert scenario.constellation_summary["satellites_per_plane"] == 22
    assert scenario.constellation_summary["model_note"] == (
        "Approximate Starlink Shell 1-like plane allocation; not exact Starlink fidelity."
    )
    assert scenario.orbit_elements[72].raan_deg == scenario.orbit_elements[0].raan_deg
    assert scenario.orbit_elements[72].mean_anomaly_deg != scenario.orbit_elements[
        0
    ].mean_anomaly_deg


def test_scenario_builder_config_from_sees_config_maps_control_plane_fields() -> None:
    config = SEESConfig(
        scenario=ScenarioConfig(
            satellite_count=24,
            user_count=40,
            compute_nodes=3,
            compute_capacity=18.0,
            compute_cpu_gflops_fp64=6.0,
            compute_gpu_tflops_fp32=2.5,
            compute_gpu_tflops_fp16=5.0,
            compute_npu_tops_int8=12.0,
            compute_memory_gb=32.0,
            compute_storage_gb=512.0,
            compute_scheduling_policy="EARLIEST_DEADLINE_FIRST",
            orbit=OrbitParameters(
                plane_count=4,
                altitude_m=600_000.0,
                inclination_deg=55.0,
            ),
            traffic_model=TrafficModel(
                flow_interval_seconds=30,
                task_compute_demand=15.0,
                flow_demand_capacity=2.5,
                traffic_class="TELEMETRY",
                destination_type="GROUND_ENDPOINT",
                output_data_size=1.5,
                telemetry_weight=3.0,
                bulk_downlink_weight=1.0,
            ),
        ),
        runtime=RuntimeConfig(seed=42, duration=300),
        network=NetworkProfile(
            application_protocol=ApplicationProtocol.MQTT,
            transport_protocol=TransportProtocol.UDP,
            transport_loss_rate=0.025,
            transport_congestion_window_segments=32,
            routing_protocol=RoutingProtocol.DISTANCE_VECTOR,
            routing_latency_weight=0.2,
            routing_inverse_capacity_weight=400.0,
            routing_hop_weight=1.0,
            carrier_frequency_hz=22_000_000_000.0,
            channel_bandwidth_hz=250_000_000.0,
            rain_rate_mm_h=12.5,
            rain_attenuation_coefficient_db_per_km_per_mm_h=0.015,
            rain_effective_path_km=4.0,
            antenna_diameter_m=0.55,
            antenna_aperture_efficiency=0.7,
            transmit_power_dbw=23.0,
            system_loss_db=1.5,
            noise_temperature_k=310.0,
            space_link_mode="BOUNDED_CANDIDATE",
            max_space_link_candidates_per_satellite=6,
            batch_space_link_update_limit=500,
        ),
    )

    generated = scenario_builder_config_from_sees_config(config)

    assert generated.seed == 42
    assert generated.satellite_count == 24
    assert generated.user_count == 40
    assert generated.compute_node_count == 3
    assert generated.compute_capacity == 18.0
    assert generated.compute_cpu_gflops_fp64 == 6.0
    assert generated.compute_gpu_tflops_fp32 == 2.5
    assert generated.compute_gpu_tflops_fp16 == 5.0
    assert generated.compute_npu_tops_int8 == 12.0
    assert generated.compute_memory_gb == 32.0
    assert generated.compute_storage_gb == 512.0
    assert generated.flow_count == 10
    assert generated.flow_interval_seconds == 30
    assert generated.task_interval_seconds == 60
    assert generated.runtime_duration_seconds == 300
    assert generated.compute_scheduling_policy == "EARLIEST_DEADLINE_FIRST"
    assert generated.orbit_plane_count == 4
    assert generated.orbit_propagation_model == "KEPLERIAN"
    assert generated.semi_major_axis_km == 6971.0
    assert generated.inclination_deg == 55.0
    assert generated.demand_capacity == 2.5
    assert generated.task_compute_demand == 15.0
    assert generated.traffic_class == "TELEMETRY"
    assert generated.traffic_destination_type == "GROUND_ENDPOINT"
    assert generated.traffic_output_data_size == 1.5
    assert generated.traffic_data_transfer_weight == 0.0
    assert generated.traffic_telemetry_weight == 3.0
    assert generated.traffic_bulk_downlink_weight == 1.0
    assert generated.traffic_compute_service_weight == 0.0
    assert generated.traffic_emergency_weight == 0.0
    assert generated.application_protocol == "MQTT"
    assert generated.transport_protocol == "UDP"
    assert generated.transport_loss_rate == 0.025
    assert generated.transport_congestion_window_segments == 32
    assert generated.routing_protocol == "DISTANCE_VECTOR"
    assert generated.routing_latency_weight == 0.2
    assert generated.routing_inverse_capacity_weight == 400.0
    assert generated.routing_hop_weight == 1.0
    assert generated.carrier_frequency_hz == 22_000_000_000.0
    assert generated.channel_bandwidth_hz == 250_000_000.0
    assert generated.rain_rate_mm_h == 12.5
    assert generated.antenna_diameter_m == 0.55
    assert generated.antenna_aperture_efficiency == 0.7
    assert generated.transmit_power_dbw == 23.0
    assert generated.system_loss_db == 1.5
    assert generated.noise_temperature_k == 310.0
    assert generated.space_link_mode == "BOUNDED_CANDIDATE"
    assert generated.max_space_link_candidates_per_satellite == 6
    assert generated.batch_space_link_update_limit == 500


def test_scenario_builder_backend_summary_reports_effective_schedule_semantics() -> None:
    config = FullSystemScenarioBuilderConfig(
        traffic_class="COMPUTE_SERVICE",
        traffic_destination_type="COMPUTE_NODE",
        flow_count=4,
        flow_interval_seconds=10,
        task_interval_seconds=30,
        runtime_duration_seconds=120,
    )

    summary = scenario_builder_backend_summary(config)
    schedule = summary["traffic_schedule_semantics_v1"]
    traffic = summary["traffic_demand_summary"]

    assert schedule["effective_arrival_interval_seconds"] == 30.0
    assert schedule["effective_arrival_interval_source"] == (
        "scenario.traffic_model.task_interval_seconds"
    )
    assert schedule["flow_arrival_schedule_source"] == (
        "scenario.traffic_model.task_interval_seconds"
    )
    assert schedule["task_arrival_schedule_source"] == (
        "scenario.traffic_model.task_interval_seconds"
    )
    assert schedule["schedule_policy"] == "CORRELATED_INPUT_FLOW_AND_TASK_INTERVAL"
    assert schedule["configured_flow_interval_seconds"] == 10.0
    assert schedule["configured_task_interval_seconds"] == 30.0
    assert traffic["arrival_interval_seconds"] == 30.0
    assert traffic["effective_arrival_interval_source"] == (
        "scenario.traffic_model.task_interval_seconds"
    )


def test_default_generated_scenario_config_file_loads() -> None:
    config = load_full_system_scenario_builder_config()

    assert config.satellite_count == 6
    assert config.user_count == 12
    assert config.compute_node_count == 3
    assert config.flow_count == 6
    assert config.earth_rotation_rate_rad_s == 0.000072921159
    assert config.space_link_max_range_km == 0.0
