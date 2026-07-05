from __future__ import annotations

import json
from pathlib import Path

import pytest

from examples.integration_demo.config import DemoConfig, demo_config_from_sees_config
from examples.integration_demo.control_plane import DemoControlPlane
from examples.integration_demo.runtime import (
    build_integration_demo_runtime,
    run_integration_demo,
)
from leo_twin.core.config import ConfigValidationError, config_from_mapping, load_config
from leo_twin.schema.config import OrbitParameters, RuntimeConfig, ScenarioConfig, SEESConfig
from leo_twin.services.control import RuntimeController, ScaleSafetyChecker
from leo_twin.services.configuration_schema import USER_CONFIGURATION_SCHEMA_V2_ID
from leo_twin.services.configuration_view import load_user_configuration_template


def test_config_loads_correctly() -> None:
    config = load_config("configs/sees_control.yaml")

    assert config.scenario.satellite_count == 72
    assert config.scenario.user_count == 1000
    assert config.scenario.compute_nodes == 10
    assert config.scenario.compute_scheduling_policy == "FIFO"
    assert config.runtime.mode == "REAL_TIME"
    assert config.runtime.speed_factor == 1.0
    assert config.network.application_protocol == "TASK_OFFLOAD_FLOW"
    assert config.network.transport_protocol == "TCP"
    assert config.network.transport_loss_rate == 0.0
    assert config.network.transport_congestion_window_segments == 0
    assert config.network.routing_protocol == "LINK_STATE"
    assert config.network.datalink_mac_protocol == "TDMA"
    assert config.network.routing_latency_weight == 1.0
    assert config.network.routing_inverse_capacity_weight == 0.0
    assert config.network.routing_hop_weight == 0.0
    assert config.network.antenna_diameter_m == 0.45
    assert config.network.antenna_aperture_efficiency == 0.65
    assert config.network.transmit_power_dbw == 20.0
    assert config.network.system_loss_db == 1.0
    assert config.network.noise_temperature_k == 290.0
    assert config.network.space_link_mode is None
    assert config.network.max_space_link_candidates_per_satellite == 4
    assert config.network.batch_space_link_update_limit == 999
    assert config.scenario.traffic_model.traffic_class == "COMPUTE_SERVICE"
    assert config.scenario.traffic_model.destination_type == "COMPUTE_NODE"
    assert config.scenario.traffic_model.output_data_size == 0.0
    assert config.ui.visualization.satellites is True


def test_invalid_config_is_rejected() -> None:
    with pytest.raises(ConfigValidationError):
        config_from_mapping({"scenario": {"satellite_count": 0}})

    with pytest.raises(ConfigValidationError):
        config_from_mapping({"scenario": {"unknown_field": 1}})

    with pytest.raises(ConfigValidationError):
        config_from_mapping({"network": {"transport_protocol": "SCTP"}})

    with pytest.raises(ConfigValidationError, match="destination_type"):
        config_from_mapping(
            {
                "scenario": {
                    "traffic_model": {
                        "traffic_class": "COMPUTE_SERVICE",
                        "destination_type": "GROUND_ENDPOINT",
                    }
                }
            }
        )


def test_network_protocol_profile_can_be_updated_directly() -> None:
    controller = RuntimeController(load_config("configs/sees_control.yaml"))
    snapshot = controller.update_config(
        {
            "application_protocol": "MQTT",
            "transport_protocol": "UDP",
            "transport_loss_rate": 0.025,
            "transport_congestion_window_segments": 32,
            "routing_protocol": "DISTANCE_VECTOR",
            "datalink_mac_protocol": "SLOTTED_ALOHA",
            "routing_latency_weight": 0.2,
            "routing_inverse_capacity_weight": 400.0,
            "routing_hop_weight": 1.0,
            "carrier_frequency_hz": 22_000_000_000.0,
            "channel_bandwidth_hz": 250_000_000.0,
            "rain_rate_mm_h": 12.5,
            "rain_attenuation_coefficient_db_per_km_per_mm_h": 0.015,
            "rain_effective_path_km": 4.0,
            "antenna_diameter_m": 0.55,
            "antenna_aperture_efficiency": 0.7,
            "transmit_power_dbw": 23.0,
            "system_loss_db": 1.5,
            "noise_temperature_k": 310.0,
            "space_link_mode": "BOUNDED_CANDIDATE",
            "max_space_link_candidates_per_satellite": 6,
            "batch_space_link_update_limit": 500,
            "compute_scheduling_policy": "SHORTEST_JOB_FIRST",
        }
    )

    assert snapshot.last_action == "CONFIG_UPDATE"
    assert controller.config.network.application_protocol == "MQTT"
    assert controller.config.network.transport_protocol == "UDP"
    assert controller.config.network.transport_loss_rate == 0.025
    assert controller.config.network.transport_congestion_window_segments == 32
    assert controller.config.network.routing_protocol == "DISTANCE_VECTOR"
    assert controller.config.network.datalink_mac_protocol == "SLOTTED_ALOHA"
    assert controller.config.network.routing_latency_weight == 0.2
    assert controller.config.network.routing_inverse_capacity_weight == 400.0
    assert controller.config.network.routing_hop_weight == 1.0
    assert controller.config.network.carrier_frequency_hz == 22_000_000_000.0
    assert controller.config.network.channel_bandwidth_hz == 250_000_000.0
    assert controller.config.network.rain_rate_mm_h == 12.5
    assert controller.config.network.antenna_diameter_m == 0.55
    assert controller.config.network.antenna_aperture_efficiency == 0.7
    assert controller.config.network.transmit_power_dbw == 23.0
    assert controller.config.network.system_loss_db == 1.5
    assert controller.config.network.noise_temperature_k == 310.0
    assert controller.config.network.space_link_mode == "BOUNDED_CANDIDATE"
    assert controller.config.network.max_space_link_candidates_per_satellite == 6
    assert controller.config.network.batch_space_link_update_limit == 500
    assert controller.config.scenario.compute_scheduling_policy == "SHORTEST_JOB_FIRST"


