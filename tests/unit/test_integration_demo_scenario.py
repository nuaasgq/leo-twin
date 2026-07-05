from __future__ import annotations

from collections import Counter
from math import pi

import pytest

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.scenario import _traffic_demand_batch, build_demo_scenario
from leo_twin.models.traffic import TrafficClass, TrafficDestinationType
from leo_twin.schema import EventType, FlowRequest, TaskRequest


def test_demo_scenario_builds_position_network_ground_endpoints() -> None:
    scenario = build_demo_scenario(_demo_config())

    assert len(scenario.orbit_elements) == len(scenario.orbit_satellites)
    assert scenario.orbit_elements[0].satellite_id == scenario.orbit_satellites[0].satellite_id
    assert len(scenario.ground_endpoints) == 5
    assert [endpoint.endpoint_id for endpoint in scenario.ground_endpoints] == [
        "ground-station-00",
        "user-0000",
        "user-0001",
        "user-0002",
        "user-0003",
    ]
    for endpoint in scenario.ground_endpoints:
        radius = sum(component * component for component in endpoint.position) ** 0.5
        assert radius == pytest.approx(6371.0)
        assert endpoint.min_elevation_deg == 10.0
        assert endpoint.max_range_km == 2500.0


def test_demo_scenario_ground_endpoints_are_deterministic() -> None:
    first = build_demo_scenario(_demo_config()).ground_endpoints
    second = build_demo_scenario(_demo_config()).ground_endpoints

    assert first == second


def test_demo_scenario_uses_configured_orbit_parameters() -> None:
    scenario = build_demo_scenario(
        _demo_config(
            orbit_plane_count=3,
            orbit_altitude_m=600_000.0,
            orbit_inclination_deg=55.0,
        )
    )

    assert scenario.frontend_config["scenario"]["orbit"] == {
        "update_interval_seconds": 60,
        "plane_count": 3,
        "altitude_m": 600_000.0,
        "inclination_deg": 55.0,
    }
    assert scenario.orbit_elements[0].semi_major_axis_km == 6971.0
    assert scenario.orbit_elements[0].inclination_deg == 55.0
    assert {element.raan_deg for element in scenario.orbit_elements[:3]} == {
        0.0,
        120.0,
        240.0,
    }


def test_demo_scenario_auto_allocates_starlink_like_planes_when_not_explicit() -> None:
    scenario = build_demo_scenario(
        _demo_config(
            satellite_count=300,
            orbit_plane_count_explicit=False,
            constellation_profile="STARLINK_SHELL_1_LIKE",
        )
    )

    summary = scenario.frontend_config["derived_constellation_summary"]
    backend_summary = scenario.frontend_config["backend_summary"]

    assert summary == {
        "profile": "STARLINK_SHELL_1_LIKE",
        "satellite_count": 300,
        "plane_count": 30,
        "satellites_per_plane": 10,
        "satellites_per_plane_distribution": [10] * 30,
        "total_slots": 300,
        "plane_count_explicit": False,
        "model_note": (
            "Approximate Starlink Shell 1-like plane allocation; "
            "not exact Starlink fidelity."
        ),
        "raan_spacing_deg": 12.0,
        "mean_anomaly_spacing_deg": 36.0,
        "phase_policy": "SLOT_INDEX_PHASE_WITH_PLANE_OFFSET",
        "altitude_m": 529_000.0,
        "orbital_period_minutes": pytest.approx(95.067783),
        "orbital_period_model_note": (
            "Simplified circular-orbit period estimate; no SGP4 or external ephemeris."
        ),
        "orbital_velocity_km_s": pytest.approx(7.600538),
        "orbital_velocity_model_note": (
            "Simplified circular-orbit speed estimate; no SGP4 or external ephemeris."
        ),
        "inclination_deg": 53.0,
    }
    assert backend_summary["derived_constellation_summary"] == summary
    assert backend_summary["traffic_demand_summary"]["traffic_class"] == "COMPUTE_SERVICE"
    assert backend_summary["compute_resource_summary"]["node_role"] == (
        "SATELLITE_HOSTED_COMPUTE"
    )
    assert scenario.frontend_config["scenario"]["orbit"]["plane_count"] == 30
    assert scenario.orbit_elements[30].raan_deg == pytest.approx(
        scenario.orbit_elements[0].raan_deg
    )
    assert scenario.orbit_elements[30].mean_anomaly_deg == pytest.approx(36.0)
    assert scenario.orbit_satellites[30].phase == pytest.approx(2.0 * pi / 10.0)


