from __future__ import annotations

from dataclasses import replace
from functools import lru_cache

from examples.integration_demo import DemoRunResult, load_demo_config, run_integration_demo
from examples.integration_demo.replay import replay_events
from examples.integration_demo.server import _FRONTEND_EVENT_TYPES
from examples.integration_demo.serialization import event_to_json, stable_json
from leo_twin.schema import EventType


@lru_cache(maxsize=1)
def _demo_result() -> DemoRunResult:
    return run_integration_demo(load_demo_config())


def test_end_to_end_pipeline_test() -> None:
    result = _demo_result()
    event_types = {str(event.event_type) for event in result.processed_events}

    assert EventType.ORBIT_UPDATE.value in event_types
    assert EventType.ACCESS_START.value in event_types
    assert EventType.ACCESS_END.value in event_types
    assert EventType.LINK_UPDATE.value in event_types
    assert EventType.FLOW_ARRIVAL.value in event_types
    assert EventType.ROUTE_UPDATE.value in event_types
    assert EventType.TASK_START.value in event_types
    assert EventType.TASK_FINISH.value in event_types
    assert EventType.METRIC_SAMPLE.value in event_types
    assert len(result.scenario.orbit_satellites) == 72
    assert result.config.ground_user_count == 1000
    assert result.config.ground_station_count == 3
    assert result.config.application_protocol == "TASK_OFFLOAD_FLOW"
    assert len(result.scenario.compute_nodes) == 10


def test_frontend_sync_test() -> None:
    result = _demo_result()
    snapshot = result.final_snapshot
    scenario_config = result.scenario.frontend_config

    assert len(snapshot["satellites"]) == 72
    assert len(snapshot["ground_users"]) == 1003
    assert len(snapshot["tasks"]) == 26
    assert len(snapshot["compute_nodes"]) == 8
    assert {
        "node_id",
        "capacity",
        "available_capacity",
        "status",
        "load_ratio",
    } <= set(snapshot["compute_nodes"][0])
    assert sum(
        1
        for link in snapshot["links"]
        if str(link["source_id"]).startswith("sat-")
        and str(link["target_id"]).startswith("sat-")
    ) == 61
    for route in snapshot["routes"]:
        if not route["available"]:
            continue
        assert all(
            not str(node_id).startswith("user-")
            for node_id in route["path"][1:-1]
        )
    assert int(snapshot["event_count"]) == len(result.processed_events)
    assert len(result.frontend_events) > 0
    assert scenario_config["backend_summary"]["derived_constellation_summary"][
        "plane_count"
    ] == 12
    assert scenario_config["backend_summary"]["traffic_demand_summary"][
        "traffic_class"
    ] == "COMPUTE_SERVICE"
    assert scenario_config["backend_summary"]["compute_resource_summary"][
        "node_role"
    ] == "SATELLITE_HOSTED_COMPUTE"
    assert {
        str(event.event_type)
        for event in result.processed_events
        if str(event.event_type) in _FRONTEND_EVENT_TYPES
    } == _FRONTEND_EVENT_TYPES
    assert scenario_config["endpoints"] == {
        "config": "/scenario/config",
        "control": "/control",
        "events": "/stream/events",
        "state": "/stream/state",
        "metrics": "/metrics/snapshot",
        "runtime_status": "/runtime/status",
    }
    assert stable_json(snapshot).startswith("{")
    assert stable_json(scenario_config).startswith("{")


def test_replay_test() -> None:
    result = _demo_result()
    replay = replay_events(
        result.processed_events,
        result.scenario.ground_user_render_states,
        result.config.state_snapshot_interval_events,
    )

    assert replay.final_snapshot == result.final_snapshot
    assert replay.replay_signature == result.replay.replay_signature
    assert replay.timeline == result.state_timeline
    assert stable_json(event_to_json(result.processed_events[0])) in replay.replay_signature