def test_runtime_mode_switching_works() -> None:
    controller = RuntimeController(load_config("configs/sees_control.yaml"))

    accelerated = controller.handle_action(
        "SET_MODE",
        {"mode": "ACCELERATED"},
    )
    assert accelerated.mode == "ACCELERATED"
    assert controller.handle_action("SET_SPEED", {"speed_factor": 25}).speed_factor == 25
    assert controller.handle_action("START").status == "RUNNING"
    try:
        controller.handle_action("SET_SPEED", {"speed_factor": 50})
    except RuntimeError as exc:
        assert "cannot be changed while runtime is running" in str(exc)
    else:
        raise AssertionError("running runtime controller must reject live speed changes")
    assert controller.handle_action("PAUSE").status == "PAUSED"
    assert controller.handle_action("SET_SPEED", {"speed_factor": 10}).speed_factor == 10
    assert controller.handle_action("STOP").status == "STOPPED"


def test_runtime_start_can_be_guarded_by_scale_safety() -> None:
    safe_controller = RuntimeController(
        load_config("configs/sees_control.yaml"),
        scale_safety_checker=ScaleSafetyChecker(),
    )

    assert safe_controller.start().status == "RUNNING"

    unsafe_controller = RuntimeController(
        SEESConfig(
            scenario=ScenarioConfig(
                satellite_count=10_000,
                user_count=100_000,
                compute_nodes=10,
                cell_count=1000,
                orbit=OrbitParameters(update_interval_seconds=1),
            ),
            runtime=RuntimeConfig(duration=1000),
        ),
        scale_safety_checker=ScaleSafetyChecker(),
    )

    with pytest.raises(RuntimeError, match="scale safety check failed"):
        unsafe_controller.start()

    assert unsafe_controller.snapshot().status == "STOPPED"
    assert unsafe_controller.snapshot().last_action == "INIT"