def test_demo_flow_requests_target_compute_nodes() -> None:
    scenario = build_demo_scenario(_demo_config())
    compute_node_ids = {node.node_id for node in scenario.compute_nodes}
    satellite_ids = {satellite.satellite_id for satellite in scenario.orbit_satellites}
    flows = tuple(
        event.payload
        for event in scenario.initial_events
        if event.event_type == EventType.FLOW_ARRIVAL
    )
    tasks = tuple(
        event.payload
        for event in scenario.initial_events
        if event.event_type == EventType.TASK_ARRIVAL
    )

    assert flows
    assert all(isinstance(flow, FlowRequest) for flow in flows)
    assert all(isinstance(task, TaskRequest) for task in tasks)
    assert compute_node_ids <= satellite_ids
    assert {flow.target_id for flow in flows if isinstance(flow, FlowRequest)} <= compute_node_ids
    assert tuple(flow.flow_id for flow in flows if isinstance(flow, FlowRequest)) == tuple(
        task.task_id for task in tasks if isinstance(task, TaskRequest)
    )


def test_demo_flow_and_task_demands_are_config_driven() -> None:
    scenario = build_demo_scenario(
        _demo_config(
            flow_demand_capacity=12.5,
            task_compute_demand=15.0,
            task_data_size=4.0,
        )
    )
    first_flow = next(
        event.payload
        for event in scenario.initial_events
        if event.event_type == EventType.FLOW_ARRIVAL
    )
    first_task = next(
        event.payload
        for event in scenario.initial_events
        if event.event_type == EventType.TASK_ARRIVAL
    )

    assert isinstance(first_flow, FlowRequest)
    assert isinstance(first_task, TaskRequest)
    assert first_flow.demand_capacity == 12.5
    assert first_task.compute_demand == 15.0
    assert first_task.data_size == 4.0
    assert scenario.frontend_config["scenario"]["traffic_model"] == {
        "flow_interval_seconds": 60,
        "task_interval_seconds": 60,
        "flow_demand_capacity": 12.5,
        "task_compute_demand": 15.0,
        "task_data_size": 4.0,
        "traffic_class": "COMPUTE_SERVICE",
        "destination_type": "COMPUTE_NODE",
        "output_data_size": 0.0,
        "data_transfer_weight": 0.0,
        "telemetry_weight": 0.0,
        "bulk_downlink_weight": 0.0,
        "compute_service_weight": 0.0,
    }


def test_demo_traffic_model_semantics_are_config_driven() -> None:
    config = _demo_config(
        traffic_class="BULK_DOWNLINK",
        traffic_destination_type="GROUND_ENDPOINT",
        traffic_output_data_size=4.5,
    )
    scenario = build_demo_scenario(config)
    demand_batch = _traffic_demand_batch(config)

    assert scenario.frontend_config["scenario"]["traffic_model"][
        "traffic_class"
    ] == "BULK_DOWNLINK"
    assert scenario.frontend_config["scenario"]["traffic_model"][
        "destination_type"
    ] == "GROUND_ENDPOINT"
    assert scenario.frontend_config["scenario"]["traffic_model"]["output_data_size"] == 4.5
    assert scenario.frontend_config["backend_summary"]["traffic_demand_summary"][
        "traffic_class"
    ] == "BULK_DOWNLINK"
    assert scenario.frontend_config["backend_summary"]["traffic_demand_summary"][
        "destination_type"
    ] == "GROUND_ENDPOINT"
    assert scenario.frontend_config["backend_summary"]["traffic_demand_summary"][
        "output_data_size_mb"
    ] == 4.5
    assert scenario.frontend_config["backend_summary"]["traffic_demand_summary"][
        "execution_shape"
    ] == "FLOW_ONLY"
    assert scenario.frontend_config["backend_summary"]["traffic_demand_summary"][
        "compatibility_note"
    ] == "该业务类型按流级网络业务执行，不生成计算任务。"
    assert scenario.frontend_config["backend_summary"]["traffic_demand_summary"][
        "generated_flow_count"
    ] == len(demand_batch.records)
    assert demand_batch.records[0].traffic_class == TrafficClass.BULK_DOWNLINK
    assert demand_batch.records[0].destination_type == TrafficDestinationType.GROUND_ENDPOINT
    assert demand_batch.records[0].output_data_size == 4.5
    assert demand_batch.records[0].task is None