def test_network_stack_trace_uses_configured_protocols() -> None:
    result = _demo_result()

    assert len(result.network_stack_traces) == 126
    assert {trace.application_protocol for trace in result.network_stack_traces} == {
        "TASK_OFFLOAD_FLOW"
    }
    assert {trace.transport_protocol for trace in result.network_stack_traces} == {"TCP"}
    assert {
        layer.protocol_name
        for trace in result.network_stack_traces
        for layer in trace.layers
        if str(layer.layer) == "NETWORK"
    } == {"LINK_STATE"}
    assert {
        layer.protocol_name
        for trace in result.network_stack_traces
        for layer in trace.layers
        if str(layer.layer) == "DATA_LINK"
    } == {"TDMA"}
    default_network_attributes = dict(result.network_stack_traces[0].layers[2].attributes)
    assert default_network_attributes["latency_weight"] == "1.000000"
    assert default_network_attributes["inverse_capacity_weight"] == "0.000000"
    assert default_network_attributes["hop_weight"] == "0.000000"
    assert any(
        ("carrier_frequency_hz", "20000000000.000000") in layer.attributes
        for trace in result.network_stack_traces
        for layer in trace.layers
    )
    assert result.metrics_summary["network_quality_effective_loss_proxy_rate"] > 0.0
    assert (
        result.metrics_summary["network_quality_effective_delay_variation_proxy_s"]
        > 0.0
    )
    assert result.metrics_summary["service_latency_task_count"] == 26
    assert result.metrics_summary["service_latency_complete_count"] == 26
    assert result.service_latency_history["service_count"] == 26
    assert result.service_latency_history["item_count"] == 26
    assert all(
        item["complete"] is True for item in result.service_latency_history["items"]
    )

    udp_result = run_integration_demo(
        replace(
            load_demo_config(),
            application_protocol="MQTT",
            transport_protocol="UDP",
            routing_protocol="DISTANCE_VECTOR",
            datalink_mac_protocol="SLOTTED_ALOHA",
            routing_latency_weight=0.2,
            routing_inverse_capacity_weight=400.0,
            routing_hop_weight=1.0,
        )
    )

    assert {trace.application_protocol for trace in udp_result.network_stack_traces} == {"MQTT"}
    assert {trace.transport_protocol for trace in udp_result.network_stack_traces} == {"UDP"}
    assert {
        layer.protocol_name
        for trace in udp_result.network_stack_traces
        for layer in trace.layers
        if str(layer.layer) == "APPLICATION"
    } == {"MQTT"}
    assert {
        layer.protocol_name
        for trace in udp_result.network_stack_traces
        for layer in trace.layers
        if str(layer.layer) == "NETWORK"
    } == {"DISTANCE_VECTOR"}
    assert {
        layer.protocol_name
        for trace in udp_result.network_stack_traces
        for layer in trace.layers
        if str(layer.layer) == "DATA_LINK"
    } == {"SLOTTED_ALOHA"}
    custom_application_attributes = dict(
        udp_result.network_stack_traces[0].layers[0].attributes
    )
    custom_network_attributes = dict(udp_result.network_stack_traces[0].layers[2].attributes)
    custom_data_link_attributes = dict(
        udp_result.network_stack_traces[0].layers[3].attributes
    )
    assert custom_application_attributes["demand_capacity_multiplier"] == "0.750000"
    assert custom_application_attributes["session_setup_latency_s"] == "0.005000"
    assert custom_network_attributes["latency_weight"] == "0.200000"
    assert custom_network_attributes["inverse_capacity_weight"] == "400.000000"
    assert custom_network_attributes["hop_weight"] == "1.000000"
    assert custom_data_link_attributes["medium_access_efficiency"] == "0.620000"
    assert custom_data_link_attributes["collision_loss_rate"] == "0.080000"
    assert custom_data_link_attributes["contention_delay_s"] == "0.004000"
    assert (
        round(udp_result.metrics_summary["network_quality_route_loss_proxy_rate"], 6)
        == 0.08
    )
    assert (
        udp_result.metrics_summary["network_quality_effective_loss_proxy_rate"]
        > 0.0
    )
    assert (
        udp_result.metrics_summary[
            "network_quality_effective_delay_variation_proxy_s"
        ]
        > 0.0
    )
    assert udp_result.metrics_summary["route_latency_avg"] < result.metrics_summary[
        "route_latency_avg"
    ]
    assert udp_result.metrics_summary["route_capacity_max"] < result.metrics_summary[
        "route_capacity_max"
    ]