def test_frontend_control_messages_are_processed(tmp_path) -> None:
    control_plane = _small_control_plane(tmp_path / "sees_control.yaml")

    ack = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "CONFIG_UPDATE",
                "payload": {
                    "satellite_count": 24,
                    "user_count": 40,
                    "compute_nodes": 3,
                    "compute_capacity": 18.0,
                    "compute_cpu_gflops_fp64": 6.0,
                    "compute_gpu_tflops_fp32": 2.5,
                    "compute_gpu_tflops_fp16": 5.0,
                    "compute_npu_tops_int8": 12.0,
                    "compute_memory_gb": 32.0,
                    "compute_storage_gb": 512.0,
                    "orbit": {
                        "update_interval_seconds": 30,
                        "plane_count": 6,
                        "altitude_m": 600_000.0,
                        "inclination_deg": 55.0,
                    },
                    "traffic_model": {
                        "flow_interval_seconds": 30,
                        "task_interval_seconds": 45,
                        "flow_demand_capacity": 12.5,
                        "task_compute_demand": 15.0,
                        "task_data_size": 4.0,
                        "traffic_class": "BULK_DOWNLINK",
                        "destination_type": "GROUND_ENDPOINT",
                        "output_data_size": 3.5,
                    },
                    "application_protocol": "MQTT",
                    "transport_protocol": "UDP",
                    "transport_loss_rate": 0.025,
                    "transport_congestion_window_segments": 32,
                    "routing_protocol": "DISTANCE_VECTOR",
                    "datalink_mac_protocol": "SLOTTED_ALOHA",
                    "routing_latency_weight": 0.2,
                    "routing_inverse_capacity_weight": 400.0,
                    "routing_hop_weight": 1.0,
                    "carrier_frequency_hz": 22_000_000_000.0,
                    "channel_bandwidth_hz": 250_000_000.0,
                    "rain_rate_mm_h": 12.5,
                    "rain_attenuation_coefficient_db_per_km_per_mm_h": 0.015,
                    "rain_effective_path_km": 4.0,
                    "antenna_diameter_m": 0.55,
                    "antenna_aperture_efficiency": 0.7,
                    "transmit_power_dbw": 23.0,
                    "system_loss_db": 1.5,
                    "noise_temperature_k": 310.0,
                    "space_link_mode": "BOUNDED_CANDIDATE",
                    "max_space_link_candidates_per_satellite": 6,
                    "batch_space_link_update_limit": 500,
                    "compute_scheduling_policy": "SHORTEST_JOB_FIRST",
                },
            }
        )
    )
    assert ack["ok"] is True
    assert ack["status"]["last_action"] == "INITIALIZE"
    assert control_plane.result.config.satellite_count == 24
    assert len(control_plane.result.scenario.orbit_satellites) == 24
    assert control_plane.result.config.ground_user_count == 40
    assert control_plane.result.config.compute_capacity == 18.0
    assert control_plane.result.config.compute_cpu_gflops_fp64 == 6.0
    assert control_plane.result.config.compute_gpu_tflops_fp32 == 2.5
    assert control_plane.result.config.compute_gpu_tflops_fp16 == 5.0
    assert control_plane.result.config.compute_npu_tops_int8 == 12.0
    assert control_plane.result.config.compute_memory_gb == 32.0
    assert control_plane.result.config.compute_storage_gb == 512.0
    assert control_plane.result.scenario.compute_nodes[0].capacity == 18.0
    assert control_plane.result.config.orbit_tick_seconds == 30
    assert control_plane.result.config.orbit_plane_count == 6
    assert control_plane.result.config.orbit_altitude_m == 600_000.0
    assert control_plane.result.config.orbit_inclination_deg == 55.0
    assert control_plane.result.config.flow_interval_seconds == 30
    assert control_plane.result.config.task_interval_seconds == 45
    assert control_plane.result.config.flow_demand_capacity == 12.5
    assert control_plane.result.config.task_compute_demand == 15.0
    assert control_plane.result.config.task_data_size == 4.0
    assert control_plane.result.config.traffic_class == "BULK_DOWNLINK"
    assert control_plane.result.config.traffic_destination_type == "GROUND_ENDPOINT"
    assert control_plane.result.config.traffic_output_data_size == 3.5
    assert control_plane.result.config.transport_protocol == "UDP"
    assert control_plane.result.config.application_protocol == "MQTT"
    assert control_plane.result.config.routing_protocol == "DISTANCE_VECTOR"
    assert control_plane.result.config.transport_loss_rate == 0.025
    assert control_plane.result.config.transport_congestion_window_segments == 32
    assert control_plane.result.config.datalink_mac_protocol == "SLOTTED_ALOHA"
    assert control_plane.result.config.routing_latency_weight == 0.2
    assert control_plane.result.config.routing_inverse_capacity_weight == 400.0
    assert control_plane.result.config.routing_hop_weight == 1.0
    assert control_plane.result.config.carrier_frequency_hz == 22_000_000_000.0
    assert control_plane.result.config.channel_bandwidth_hz == 250_000_000.0
    assert control_plane.result.config.rain_rate_mm_h == 12.5
    assert control_plane.result.config.antenna_diameter_m == 0.55
    assert control_plane.result.config.antenna_aperture_efficiency == 0.7
    assert control_plane.result.config.transmit_power_dbw == 23.0
    assert control_plane.result.config.system_loss_db == 1.5
    assert control_plane.result.config.noise_temperature_k == 310.0
    assert control_plane.result.config.space_link_mode == "BOUNDED_CANDIDATE"
    assert control_plane.result.config.max_space_link_candidates_per_satellite == 6
    assert control_plane.result.config.batch_space_link_update_limit == 500
    assert control_plane.result.config.compute_scheduling_policy == "SHORTEST_JOB_FIRST"
    assert control_plane.result.scenario.frontend_config["scenario"][
        "compute_scheduling_policy"
    ] == "SHORTEST_JOB_FIRST"
    assert control_plane.result.scenario.frontend_config["scenario"][
        "compute_capacity"
    ] == 18.0
    assert control_plane.result.scenario.frontend_config["scenario"][
        "compute_gpu_tflops_fp32"
    ] == 2.5
    assert control_plane.result.scenario.frontend_config["scenario"][
        "compute_npu_tops_int8"
    ] == 12.0
    assert control_plane.result.scenario.frontend_config["scenario"]["orbit"] == {
        "update_interval_seconds": 30,
        "plane_count": 6,
        "altitude_m": 600_000.0,
        "inclination_deg": 55.0,
    }
    assert control_plane.result.scenario.frontend_config["scenario"]["traffic_model"] == {
        "flow_interval_seconds": 30,
        "task_interval_seconds": 45,
        "flow_demand_capacity": 12.5,
        "task_compute_demand": 15.0,
        "task_data_size": 4.0,
        "traffic_class": "BULK_DOWNLINK",
        "destination_type": "GROUND_ENDPOINT",
        "output_data_size": 3.5,
        "data_transfer_weight": 0.0,
        "telemetry_weight": 0.0,
        "bulk_downlink_weight": 0.0,
        "compute_service_weight": 0.0,
    }
    assert control_plane.result.scenario.frontend_config["network"] == {
        "application_protocol": "MQTT",
        "transport_protocol": "UDP",
        "transport_loss_rate": 0.025,
        "transport_congestion_window_segments": 32,
        "routing_protocol": "DISTANCE_VECTOR",
        "datalink_mac_protocol": "SLOTTED_ALOHA",
        "routing_latency_weight": 0.2,
        "routing_inverse_capacity_weight": 400.0,
        "routing_hop_weight": 1.0,
        "carrier_frequency_hz": 22_000_000_000.0,
        "channel_bandwidth_hz": 250_000_000.0,
        "rain_rate_mm_h": 12.5,
        "rain_attenuation_coefficient_db_per_km_per_mm_h": 0.015,
        "rain_effective_path_km": 4.0,
        "antenna_diameter_m": 0.55,
        "antenna_aperture_efficiency": 0.7,
        "transmit_power_dbw": 23.0,
        "system_loss_db": 1.5,
        "noise_temperature_k": 310.0,
        "space_link_mode": "BOUNDED_CANDIDATE",
        "max_space_link_candidates_per_satellite": 6,
        "batch_space_link_update_limit": 500,
    }
    assert ack["generated_config"]["application_protocol"] == "MQTT"
    assert ack["generated_config"]["transport_protocol"] == "UDP"
    assert ack["generated_config"]["transport_loss_rate"] == 0.025
    assert ack["generated_config"]["transport_congestion_window_segments"] == 32
    assert ack["generated_config"]["routing_protocol"] == "DISTANCE_VECTOR"
    assert ack["generated_config"]["datalink_mac_protocol"] == "SLOTTED_ALOHA"
    assert ack["generated_config"]["routing_latency_weight"] == 0.2
    assert ack["generated_config"]["routing_inverse_capacity_weight"] == 400.0
    assert ack["generated_config"]["routing_hop_weight"] == 1.0
    assert ack["generated_config"]["carrier_frequency_hz"] == 22_000_000_000.0
    assert ack["generated_config"]["antenna_diameter_m"] == 0.55
    assert ack["generated_config"]["antenna_aperture_efficiency"] == 0.7
    assert ack["generated_config"]["transmit_power_dbw"] == 23.0
    assert ack["generated_config"]["system_loss_db"] == 1.5
    assert ack["generated_config"]["noise_temperature_k"] == 310.0
    assert ack["generated_config"]["space_link_mode"] == "BOUNDED_CANDIDATE"
    assert ack["generated_config"]["max_space_link_candidates_per_satellite"] == 6
    assert ack["generated_config"]["batch_space_link_update_limit"] == 500
    assert ack["generated_config"]["compute_scheduling_policy"] == "SHORTEST_JOB_FIRST"
    assert ack["generated_config"]["compute_cpu_gflops_fp64"] == 6.0
    assert ack["generated_config"]["compute_gpu_tflops_fp32"] == 2.5
    assert ack["generated_config"]["compute_gpu_tflops_fp16"] == 5.0
    assert ack["generated_config"]["compute_npu_tops_int8"] == 12.0
    assert ack["generated_config"]["compute_memory_gb"] == 32.0
    assert ack["generated_config"]["compute_storage_gb"] == 512.0
    assert ack["generated_config"]["orbit_plane_count"] == 6
    assert ack["generated_config"]["semi_major_axis_km"] == 6971.0
    assert ack["generated_config"]["inclination_deg"] == 55.0
    assert ack["generated_config"]["demand_capacity"] == 12.5
    assert ack["generated_config"]["task_compute_demand"] == 15.0
    assert ack["generated_config"]["task_data_size"] == 4.0
    assert ack["generated_config"]["traffic_class"] == "BULK_DOWNLINK"
    assert ack["generated_config"]["traffic_destination_type"] == "GROUND_ENDPOINT"
    assert ack["generated_config"]["traffic_output_data_size"] == 3.5
    assert ack["generated_config"]["backend_summary"][
        "derived_constellation_summary"
    ]["plane_count"] == 6
    assert ack["generated_config"]["backend_summary"]["traffic_demand_summary"][
        "traffic_class"
    ] == "BULK_DOWNLINK"
    assert ack["generated_config"]["backend_summary"]["traffic_demand_summary"][
        "destination_type"
    ] == "GROUND_ENDPOINT"
    assert ack["generated_config"]["backend_summary"]["traffic_demand_summary"][
        "output_data_size_mb"
    ] == 3.5
    assert ack["generated_config"]["backend_summary"]["traffic_demand_summary"][
        "execution_shape"
    ] == "FLOW_ONLY"
    assert ack["generated_config"]["backend_summary"]["traffic_demand_summary"][
        "lifecycle_note"
    ] == "网络流完成即完成本次业务；不触发星上计算任务生命周期。"
    assert ack["generated_config"]["backend_summary"]["compute_resource_summary"][
        "capacity_unit"
    ] == "GFLOPS FP32"
    assert ack["generated_config"]["backend_summary"]["compute_resource_summary"][
        "total_gpu_tflops_fp32"
    ] == 7.5
    assert ack["generated_config"]["backend_summary"]["compute_resource_summary"][
        "total_npu_tops_int8"
    ] == 36.0

    runtime_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert runtime_ack["ok"] is True
    assert runtime_ack["status"]["status"] == "RUNNING"


