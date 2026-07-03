from __future__ import annotations

from examples.generated_full_system_demo import run_generated_full_system_demo
from leo_twin.schema import EventType
from leo_twin.services.scenario_builder import FullSystemScenarioBuilderConfig


def test_generated_full_system_demo_runs_domain_lifecycle() -> None:
    result = run_generated_full_system_demo(
        FullSystemScenarioBuilderConfig(
            seed=11,
            satellite_count=4,
            user_count=6,
            compute_node_count=2,
            flow_count=4,
            orbit_plane_count=2,
            min_elevation_deg=-90.0,
            max_range_km=30000.0,
            compute_capacity=20.0,
        )
    )

    assert result.satellite_count == 4
    assert result.ground_endpoint_count == 6
    assert result.compute_node_count == 2
    assert result.flow_count == 4
    assert result.active_link_count > 0
    assert len(result.network_stack_traces) == 4
    assert result.network_stack_traces[0].application_protocol == "TASK_OFFLOAD_FLOW"
    assert result.network_stack_traces[0].transport_protocol == "TCP"
    assert len(result.scheduled_tasks) == 4
    assert result.metrics_summary["routes_available"] == 4
    assert result.metrics_summary["route_latency_min"] > 0.0
    assert result.metrics_summary["route_capacity_max"] == 89.54666666666667
    assert result.metrics_summary["active_link_capacity_avg"] == 100.0
    assert result.metrics_summary["finished_tasks"] == 4
    assert EventType.ORBIT_UPDATE.value in result.processed_event_types
    assert EventType.ROUTE_UPDATE.value in result.processed_event_types
    assert EventType.TASK_START.value in result.processed_event_types
    assert EventType.TASK_FINISH.value in result.processed_event_types


def test_generated_full_system_demo_is_deterministic() -> None:
    config = FullSystemScenarioBuilderConfig(
        seed=12,
        satellite_count=3,
        user_count=5,
        compute_node_count=2,
        flow_count=3,
        orbit_plane_count=1,
        earth_rotation_rate_rad_s=0.000072921159,
        min_elevation_deg=-90.0,
        max_range_km=30000.0,
        compute_capacity=20.0,
    )

    assert run_generated_full_system_demo(config) == run_generated_full_system_demo(config)


def test_generated_full_system_demo_transport_protocol_changes_route_profile() -> None:
    base = dict(
        seed=12,
        satellite_count=3,
        user_count=5,
        compute_node_count=2,
        flow_count=3,
        orbit_plane_count=1,
        min_elevation_deg=-90.0,
        max_range_km=30000.0,
        compute_capacity=20.0,
    )

    tcp = run_generated_full_system_demo(
        FullSystemScenarioBuilderConfig(**base, transport_protocol="TCP")
    )
    udp = run_generated_full_system_demo(
        FullSystemScenarioBuilderConfig(**base, transport_protocol="UDP")
    )

    assert tcp.metrics_summary["route_latency_min"] > udp.metrics_summary["route_latency_min"]
    assert tcp.metrics_summary["route_capacity_max"] < udp.metrics_summary["route_capacity_max"]
    assert {trace.transport_protocol for trace in tcp.network_stack_traces} == {"TCP"}
    assert {trace.transport_protocol for trace in udp.network_stack_traces} == {"UDP"}


def test_generated_full_system_demo_records_configured_network_stack_trace() -> None:
    result = run_generated_full_system_demo(
        FullSystemScenarioBuilderConfig(
            seed=15,
            satellite_count=3,
            user_count=5,
            compute_node_count=2,
            flow_count=3,
            orbit_plane_count=1,
            min_elevation_deg=-90.0,
            max_range_km=30000.0,
            compute_capacity=20.0,
            application_protocol="HTTP",
            transport_protocol="UDP",
            routing_protocol="DISTANCE_VECTOR",
            datalink_mac_protocol="CSMA_CA",
            carrier_frequency_hz=22_000_000_000.0,
            channel_bandwidth_hz=250_000_000.0,
        )
    )

    trace = result.network_stack_traces[0]
    layer_protocols = tuple(layer.protocol_name for layer in trace.layers)
    network_attributes = dict(trace.layers[2].attributes)
    channel_attributes = dict(trace.layers[5].attributes)

    assert layer_protocols == (
        "HTTP",
        "UDP",
        "DISTANCE_VECTOR",
        "CSMA_CA",
        "CONFIGURED_TERMINAL_PROFILE",
        "CONFIGURED_CHANNEL_PROFILE",
    )
    application_attributes = dict(trace.layers[0].attributes)
    data_link_attributes = dict(trace.layers[3].attributes)
    assert trace.application_protocol == "HTTP"
    assert application_attributes["application_profile"] == "web_request"
    assert application_attributes["interaction_model"] == "request_response"
    assert network_attributes["latency_weight"] == "0.000000"
    assert network_attributes["hop_weight"] == "1.000000"
    assert data_link_attributes["mac_profile"] == "CSMA_CA"
    assert data_link_attributes["medium_access"] == "listen_before_transmit"
    assert channel_attributes["carrier_frequency_hz"] == "22000000000.000000"
    assert channel_attributes["bandwidth_hz"] == "250000000.000000"


def test_generated_full_system_demo_rain_fade_reduces_route_capacity() -> None:
    base = dict(
        seed=14,
        satellite_count=4,
        user_count=6,
        compute_node_count=2,
        flow_count=4,
        orbit_plane_count=2,
        min_elevation_deg=-90.0,
        max_range_km=30000.0,
        compute_capacity=20.0,
        transport_protocol="UDP",
    )

    clear = run_generated_full_system_demo(FullSystemScenarioBuilderConfig(**base))
    rainy = run_generated_full_system_demo(
        FullSystemScenarioBuilderConfig(
            **base,
            rain_rate_mm_h=40.0,
            rain_attenuation_coefficient_db_per_km_per_mm_h=0.2,
            rain_effective_path_km=5.0,
        )
    )

    assert rainy.metrics_summary["route_capacity_max"] < clear.metrics_summary[
        "route_capacity_max"
    ]
    assert rainy.metrics_summary["routes_available"] < clear.metrics_summary[
        "routes_available"
    ]


def test_generated_full_system_demo_can_enable_space_links() -> None:
    result = run_generated_full_system_demo(
        FullSystemScenarioBuilderConfig(
            seed=13,
            satellite_count=3,
            user_count=3,
            compute_node_count=1,
            flow_count=0,
            orbit_plane_count=1,
            min_elevation_deg=-90.0,
            max_range_km=30000.0,
            space_link_max_range_km=50000.0,
            space_link_capacity=10000.0,
            compute_capacity=20.0,
        )
    )
    space_links = tuple(
        link
        for link in result.active_links
        if link.source_id.startswith("sat-") and link.target_id.startswith("sat-")
    )

    assert result.active_link_count >= 12
    assert space_links
    assert all(link.capacity < 10000.0 for link in space_links)