def test_demo_service_mix_weights_drive_demand_generation() -> None:
    config = _demo_config(
        traffic_data_transfer_weight=2.0,
        traffic_compute_service_weight=1.0,
    )

    scenario = build_demo_scenario(config)
    demand_batch = _traffic_demand_batch(config)
    class_counts = Counter(record.traffic_class for record in demand_batch.records)
    task_count = sum(1 for record in demand_batch.records if record.task is not None)
    compute_records = tuple(
        record
        for record in demand_batch.records
        if record.traffic_class == TrafficClass.COMPUTE_SERVICE
    )

    assert len(demand_batch.records) == 4
    assert class_counts == {
        TrafficClass.DATA_TRANSFER: 3,
        TrafficClass.COMPUTE_SERVICE: 1,
    }
    assert task_count == 1
    assert all(
        record.destination_type == TrafficDestinationType.SERVICE_ENDPOINT
        for record in demand_batch.records
        if record.traffic_class == TrafficClass.DATA_TRANSFER
    )
    assert any(
        record.input_flow.source_id.startswith("user-")
        and record.input_flow.target_id.startswith("ground-")
        for record in demand_batch.records
        if record.traffic_class == TrafficClass.DATA_TRANSFER
    )
    traffic_summary = scenario.frontend_config["backend_summary"][
        "traffic_demand_summary"
    ]
    assert traffic_summary["service_mix_mode"] == "WEIGHTED_MIX"
    assert traffic_summary["service_mix_generated_request_counts"] == {
        "DATA_TRANSFER": 3,
        "TELEMETRY": 0,
        "BULK_DOWNLINK": 0,
        "COMPUTE_SERVICE": 1,
    }
    assert traffic_summary["generated_task_count"] == 1
    assert len(compute_records) == 1
    assert compute_records[0].task is not None
    assert compute_records[0].task.flow_id == compute_records[0].input_flow.flow_id
    assert compute_records[0].task.task_id != compute_records[0].input_flow.flow_id


def test_demo_initial_workload_uses_traffic_demand_records() -> None:
    config = _demo_config()
    scenario = build_demo_scenario(config)
    demand_batch = _traffic_demand_batch(config)
    flow_events = tuple(
        event
        for event in scenario.initial_events
        if event.event_type == EventType.FLOW_ARRIVAL
    )
    task_events = tuple(
        event
        for event in scenario.initial_events
        if event.event_type == EventType.TASK_ARRIVAL
    )

    assert demand_batch == _traffic_demand_batch(config)
    assert len(demand_batch.records) == len(flow_events) == len(task_events)
    first_record = demand_batch.records[0]
    first_flow_event = flow_events[0]
    first_task_event = task_events[0]

    assert first_record.traffic_class == TrafficClass.COMPUTE_SERVICE
    assert first_record.destination_type == TrafficDestinationType.COMPUTE_NODE
    assert first_record.input_data_size == config.flow_demand_capacity
    assert first_record.output_data_size == config.traffic_output_data_size
    assert first_record.arrival_time == first_flow_event.sim_time
    assert first_record.task == first_task_event.payload
    assert first_record.input_flow == first_flow_event.payload
    assert first_task_event.sim_time - first_flow_event.sim_time == pytest.approx(0.05)
    assert first_flow_event.priority == 5
    assert first_task_event.priority == 4
    assert first_record.input_flow.priority == 0
    assert first_record.input_flow.application_id is None
    assert first_record.task is not None
    assert first_record.task.priority == 0
    assert first_record.task.flow_id is None


def test_non_compute_demo_traffic_generates_flow_only_events() -> None:
    config = _demo_config(
        traffic_class="BULK_DOWNLINK",
        traffic_destination_type="GROUND_ENDPOINT",
        ground_station_count=2,
        compute_node_count=4,
    )
    scenario = build_demo_scenario(config)
    flow_events = tuple(
        event
        for event in scenario.initial_events
        if event.event_type == EventType.FLOW_ARRIVAL
    )
    task_events = tuple(
        event
        for event in scenario.initial_events
        if event.event_type == EventType.TASK_ARRIVAL
    )
    flow_payloads = tuple(event.payload for event in flow_events)

    assert len(flow_events) == 4
    assert task_events == ()
    assert all(isinstance(flow, FlowRequest) for flow in flow_payloads)
    assert tuple(flow.source_id for flow in flow_payloads if isinstance(flow, FlowRequest)) == (
        "sat-000",
        "sat-001",
        "sat-002",
        "sat-003",
    )
    assert tuple(flow.target_id for flow in flow_payloads if isinstance(flow, FlowRequest)) == (
        "ground-station-00",
        "ground-station-01",
        "ground-station-00",
        "ground-station-01",
    )
    assert scenario.frontend_config["backend_summary"]["traffic_demand_summary"][
        "generated_flow_count"
    ] == 4