def test_initialize_writes_config_and_start_gates_streams(tmp_path) -> None:
    config_path = tmp_path / "sees_control.yaml"
    generated_config_path = tmp_path / "generated_full_system_demo.json"
    control_plane = _small_control_plane(config_path, generated_config_path)

    assert control_plane.stream_events() == ()
    assert control_plane.stream_snapshots() == ()
    assert control_plane.visible_snapshot()["satellites"] == []
    assert control_plane.visible_snapshot()["event_count"] == 0
    assert control_plane.runtime_status()["status"]["initialized"] is False

    blocked_start = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert blocked_start["ok"] is False
    assert "initialized before start" in blocked_start["error"]
    assert control_plane.stream_events() == ()

    init_ack = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "RUNTIME_CONTROL",
                "action": "INITIALIZE",
                "payload": {
                    "satellite_count": 24,
                    "user_count": 40,
                    "compute_capacity": 18.0,
                    "orbit": {
                        "update_interval_seconds": 30,
                        "plane_count": 6,
                        "altitude_m": 600_000.0,
                        "inclination_deg": 55.0,
                    },
                    "traffic_model": {
                        "flow_interval_seconds": 30,
                        "task_interval_seconds": 45,
                        "flow_demand_capacity": 12.5,
                        "task_compute_demand": 15.0,
                        "task_data_size": 4.0,
                        "traffic_class": "COMPUTE_SERVICE",
                        "destination_type": "COMPUTE_NODE",
                        "output_data_size": 0.0,
                    },
                    "mode": "ACCELERATED",
                    "speed_factor": 10,
                },
            }
        )
    )

    assert init_ack["ok"] is True
    assert init_ack["status"]["last_action"] == "INITIALIZE"
    assert init_ack["status"]["status"] == "STOPPED"
    assert init_ack["status"]["initialized"] is True
    assert "satellite_count: 24" in config_path.read_text(encoding="utf-8")
    assert "compute_capacity: 18.0" in config_path.read_text(encoding="utf-8")
    assert "plane_count: 6" in config_path.read_text(encoding="utf-8")
    assert "altitude_m: 600000.0" in config_path.read_text(encoding="utf-8")
    assert "inclination_deg: 55.0" in config_path.read_text(encoding="utf-8")
    assert "flow_interval_seconds: 30" in config_path.read_text(encoding="utf-8")
    assert "flow_demand_capacity: 12.5" in config_path.read_text(encoding="utf-8")
    assert "task_data_size: 4.0" in config_path.read_text(encoding="utf-8")
    assert "traffic_class: COMPUTE_SERVICE" in config_path.read_text(encoding="utf-8")
    assert "destination_type: COMPUTE_NODE" in config_path.read_text(encoding="utf-8")
    assert "output_data_size: 0.0" in config_path.read_text(encoding="utf-8")
    assert "speed_factor: 10" in config_path.read_text(encoding="utf-8")
    generated_config = json.loads(generated_config_path.read_text(encoding="utf-8"))
    assert generated_config["satellite_count"] == 24
    assert generated_config["user_count"] == 40
    assert generated_config["compute_capacity"] == 18.0
    assert generated_config["orbit_plane_count"] == 6
    assert generated_config["semi_major_axis_km"] == 6971.0
    assert generated_config["inclination_deg"] == 55.0
    assert generated_config["demand_capacity"] == 12.5
    assert generated_config["task_compute_demand"] == 15.0
    assert generated_config["task_data_size"] == 4.0
    assert generated_config["traffic_class"] == "COMPUTE_SERVICE"
    assert generated_config["traffic_destination_type"] == "COMPUTE_NODE"
    assert generated_config["traffic_output_data_size"] == 0.0
    assert generated_config["compute_node_count"] == 2
    assert generated_config["seed"] == 1234
    assert generated_config["application_protocol"] == "TASK_OFFLOAD_FLOW"
    assert generated_config["transport_protocol"] == "TCP"
    assert generated_config["transport_loss_rate"] == 0.0
    assert generated_config["transport_congestion_window_segments"] == 0
    assert generated_config["routing_protocol"] == "LINK_STATE"
    assert generated_config["datalink_mac_protocol"] == "TDMA"
    assert generated_config["routing_latency_weight"] == 1.0
    assert generated_config["routing_inverse_capacity_weight"] == 0.0
    assert generated_config["routing_hop_weight"] == 0.0
    assert generated_config["transmit_power_dbw"] == 20.0
    assert generated_config["system_loss_db"] == 1.0
    assert generated_config["noise_temperature_k"] == 290.0
    assert generated_config["space_link_mode"] is None
    assert generated_config["max_space_link_candidates_per_satellite"] == 4
    assert generated_config["batch_space_link_update_limit"] == 999
    assert generated_config["compute_scheduling_policy"] == "FIFO"
    assert init_ack["generated_config"]["satellite_count"] == 24
    assert init_ack["generated_config"]["user_count"] == 40
    assert init_ack["generated_config"]["backend_summary"][
        "derived_constellation_summary"
    ]["plane_count"] == 6
    assert init_ack["generated_config"]["backend_summary"][
        "derived_constellation_summary"
    ]["orbital_period_minutes"] == pytest.approx(96.538902)
    assert init_ack["generated_config"]["backend_summary"][
        "coverage_beam_summary"
    ]["default_beam_count"] == 7
    assert init_ack["generated_config"]["backend_summary"][
        "coverage_beam_summary"
    ]["beam_pattern"] == "CENTER_PLUS_HEX_RING_VISUAL_APPROXIMATION"
    assert init_ack["generated_config"]["backend_summary"]["compute_resource_summary"][
        "total_cpu_gflops_fp32"
    ] == 36.0
    assert init_ack["generated_config"]["backend_summary"]["compute_resource_summary"][
        "total_gpu_tflops_fp32"
    ] == 0.0
    assert init_ack["generated_config"]["backend_summary"]["compute_resource_summary"][
        "total_npu_tops_int8"
    ] == 0.0
    configuration_surface = init_ack["generated_config"]["backend_summary"][
        "configuration_surface_summary"
    ]
    assert configuration_surface == init_ack["status"]["configuration_surface_summary"]
    assert configuration_surface["frontend_policy"] == "CONTROL_PANEL_KEY_FIELDS_ONLY"
    assert configuration_surface["template_config_file"] == (
        "configs/templates/sees_user_detailed.example.yaml"
    )
    assert any(
        field["path"] == "scenario.satellite_count" and field["value"] == 24
        for field in configuration_surface["key_fields"]
    )
    assert "network.carrier_frequency_hz" in configuration_surface["file_only_fields"]
    assert control_plane.result.config.satellite_count == 24
    assert control_plane.result.processed_events == ()
    assert control_plane.stream_events() == ()

    start_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert start_ack["status"]["status"] == "RUNNING"
    control_plane._require_advance_loop().tick()
    assert len(control_plane.stream_events()) > 0
    assert len(control_plane.stream_snapshots()) > 0

    stop_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "STOP"})
    )
    assert stop_ack["status"]["status"] == "STOPPED"
    assert control_plane.stream_events() == ()

    reset_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "RESET"})
    )
    assert reset_ack["status"]["last_action"] == "RESET"
    assert reset_ack["status"]["initialized"] is False
    assert control_plane.visible_snapshot()["event_count"] == 0


