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
    assert len(snapshot["tasks"]) == 32
    assert len(snapshot["compute_nodes"]) == 10
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
    ) == 53
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

    assert len(result.network_stack_traces) == 100
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
    assert udp_result.metrics_summary["route_latency_avg"] < result.metrics_summary[
        "route_latency_avg"
    ]
    assert udp_result.metrics_summary["route_capacity_max"] < result.metrics_summary[
        "route_capacity_max"
    ]


def test_scale_test_basic() -> None:
    result = _demo_result()
    summary = result.metrics_summary

    assert len(result.processed_events) >= 10_000
    assert len(result.processed_events) == 18_241
    assert summary["event_count"] >= 10_000
    assert summary["routes_total"] == 100
    assert summary["routes_available"] == 12
    assert summary["route_hop_count_avg"] >= 2.0
    assert 500.0 <= summary["satellite_altitude_avg"] <= 600.0
    assert summary["task_duration_avg"] >= 0.0
    assert summary["finished_tasks"] == 32
    assert summary["deadline_missed_tasks"] == 21
    assert len(result.state_timeline) <= len(result.processed_events) // 1000 + 1
    assert len(result.final_snapshot["links"]) <= 72 * 21