def test_scale_initial_workload_smoothing_spreads_first_burst() -> None:
    scenario = build_demo_scenario(
        _demo_config(
            satellite_count=1200,
            ground_user_count=20,
            compute_node_count=1200,
            duration_seconds=120,
            task_interval_seconds=60,
            flow_interval_seconds=60,
        )
    )
    first_period_workload = tuple(
        event
        for event in scenario.initial_events
        if event.event_type in {EventType.FLOW_ARRIVAL, EventType.TASK_ARRIVAL}
        and str(event.event_id).endswith(tuple(f"{index:05d}" for index in range(1200)))
    )
    first_second_workload = tuple(
        event
        for event in first_period_workload
        if event.sim_time <= 1.0
    )
    task_times = tuple(
        event.sim_time
        for event in first_period_workload
        if event.event_type == EventType.TASK_ARRIVAL
    )
    summary = scenario.frontend_config["backend_summary"][
        "workload_smoothing_summary"
    ]

    assert summary["enabled"] is True
    assert summary["scale_triggered"] is True
    assert summary["mode"] == "DETERMINISTIC_STAGGER"
    assert summary["initial_workload_window_s"] == 59.0
    assert len(first_period_workload) == 2400
    assert len(first_second_workload) < 80
    assert max(task_times) - min(task_times) == pytest.approx(59.0)


def test_initial_workload_smoothing_preserves_count_and_determinism() -> None:
    config = _demo_config(
        satellite_count=1200,
        ground_user_count=20,
        compute_node_count=1200,
        duration_seconds=120,
        task_interval_seconds=60,
    )
    first = build_demo_scenario(config).initial_events
    second = build_demo_scenario(config).initial_events
    workload_events = tuple(
        event
        for event in first
        if event.event_type in {EventType.FLOW_ARRIVAL, EventType.TASK_ARRIVAL}
    )

    assert tuple((event.event_id, event.event_type, event.sim_time) for event in first) == tuple(
        (event.event_id, event.event_type, event.sim_time) for event in second
    )
    assert len(workload_events) == 4800


def test_small_scenario_keeps_default_initial_workload_timing() -> None:
    scenario = build_demo_scenario(_demo_config())
    workload_times = tuple(
        (event.event_type, event.sim_time)
        for event in scenario.initial_events
        if event.event_type in {EventType.FLOW_ARRIVAL, EventType.TASK_ARRIVAL}
    )

    assert [event_type for event_type, _time in workload_times[:4]] == [
        EventType.FLOW_ARRIVAL.value,
        EventType.FLOW_ARRIVAL.value,
        EventType.TASK_ARRIVAL.value,
        EventType.TASK_ARRIVAL.value,
    ]
    assert [time for _event_type, time in workload_times[:4]] == pytest.approx(
        [0.15, 0.16, 0.2, 0.21]
    )


def test_demo_compute_capacity_is_config_driven() -> None:
    scenario = build_demo_scenario(_demo_config(compute_capacity=18.0))

    assert tuple(node.node_id for node in scenario.compute_nodes) == ("sat-000", "sat-001")
    assert scenario.compute_nodes[0].capacity == 18.0
    assert scenario.compute_nodes[1].capacity == 20.5
    assert scenario.frontend_config["scenario"]["compute_capacity"] == 18.0


def test_demo_compute_resource_vector_is_config_driven() -> None:
    scenario = build_demo_scenario(
        _demo_config(
            compute_capacity=40.0,
            compute_cpu_gflops_fp64=8.0,
            compute_gpu_tflops_fp32=2.5,
            compute_gpu_tflops_fp16=5.0,
            compute_npu_tops_int8=12.0,
            compute_memory_gb=32.0,
            compute_storage_gb=512.0,
        )
    )
    frontend_scenario = scenario.frontend_config["scenario"]
    summary = scenario.frontend_config["backend_summary"]["compute_resource_summary"]

    assert frontend_scenario["compute_capacity"] == 40.0
    assert frontend_scenario["compute_gpu_tflops_fp32"] == 2.5
    assert frontend_scenario["compute_npu_tops_int8"] == 12.0
    assert scenario.compute_nodes[0].capacity == 40.0
    assert scenario.compute_nodes[0].cpu_gflops_fp64 == 8.0
    assert scenario.compute_nodes[0].gpu_tflops_fp32 == 2.5
    assert scenario.compute_nodes[0].gpu_tflops_fp16 == 5.0
    assert scenario.compute_nodes[0].npu_tops_int8 == 12.0
    assert scenario.compute_nodes[0].memory_gb == 32.0
    assert scenario.compute_nodes[0].storage_gb == 512.0
    assert summary["cpu_gflops_fp32_per_node"] == 40.0
    assert summary["cpu_gflops_fp64_per_node"] == 8.0
    assert summary["gpu_tflops_fp32_per_node"] == 2.5
    assert summary["gpu_tflops_fp16_per_node"] == 5.0
    assert summary["npu_tops_int8_per_node"] == 12.0
    assert summary["memory_gb_per_node"] == 32.0
    assert summary["storage_gb_per_node"] == 512.0
    assert summary["total_gpu_tflops_fp32"] == 5.0
    assert summary["total_npu_tops_int8"] == 24.0


def _demo_config(**overrides: object) -> DemoConfig:
    values = dict(
        seed=1234,
        satellite_count=6,
        ground_user_count=4,
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
    values.update(overrides)
    return DemoConfig(**values)