def test_control_plane_loads_user_config_template_before_initialization(
    tmp_path,
) -> None:
    config_path = tmp_path / "sees_control.yaml"
    generated_config_path = tmp_path / "generated_full_system_demo.json"
    control_plane = _small_control_plane(config_path, generated_config_path)

    ack = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "RUNTIME_CONTROL",
                "action": "LOAD_TEMPLATE",
                "payload": {"template_id": "network_stress_120sat"},
            }
        )
    )

    assert ack["ok"] is True
    assert ack["command"] == "LOAD_TEMPLATE"
    assert ack["loaded_template_id"] == "network_stress_120sat"
    assert ack["status"]["initialized"] is False
    assert ack["status"]["last_action"] == "CONFIG_UPDATE"
    assert ack["config"]["scenario"]["satellite_count"] == 120
    assert ack["config"]["scenario"]["user_count"] == 240
    assert ack["config"]["network"]["transport_loss_rate"] == 0.05
    assert ack["config"]["runtime"]["duration"] == 600
    assert ack["generated_config"]["satellite_count"] == 120
    assert ack["generated_config"]["user_count"] == 240
    assert ack["generated_config"]["transport_loss_rate"] == 0.05
    assert ack["generated_config"]["backend_summary"][
        "configuration_surface_summary"
    ]["template_profiles"][2]["id"] == "network_stress_120sat"
    assert control_plane.result.config.satellite_count == 120
    assert control_plane.result.config.ground_user_count == 240
    assert control_plane.result.config.transport_loss_rate == 0.05
    assert "satellite_count: 120" in config_path.read_text(encoding="utf-8")
    assert "transport_loss_rate: 0.05" in config_path.read_text(encoding="utf-8")
    generated_config = json.loads(generated_config_path.read_text(encoding="utf-8"))
    assert generated_config["satellite_count"] == 120
    assert generated_config["transport_loss_rate"] == 0.05

    initialize_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "INITIALIZE"})
    )
    assert initialize_ack["ok"] is True
    assert initialize_ack["status"]["initialized"] is True
    assert initialize_ack["generated_config"]["satellite_count"] == 120