def test_non_compute_traffic_mix_runs_without_compute_tasks() -> None:
    result = run_integration_demo(
        replace(
            load_demo_config(),
            satellite_count=12,
            ground_user_count=20,
            ground_station_count=2,
            compute_node_count=4,
            duration_seconds=120,
            traffic_class="BULK_DOWNLINK",
            traffic_destination_type="GROUND_ENDPOINT",
            traffic_output_data_size=3.5,
        )
    )
    event_types = tuple(str(event.event_type) for event in result.processed_events)
    traffic_summary = result.scenario.frontend_config["backend_summary"][
        "traffic_demand_summary"
    ]

    assert event_types.count(EventType.FLOW_ARRIVAL.value) == 4
    assert EventType.TASK_ARRIVAL.value not in event_types
    assert EventType.TASK_START.value not in event_types
    assert EventType.TASK_FINISH.value not in event_types
    assert traffic_summary["traffic_class"] == "BULK_DOWNLINK"
    assert traffic_summary["destination_type"] == "GROUND_ENDPOINT"
    assert traffic_summary["generated_flow_count"] == 4
    assert traffic_summary["output_data_size_mb"] == 3.5
    assert traffic_summary["execution_shape"] == "FLOW_ONLY"
    assert traffic_summary["requires_compute_node_destination"] is False
    assert len(result.network_stack_traces) == 4


def test_compute_service_summary_reports_actual_task_interval_schedule() -> None:
    result = run_integration_demo(
        replace(
            load_demo_config(),
            satellite_count=6,
            ground_user_count=12,
            ground_station_count=2,
            compute_node_count=2,
            duration_seconds=90,
            flow_interval_seconds=10,
            task_interval_seconds=30,
            traffic_class="COMPUTE_SERVICE",
            traffic_destination_type="COMPUTE_NODE",
        )
    )
    flow_arrivals = tuple(
        event
        for event in result.scenario.initial_events
        if event.event_type == EventType.FLOW_ARRIVAL.value
    )
    task_arrivals = tuple(
        event
        for event in result.scenario.initial_events
        if event.event_type == EventType.TASK_ARRIVAL.value
    )
    backend_summary = result.scenario.frontend_config["backend_summary"]
    traffic_summary = backend_summary["traffic_demand_summary"]
    schedule = backend_summary["traffic_schedule_semantics_v1"]

    assert len(flow_arrivals) == 6
    assert len(task_arrivals) == 6
    assert sorted({int(event.sim_time) for event in flow_arrivals}) == [0, 30, 60]
    assert sorted({int(event.sim_time) for event in task_arrivals}) == [0, 30, 60]
    assert traffic_summary["arrival_interval_seconds"] == 30.0
    assert traffic_summary["effective_arrival_interval_source"] == (
        "scenario.traffic_model.task_interval_seconds"
    )
    assert schedule["configured_flow_interval_seconds"] == 10.0
    assert schedule["configured_task_interval_seconds"] == 30.0
    assert schedule["effective_arrival_interval_seconds"] == 30.0
    assert schedule["flow_arrival_schedule_source"] == (
        "scenario.traffic_model.task_interval_seconds"
    )
    assert schedule["schedule_policy"] == "CORRELATED_INPUT_FLOW_AND_TASK_INTERVAL"
    assert (
        backend_summary["traffic_demand_explanation_v1"][
            "traffic_schedule_semantics_v1"
        ]
        == schedule
    )


def test_scale_test_basic() -> None:
    result = _demo_result()
    summary = result.metrics_summary

    assert len(result.processed_events) >= 10_000
    assert len(result.processed_events) == 32_456
    assert summary["event_count"] >= 10_000
    assert summary["routes_total"] == 126
    assert summary["routes_available"] == 52
    assert summary["route_hop_count_avg"] >= 2.0
    assert 500.0 <= summary["satellite_altitude_avg"] <= 600.0
    assert summary["task_duration_avg"] >= 0.0
    assert summary["finished_tasks"] == 26
    assert summary["service_latency_complete_count"] == 26
    assert summary["deadline_missed_tasks"] == 0
    assert len(result.state_timeline) <= len(result.processed_events) // 1000 + 1
    assert len(result.final_snapshot["links"]) <= 72 * 21