def test_control_plane_exposes_user_configuration_contract_api(tmp_path) -> None:
    control_plane = _small_control_plane(tmp_path / "sees_control.yaml")
    update_ack = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "CONFIG_UPDATE",
                "payload": {
                    "satellite_count": 96,
                    "user_count": 144,
                    "compute_gpu_tflops_fp32": 2.5,
                    "duration": 900,
                },
            }
        )
    )

    schema = control_plane.user_configuration_schema()
    templates = control_plane.user_configuration_templates()
    exported = control_plane.user_configuration_export()

    assert update_ack["ok"] is True
    assert schema["type"] == "USER_CONFIGURATION_SCHEMA_V2"
    assert schema["summary"]["schema_id"] == USER_CONFIGURATION_SCHEMA_V2_ID
    assert schema["summary"]["unknown_key_policy"] == "REJECT"
    schema_fields = {
        field["path"]: field
        for field in schema["summary"]["fields"]
        if isinstance(field, dict)
    }
    assert schema_fields["scenario.satellite_count"]["current_value"] == 96
    assert schema_fields["scenario.compute_gpu_tflops_fp32"]["current_value"] == 2.5
    assert schema_fields["runtime.duration"]["current_value"] == 900

    assert templates["type"] == "USER_CONFIGURATION_TEMPLATE_CATALOG"
    template_summary = templates["summary"]
    assert template_summary["schema_id"] == USER_CONFIGURATION_SCHEMA_V2_ID
    assert template_summary["mutation_policy"] == "READ_ONLY_CATALOG"
    assert template_summary["load_command"] == {
        "type": "RUNTIME_CONTROL",
        "action": "LOAD_TEMPLATE",
        "payload_key": "template_id",
        "requires_uninitialized_runtime": True,
    }
    assert [item["id"] for item in template_summary["templates"]] == [
        "baseline_72sat",
        "dynamic_observability_120sat",
        "network_stress_120sat",
        "large_scale_1200sat",
    ]
    template_by_id = {
        item["id"]: item for item in template_summary["templates"] if isinstance(item, dict)
    }
    assert template_by_id["dynamic_observability_120sat"]["scale"] == (
        "120 satellites, 120 compute nodes, mixed communication/compute demand."
    )
    assert template_by_id["network_stress_120sat"]["expected_kpi_behavior"] == (
        "Non-zero loss and jitter proxies with route pressure and recent-flow "
        "KPI variation."
    )
    assert template_by_id["large_scale_1200sat"]["fidelity_mode"] == (
        "LARGE_SCALE_BATCH_ORBIT_BOUNDED_ISL"
    )

    export_summary = exported["summary"]
    assert exported["type"] == "USER_CONFIGURATION_EXPORT"
    assert export_summary["schema_id"] == USER_CONFIGURATION_SCHEMA_V2_ID
    assert export_summary["export_scope"] == "CURRENT_EFFECTIVE_SEES_CONFIG"
    assert export_summary["format"] == "JSON_MAPPING"
    assert export_summary["validation_ok"] is True
    assert export_summary["validation_error_count"] == 0
    assert export_summary["config_hash"].startswith("sha256:")
    assert export_summary["config"]["scenario"]["satellite_count"] == 96
    assert export_summary["config"]["scenario"]["user_count"] == 144
    assert export_summary["config"]["runtime"]["duration"] == 900
    assert "CONFIG_UPDATE control message for partial updates" in export_summary[
        "import_paths"
    ]
    json.dumps(schema, sort_keys=True)
    json.dumps(templates, sort_keys=True)
    json.dumps(exported, sort_keys=True)
    assert control_plane.runtime_status()["status"]["initialized"] is True


def test_control_plane_validates_user_configuration_without_applying(tmp_path) -> None:
    control_plane = _small_control_plane(tmp_path / "sees_control.yaml")
    before_config = control_plane.controller.config_json()
    before_initialized = control_plane.runtime_status()["status"]["initialized"]

    accepted = control_plane.user_configuration_validate(
        {
            "scenario": {
                "satellite_count": 72,
                "compute_nodes": 72,
            },
            "runtime": {
                "duration": 600,
                "seed": 20260703,
            },
        }
    )
    rejected = control_plane.user_configuration_validate(
        {
            "scenario": {
                "satellite_count": 72,
                "unsupported_compute_gpu": 1.0,
            },
        }
    )

    assert accepted["type"] == "USER_CONFIGURATION_VALIDATION_REPORT"
    accepted_summary = accepted["summary"]
    assert accepted_summary["schema_id"] == USER_CONFIGURATION_SCHEMA_V2_ID
    assert accepted_summary["validation_scope"] == "USER_PROVIDED_CONFIG_MAPPING"
    assert accepted_summary["mutation_policy"] == "VALIDATE_ONLY_NO_APPLY"
    assert accepted_summary["ok"] is True
    assert accepted_summary["error_count"] == 0
    assert accepted_summary["errors"] == ()
    assert accepted_summary["normalized_config_hash"].startswith("sha256:")
    assert accepted_summary["normalized_config"]["scenario"]["satellite_count"] == 72
    assert accepted_summary["normalized_config"]["runtime"]["duration"] == 600
    assert accepted_summary["change_summary"]["source"] == "BACKEND_USER_CONFIGURATION"
    assert accepted_summary["change_summary"]["baseline"] == "CURRENT_EFFECTIVE_SEES_CONFIG"
    assert accepted_summary["change_summary"]["candidate"] == "NORMALIZED_USER_CONFIG"
    assert accepted_summary["change_summary"]["changed_field_count"] > 0
    assert accepted_summary["change_summary"]["section_counts"]["scenario"] > 0
    assert accepted_summary["change_summary"]["section_counts"]["runtime"] > 0
    assert accepted_summary["apply_readiness"] == {
        "version": "v1",
        "source": "BACKEND_RUNTIME_STATUS",
        "can_apply": True,
        "readiness": "APPLY_ALLOWED_REINITIALIZES_SESSION",
        "requires_confirmation": False,
        "recommended_action": "APPLY_WHEN_READY",
        "reason": "runtime session exists; applying config will rebuild the initialized session",
        "runtime_initialized": False,
        "controller_status": "STOPPED",
        "lifecycle_state": "INITIALIZED",
        "session_effect": "REINITIALIZES_SESSION",
        "stream_effect": "STOPS_AND_RECREATES_STREAM_BUFFERS",
    }
    assert accepted_summary["apply_command"] == {
        "type": "CONFIG_UPDATE",
        "action": "CONFIG_UPDATE",
        "payload_source": "normalized_config",
        "payload_format": "SEES_CONFIG_MAPPING",
        "requires_preflight_ok": True,
        "requires_explicit_user_action": True,
        "runtime_effect": "REINITIALIZES_SESSION_AND_STREAMS",
        "runtime_status_policy": (
            "SAFE_WHEN_STOPPED_OR_UNINITIALIZED; "
            "RUNNING_SESSION_IS_STOPPED_AND_REINITIALIZED_BY_BACKEND"
        ),
    }

    rejected_summary = rejected["summary"]
    assert rejected_summary["ok"] is False
    assert rejected_summary["error_count"] == 1
    assert rejected_summary["normalized_config_hash"] is None
    assert rejected_summary["normalized_config"] is None
    assert rejected_summary["change_summary"] is None
    assert rejected_summary["apply_readiness"] is None
    assert "unknown scenario keys: unsupported_compute_gpu" in rejected_summary[
        "errors"
    ][0]["message"]
    assert control_plane.controller.config_json() == before_config
    assert control_plane.runtime_status()["status"]["initialized"] is before_initialized


def test_control_plane_validates_user_configuration_text_without_applying(tmp_path) -> None:
    control_plane = _small_control_plane(tmp_path / "sees_control.yaml")
    before_config = control_plane.controller.config_json()

    yaml_report = control_plane.user_configuration_validate_text(
        """
scenario:
  satellite_count: 72
  compute_nodes: 72
runtime:
  duration: 600
  seed: 20260703
""",
        format_hint="yaml",
    )
    json_report = control_plane.user_configuration_validate_text(
        json.dumps(
            {
                "scenario": {
                    "satellite_count": 72,
                    "compute_nodes": 72,
                },
                "runtime": {
                    "duration": 600,
                    "seed": 20260703,
                },
            }
        ),
        format_hint="auto",
    )
    rejected = control_plane.user_configuration_validate_text(
        "scenario:\n  satellite_count: [unsupported]\n",
        format_hint="yaml",
    )

    yaml_summary = yaml_report["summary"]
    assert yaml_report["type"] == "USER_CONFIGURATION_VALIDATION_REPORT"
    assert yaml_summary["validation_scope"] == "USER_PROVIDED_CONFIG_TEXT"
    assert yaml_summary["format"] == "YAML_TEXT"
    assert yaml_summary["text_parse"] == {
        "version": "v1",
        "source": "BACKEND_USER_CONFIGURATION",
        "requested_format": "yaml",
        "detected_format": "yaml",
        "ok": True,
    }
    assert yaml_summary["ok"] is True
    assert yaml_summary["normalized_config"]["scenario"]["satellite_count"] == 72
    assert yaml_summary["change_summary"]["changed_field_count"] > 0
    assert yaml_summary["apply_readiness"]["can_apply"] is True

    json_summary = json_report["summary"]
    assert json_summary["ok"] is True
    assert json_summary["format"] == "JSON_TEXT"
    assert json_summary["text_parse"]["requested_format"] == "auto"
    assert json_summary["text_parse"]["detected_format"] == "json"

    rejected_summary = rejected["summary"]
    assert rejected_summary["ok"] is False
    assert rejected_summary["validation_scope"] == "USER_PROVIDED_CONFIG_TEXT"
    assert rejected_summary["format"] == "YAML_TEXT"
    assert rejected_summary["normalized_config"] is None
    assert rejected_summary["change_summary"] is None
    assert rejected_summary["apply_readiness"] is None
    assert control_plane.controller.config_json() == before_config


def test_control_plane_applies_preflight_normalized_user_configuration(tmp_path) -> None:
    control_plane = _small_control_plane(tmp_path / "sees_control.yaml")
    accepted = control_plane.user_configuration_validate(
        {
            "scenario": {
                "satellite_count": 84,
                "compute_nodes": 84,
                "compute_gpu_tflops_fp32": 1.5,
            },
            "runtime": {
                "duration": 480,
                "seed": 20260706,
            },
        }
    )
    normalized_config = accepted["summary"]["normalized_config"]
    change_summary = accepted["summary"]["change_summary"]
    changed_paths = [item["path"] for item in change_summary["changes"]]

    response = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "CONFIG_UPDATE",
                "payload": normalized_config,
            }
        )
    )
    applied = control_plane.controller.config_json()

    assert accepted["summary"]["ok"] is True
    assert change_summary["changed_field_count"] >= 5
    assert change_summary["hidden_change_count"] == max(
        0,
        change_summary["changed_field_count"] - change_summary["change_count"],
    )
    assert changed_paths == sorted(changed_paths)
    assert "scenario.satellite_count" in changed_paths
    assert "scenario.compute_gpu_tflops_fp32" in changed_paths
    assert "runtime.duration" in changed_paths
    assert next(
        item
        for item in change_summary["changes"]
        if item["path"] == "scenario.satellite_count"
    ) == {
        "path": "scenario.satellite_count",
        "section": "scenario",
        "change_type": "CHANGED",
        "current_value": 12,
        "candidate_value": 84,
    }
    assert response["ok"] is True
    assert response["command"] == "INITIALIZE"
    assert applied["scenario"]["satellite_count"] == 84
    assert applied["scenario"]["compute_nodes"] == 84
    assert applied["scenario"]["compute_gpu_tflops_fp32"] == 1.5
    assert applied["runtime"]["duration"] == 480
    assert applied["runtime"]["seed"] == 20260706
    assert control_plane.runtime_status()["status"]["initialized"] is True


def test_control_plane_reports_running_apply_readiness(tmp_path) -> None:
    control_plane = _small_control_plane(tmp_path / "sees_control.yaml")
    control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "INITIALIZE"})
    )
    control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    try:
        report = control_plane.user_configuration_validate(
            {
                "scenario": {
                    "satellite_count": 72,
                    "compute_nodes": 72,
                },
                "runtime": {
                    "duration": 600,
                    "seed": 20260703,
                },
            }
        )
        readiness = report["summary"]["apply_readiness"]

        assert report["summary"]["ok"] is True
        assert readiness["can_apply"] is True
        assert readiness["runtime_initialized"] is True
        assert readiness["controller_status"] == "RUNNING"
        assert readiness["lifecycle_state"] == "RUNNING"
        assert readiness["readiness"] == "APPLY_ALLOWED_WITH_RUNNING_SESSION_REINIT"
        assert readiness["requires_confirmation"] is True
        assert readiness["recommended_action"] == "PAUSE_OR_STOP_BEFORE_APPLY"
        assert readiness["session_effect"] == "REINITIALIZES_SESSION"
        assert readiness["stream_effect"] == "STOPS_AND_RECREATES_STREAM_BUFFERS"
    finally:
        control_plane.handle_raw_message(
            json.dumps({"type": "RUNTIME_CONTROL", "action": "STOP"})
        )


def test_control_plane_rejects_template_load_after_initialization(tmp_path) -> None:
    control_plane = _small_control_plane(tmp_path / "sees_control.yaml")
    initialized = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "INITIALIZE"})
    )

    ack = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "RUNTIME_CONTROL",
                "action": "LOAD_TEMPLATE",
                "payload": {"template_id": "network_stress_120sat"},
            }
        )
    )

    assert initialized["ok"] is True
    assert ack["ok"] is False
    assert "reset first" in ack["error"]
    assert ack["status"]["initialized"] is True


def test_network_stress_template_status_polling_stays_stable(tmp_path) -> None:
    control_plane = _small_control_plane(tmp_path / "sees_control.yaml")
    load_ack = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "RUNTIME_CONTROL",
                "action": "LOAD_TEMPLATE",
                "payload": {"template_id": "network_stress_120sat"},
            }
        )
    )
    initialize_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "INITIALIZE"})
    )
    start_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )

    assert load_ack["ok"] is True
    assert initialize_ack["ok"] is True
    assert start_ack["ok"] is True
    for _ in range(8):
        control_plane._require_advance_loop().tick()
        status = control_plane.runtime_status()["status"]
        assert status["lifecycle_state"] == "RUNNING"
        assert status["processed_event_count"] > 0
        assert status["kpi_time_series_v1"]["sample_count"] > 0
        assert status["satellite_kpi_slices_v1"]["slice_count"] >= 0


def test_network_stress_template_exposes_nonzero_time_varying_network_kpis() -> None:
    config = demo_config_from_sees_config(
        load_user_configuration_template("network_stress_120sat"),
        _small_demo_config(),
    )
    context = build_integration_demo_runtime(config)
    for event in context.scenario.initial_events:
        context.kernel.schedule_event(event)

    processed_event_count = 0
    for sim_time in range(1, 7):
        processed_event_count += len(context.kernel.run(until_time=float(sim_time)))

    summary = context.metrics.summary()
    samples = context.metrics.kpi_time_series()["samples"]
    sampled_network_values = {
        (
            round(float(sample["network_effective_throughput_mbps"]), 6),
            round(float(sample["network_effective_loss_proxy_rate"]), 6),
            round(float(sample["network_effective_delay_variation_s"]), 6),
        )
        for sample in samples
        if float(sample["network_recent_flow_count"]) > 0.0
    }

    assert processed_event_count < 8_000
    assert summary["routes_total"] > 0
    assert summary["routes_available"] > 0
    assert summary["routes_available"] < summary["routes_total"]
    assert summary["network_quality_effective_throughput_mbps"] > 0.0
    assert summary["network_quality_effective_latency_avg_s"] > 0.0
    assert 0.0 < summary["network_quality_effective_loss_proxy_rate"] < 1.0
    assert summary["network_quality_effective_delay_variation_proxy_s"] > 0.0
    assert len(sampled_network_values) > 1


def test_demo_control_plane_blocks_unsafe_scale_start(tmp_path) -> None:
    control_plane = _small_control_plane(tmp_path / "sees_control.yaml")
    control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "INITIALIZE"})
    )
    control_plane.controller.apply_config(
        SEESConfig(
            scenario=ScenarioConfig(
                satellite_count=10_000,
                user_count=100_000,
                compute_nodes=10,
                cell_count=1000,
                orbit=OrbitParameters(update_interval_seconds=1),
            ),
            runtime=RuntimeConfig(duration=1000),
        )
    )

    ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )

    assert ack["ok"] is False
    assert "scale safety check failed" in ack["error"]
    assert control_plane.controller.snapshot().status == "STOPPED"


def test_demo_control_plane_blocks_unsafe_scale_initialize(tmp_path) -> None:
    control_plane = _small_control_plane(tmp_path / "sees_control.yaml")

    ack = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "RUNTIME_CONTROL",
                "action": "INITIALIZE",
                "payload": {
                    "satellite_count": 1200,
                    "user_count": 1000,
                    "compute_nodes": 1200,
                    "duration": 28740,
                    "orbit": {
                        "update_interval_seconds": 60,
                        "plane_count": 12,
                    },
                    "traffic_model": {
                        "flow_interval_seconds": 60,
                        "task_interval_seconds": 60,
                    },
                },
            }
        )
    )

    assert ack["ok"] is False
    assert "scale safety check failed" in ack["error"]
    assert ack["status"]["initialized"] is False
    assert control_plane.controller.snapshot().status == "STOPPED"


def test_system_remains_deterministic_under_config_changes(tmp_path) -> None:
    first = _small_control_plane(tmp_path / "first.yaml")
    second = _small_control_plane(tmp_path / "second.yaml")
    command = json.dumps(
        {
            "type": "CONFIG_UPDATE",
            "payload": {
                "satellite_count": 24,
                "user_count": 40,
                "speed_factor": 10,
                "mode": "ACCELERATED",
            },
        }
    )

    first_ack = first.handle_raw_message(command)
    second_ack = second.handle_raw_message(command)

    assert first_ack == second_ack
    assert first.result.event_log_jsonl() == second.result.event_log_jsonl()
    assert first.result.final_snapshot == second.result.final_snapshot


def _small_control_plane(
    config_path: object = "configs/sees_control.yaml",
    generated_config_path: object | None = None,
) -> DemoControlPlane:
    resolved_generated_path = (
        generated_config_path
        if generated_config_path is not None
        else Path(config_path).with_name("generated_full_system_demo.json")
    )
    return DemoControlPlane.from_result(
        run_integration_demo(_small_demo_config()),
        config_output_path=config_path,
        generated_config_output_path=resolved_generated_path,
    )


def _small_demo_config() -> DemoConfig:
    return DemoConfig(
        seed=1234,
        satellite_count=12,
        ground_user_count=30,
        ground_station_count=1,
        compute_node_count=2,
        duration_seconds=120,
        orbit_tick_seconds=60,
        network_slot_seconds=60,
        flow_interval_seconds=60,
        task_interval_seconds=60,
        cell_count=10,
        state_snapshot_interval_events=100,
        metric_sample_interval=10,
        websocket_events="/stream/events",
        websocket_state="/stream/state",
        metrics_snapshot="/metrics/snapshot",
        scenario_config="/scenario/config",
        backend_host="127.0.0.1",
        backend_port=8765,
    )
