from __future__ import annotations

import json

import pytest

from leo_twin.models.traffic import (
    TrafficArrivalProfile,
    TrafficClass,
    TrafficDemandConfig,
    TrafficDemandModel,
    TrafficDemandProfile,
    TrafficDestinationType,
    TrafficServiceMixConfig,
    TrafficServiceMixItem,
    generate_traffic_demand,
    generate_traffic_service_mix,
)
from leo_twin.schema import EventType, FlowRequest


def test_traffic_classes_are_explicit_contract_values() -> None:
    assert tuple(item.value for item in TrafficClass) == (
        "DATA_TRANSFER",
        "TELEMETRY",
        "BULK_DOWNLINK",
        "COMPUTE_SERVICE",
        "EMERGENCY",
    )


def test_normal_data_profile_generates_flow_requests_with_arrivals() -> None:
    profile = TrafficDemandProfile(
        traffic_class=TrafficClass.DATA_TRANSFER,
        source_ids=("user-a", "user-b"),
        destination_ids=("gateway-a", "gateway-b"),
        request_count=3,
        arrival_interval=5.0,
        input_data_size=12.5,
        priority=4,
        destination_type=TrafficDestinationType.SERVICE_ENDPOINT,
        start_time=2.0,
        id_prefix="demo",
    )

    batch = generate_traffic_demand((profile,))

    assert tuple(record.arrival_time for record in batch.records) == (2.0, 7.0, 12.0)
    assert batch.task_requests == ()
    assert batch.output_flow_metadata == ()
    assert batch.flow_requests == (
        FlowRequest(
            flow_id="demo-00-data_transfer-00000",
            source_id="user-a",
            target_id="gateway-a",
            demand_capacity=12.5,
            application_id="DATA_TRANSFER",
            priority=4,
        ),
        FlowRequest(
            flow_id="demo-00-data_transfer-00001",
            source_id="user-b",
            target_id="gateway-b",
            demand_capacity=12.5,
            application_id="DATA_TRANSFER",
            priority=4,
        ),
        FlowRequest(
            flow_id="demo-00-data_transfer-00002",
            source_id="user-a",
            target_id="gateway-a",
            demand_capacity=12.5,
            application_id="DATA_TRANSFER",
            priority=4,
        ),
    )

    events = batch.flow_arrival_events()

    assert tuple(event.event_type for event in events) == (
        EventType.FLOW_ARRIVAL.value,
        EventType.FLOW_ARRIVAL.value,
        EventType.FLOW_ARRIVAL.value,
    )
    assert tuple(event.sim_time for event in events) == (2.0, 7.0, 12.0)
    assert tuple(event.priority for event in events) == (4, 4, 4)


def test_compute_service_generates_correlated_requests_and_output_metadata() -> None:
    profile = TrafficDemandProfile(
        traffic_class=TrafficClass.COMPUTE_SERVICE,
        source_ids=("user-a", "user-b"),
        destination_ids=("compute-a", "compute-b"),
        request_count=2,
        arrival_interval=10.0,
        input_data_size=8.0,
        output_data_size=3.0,
        priority=9,
        destination_type=TrafficDestinationType.COMPUTE_NODE,
        start_time=1.0,
        compute_demand=21.0,
        fp32_ops=10_000_000_000_000.0,
        fp16_ops=4_000_000_000_000.0,
        int8_ops=8_000_000_000_000.0,
        memory_gb=4.0,
        input_data_mb=512.0,
        output_data_mb=128.0,
        id_prefix="svc",
        output_destination_ids=("sink-a", "sink-b"),
    )

    batch = TrafficDemandModel(TrafficDemandConfig((profile,))).generate()

    first_flow, second_flow = batch.flow_requests
    first_task, second_task = batch.task_requests
    first_output, second_output = batch.output_flow_metadata

    assert first_flow.flow_id == "svc-00-compute_service-00000-input"
    assert first_flow.source_id == "user-a"
    assert first_flow.target_id == "compute-a"
    assert first_flow.demand_capacity == 8.0
    assert first_flow.priority == 9

    assert first_task.task_id == "svc-00-compute_service-00000-task"
    assert first_task.source_id == "user-a"
    assert first_task.submit_time == 1.0
    assert first_task.compute_demand == 21.0
    assert first_task.data_size == 8.0
    assert first_task.flow_id == first_flow.flow_id
    assert first_task.priority == 9
    assert first_task.fp32_ops == 10_000_000_000_000.0
    assert first_task.fp16_ops == 4_000_000_000_000.0
    assert first_task.int8_ops == 8_000_000_000_000.0
    assert first_task.memory_gb == 4.0
    assert first_task.input_data_mb == 512.0
    assert first_task.output_data_mb == 128.0

    assert first_output.flow_id == "svc-00-compute_service-00000-output"
    assert first_output.task_id == first_task.task_id
    assert first_output.input_flow_id == first_flow.flow_id
    assert first_output.source_id == "compute-a"
    assert first_output.target_id == "sink-a"
    assert first_output.data_size == 3.0
    assert first_output.to_flow_request() == FlowRequest(
        flow_id="svc-00-compute_service-00000-output",
        source_id="compute-a",
        target_id="sink-a",
        demand_capacity=3.0,
        application_id="COMPUTE_SERVICE",
        priority=9,
    )

    assert second_flow.source_id == "user-b"
    assert second_flow.target_id == "compute-b"
    assert second_task.submit_time == 11.0
    assert second_task.flow_id == second_flow.flow_id
    assert second_output.source_id == "compute-b"
    assert second_output.target_id == "sink-b"

    task_events = batch.task_arrival_events()

    assert tuple(event.event_type for event in task_events) == (
        EventType.TASK_ARRIVAL.value,
        EventType.TASK_ARRIVAL.value,
    )
    assert tuple(event.sim_time for event in task_events) == (1.0, 11.0)
    assert tuple(event.payload for event in task_events) == batch.task_requests


def test_traffic_demand_model_is_deterministic_for_same_config() -> None:
    profiles = (
        TrafficDemandProfile(
            traffic_class=TrafficClass.TELEMETRY,
            source_ids=("sensor-a", "sensor-b"),
            destination_ids=("gateway-a",),
            request_count=4,
            arrival_interval=2.5,
            input_data_size=1.25,
            priority=1,
            id_prefix="tm",
        ),
        TrafficDemandProfile(
            traffic_class=TrafficClass.BULK_DOWNLINK,
            source_ids=("sat-a",),
            destination_ids=("ground-a", "ground-b"),
            request_count=3,
            arrival_interval=30.0,
            input_data_size=64.0,
            priority=2,
            destination_type=TrafficDestinationType.GROUND_ENDPOINT,
            id_prefix="bulk",
        ),
    )
    config = TrafficDemandConfig(profiles)

    first = TrafficDemandModel(config).generate()
    second = TrafficDemandModel(config).generate()

    assert first == second
    assert first.flow_arrival_events() == second.flow_arrival_events()
    assert first.task_arrival_events() == second.task_arrival_events()


def test_service_mix_allocates_requests_and_generates_correlated_businesses() -> None:
    config = TrafficServiceMixConfig(
        total_request_count=10,
        arrival_interval=3.0,
        start_time=1.0,
        id_prefix="mix",
        items=(
            TrafficServiceMixItem(
                traffic_class=TrafficClass.DATA_TRANSFER,
                weight=0.5,
                source_ids=("user-a", "user-b"),
                destination_ids=("gateway-a",),
                input_data_size=5.0,
                priority=1,
                destination_type=TrafficDestinationType.SERVICE_ENDPOINT,
            ),
            TrafficServiceMixItem(
                traffic_class=TrafficClass.COMPUTE_SERVICE,
                weight=0.3,
                source_ids=("user-a", "user-b"),
                destination_ids=("sat-compute-a",),
                input_data_size=8.0,
                output_data_size=2.0,
                priority=4,
                compute_demand=16.0,
                fp32_ops=1_000.0,
                memory_gb=2.0,
                output_destination_ids=("user-a",),
            ),
            TrafficServiceMixItem(
                traffic_class=TrafficClass.TELEMETRY,
                weight=0.2,
                source_ids=("sensor-a",),
                destination_ids=("telemetry-gateway",),
                input_data_size=1.0,
                priority=0,
            ),
        ),
    )

    profiles = config.to_demand_profiles()
    batch = generate_traffic_service_mix(config)

    assert tuple(profile.request_count for profile in profiles) == (5, 3, 2)
    assert tuple(profile.id_prefix for profile in profiles) == (
        "mix-00",
        "mix-01",
        "mix-02",
    )
    assert len(batch.records) == 10
    assert len(batch.flow_requests) == 10
    assert len(batch.task_requests) == 3
    assert len(batch.output_flow_metadata) == 3
    assert tuple(record.traffic_class for record in batch.records[:6]) == (
        TrafficClass.COMPUTE_SERVICE,
        TrafficClass.DATA_TRANSFER,
        TrafficClass.TELEMETRY,
        TrafficClass.COMPUTE_SERVICE,
        TrafficClass.DATA_TRANSFER,
        TrafficClass.TELEMETRY,
    )
    compute_record = next(
        record
        for record in batch.records
        if record.traffic_class == TrafficClass.COMPUTE_SERVICE
    )
    assert compute_record.task is not None
    assert compute_record.task.compute_demand == 16.0
    assert compute_record.task.fp32_ops == 1_000.0
    assert compute_record.task.memory_gb == 2.0
    assert compute_record.output_flow is not None
    assert compute_record.output_flow.target_id == "user-a"
    assert tuple(event.sim_time for event in batch.flow_arrival_events()) == (
        1.0,
        1.0,
        1.0,
        4.0,
        4.0,
        4.0,
        7.0,
        7.0,
        10.0,
        13.0,
    )


def test_service_mix_weight_ties_are_allocated_by_item_order() -> None:
    config = TrafficServiceMixConfig(
        total_request_count=5,
        arrival_interval=1.0,
        items=(
            TrafficServiceMixItem(
                traffic_class=TrafficClass.DATA_TRANSFER,
                weight=1.0,
                source_ids=("user-a",),
                destination_ids=("gateway-a",),
                input_data_size=1.0,
            ),
            TrafficServiceMixItem(
                traffic_class=TrafficClass.BULK_DOWNLINK,
                weight=1.0,
                source_ids=("sat-a",),
                destination_ids=("ground-a",),
                input_data_size=1.0,
            ),
        ),
    )

    assert tuple(profile.request_count for profile in config.to_demand_profiles()) == (3, 2)
    assert generate_traffic_service_mix(config) == generate_traffic_service_mix(config)


def test_service_mix_summary_reports_counts_and_per_user_state() -> None:
    config = TrafficServiceMixConfig(
        total_request_count=7,
        arrival_interval=4.0,
        id_prefix="portfolio",
        items=(
            TrafficServiceMixItem(
                traffic_class=TrafficClass.EMERGENCY,
                weight=2.0,
                source_ids=("user-a", "user-b"),
                destination_ids=("ops-center",),
                input_data_size=0.5,
                priority=10,
                arrival_profile=TrafficArrivalProfile.BURST,
                burst_size=2,
                burst_spacing=0.25,
            ),
            TrafficServiceMixItem(
                traffic_class=TrafficClass.COMPUTE_SERVICE,
                weight=1.0,
                source_ids=("user-a",),
                destination_ids=("sat-compute-a",),
                input_data_size=6.0,
                output_data_size=2.0,
                priority=5,
                output_destination_ids=("user-a",),
            ),
            TrafficServiceMixItem(
                traffic_class=TrafficClass.BULK_DOWNLINK,
                weight=1.0,
                source_ids=("sat-a",),
                destination_ids=("ground-a",),
                input_data_size=10.0,
                priority=1,
            ),
        ),
    )

    batch = generate_traffic_service_mix(config)
    summary = batch.service_mix_summary()
    per_user = {
        item["user_id"]: item
        for item in summary["per_user_active_service_state"]
        if isinstance(item, dict)
    }

    assert summary["generated_request_count"] == 7
    assert summary["generated_request_counts"] == {
        "DATA_TRANSFER": 0,
        "TELEMETRY": 0,
        "BULK_DOWNLINK": 2,
        "COMPUTE_SERVICE": 2,
        "EMERGENCY": 3,
    }
    assert summary["active_service_classes"] == (
        "BULK_DOWNLINK",
        "COMPUTE_SERVICE",
        "EMERGENCY",
    )
    assert summary["schedule_ordering"] == "ARRIVAL_TIME_PRIORITY_CLASS_FLOW"
    assert summary["simultaneous_arrival_policy"] == (
        "HIGHER_PRIORITY_FIRST_THEN_CLASS_AND_FLOW_ID"
    )
    assert per_user["user-a"]["request_count"] == 4
    assert per_user["user-a"]["service_classes"] == (
        "COMPUTE_SERVICE",
        "EMERGENCY",
    )
    assert per_user["user-a"]["primary_service_class"] == "EMERGENCY"
    assert per_user["user-a"]["max_priority"] == 10
    assert per_user["user-a"]["task_ids"] == (
        "portfolio-01-01-compute_service-00000-task",
        "portfolio-01-01-compute_service-00001-task",
    )
    assert per_user["user-b"]["service_classes"] == ("EMERGENCY",)
    assert per_user["sat-a"]["service_classes"] == ("BULK_DOWNLINK",)


def test_traffic_demand_explanation_reports_business_semantics() -> None:
    config = TrafficServiceMixConfig(
        total_request_count=7,
        arrival_interval=4.0,
        id_prefix="portfolio",
        items=(
            TrafficServiceMixItem(
                traffic_class=TrafficClass.EMERGENCY,
                weight=2.0,
                source_ids=("user-a", "user-b"),
                destination_ids=("ops-center",),
                input_data_size=0.5,
                priority=10,
                arrival_profile=TrafficArrivalProfile.BURST,
                burst_size=2,
                burst_spacing=0.25,
            ),
            TrafficServiceMixItem(
                traffic_class=TrafficClass.COMPUTE_SERVICE,
                weight=1.0,
                source_ids=("user-a",),
                destination_ids=("sat-compute-a",),
                input_data_size=6.0,
                output_data_size=2.0,
                priority=5,
                output_destination_ids=("user-a",),
            ),
            TrafficServiceMixItem(
                traffic_class=TrafficClass.BULK_DOWNLINK,
                weight=1.0,
                source_ids=("sat-a",),
                destination_ids=("ground-a",),
                input_data_size=10.0,
                priority=1,
            ),
        ),
    )

    first = generate_traffic_service_mix(config).traffic_demand_explanation()
    second = generate_traffic_service_mix(config).traffic_demand_explanation()
    rows = {row["traffic_class"]: row for row in first["traffic_class_rows"]}
    users = {
        row["user_id"]: row
        for row in first["per_user_active_service_state"]
        if isinstance(row, dict)
    }

    assert first == second
    assert first["explanation_id"] == "leo_twin.traffic_demand_explanation.v1"
    assert first["request_count"] == 7
    assert first["input_flow_count"] == 7
    assert first["task_request_count"] == 2
    assert first["output_flow_count"] == 2
    assert first["communication_only_request_count"] == 5
    assert first["compute_service_request_count"] == 2
    assert first["active_traffic_classes"] == (
        "BULK_DOWNLINK",
        "COMPUTE_SERVICE",
        "EMERGENCY",
    )
    assert first["schedule_ordering"] == "ARRIVAL_TIME_PRIORITY_CLASS_FLOW"
    assert first["simultaneous_arrival_policy"] == (
        "HIGHER_PRIORITY_FIRST_THEN_CLASS_AND_FLOW_ID"
    )
    assert first["arrival_window"] == {
        "first_arrival_time": 0.0,
        "last_arrival_time": 4.0,
        "duration_seconds": 4.0,
    }
    assert first["priority_summary"] == {
        "min_priority": 1,
        "max_priority": 10,
        "unique_priorities": (1, 5, 10),
    }
    assert first["data_volume"] == {
        "total_input_data_mb": 33.5,
        "total_output_data_mb": 4.0,
        "total_data_mb": 37.5,
    }
    assert first["correlation_summary"] == {
        "all_compute_services_have_task": True,
        "all_compute_services_have_output_flow": True,
        "packet_level_simulation": False,
        "frontend_inference_required": False,
    }
    assert rows["COMPUTE_SERVICE"]["request_count"] == 2
    assert rows["COMPUTE_SERVICE"]["task_request_count"] == 2
    assert rows["COMPUTE_SERVICE"]["output_flow_count"] == 2
    assert rows["COMPUTE_SERVICE"]["destination_types"] == ("COMPUTE_NODE",)
    assert rows["EMERGENCY"]["destination_types"] == ("SERVICE_ENDPOINT",)
    assert users["user-a"]["primary_service_class"] == "EMERGENCY"
    assert users["user-a"]["task_ids"] == (
        "portfolio-01-01-compute_service-00000-task",
        "portfolio-01-01-compute_service-00001-task",
    )
    assert "Packet-level traffic" in first["model_assumptions"][2]
    assert json.loads(json.dumps(first, sort_keys=True))["explanation_id"] == (
        "leo_twin.traffic_demand_explanation.v1"
    )


def test_runtime_request_timeline_reports_time_relative_business_state() -> None:
    profile = TrafficDemandProfile(
        traffic_class=TrafficClass.COMPUTE_SERVICE,
        source_ids=("user-a",),
        destination_ids=("sat-compute-a",),
        request_count=3,
        arrival_interval=10.0,
        input_data_size=6.0,
        output_data_size=2.0,
        priority=5,
        destination_type=TrafficDestinationType.COMPUTE_NODE,
        output_destination_ids=("user-a",),
    )
    batch = generate_traffic_demand((profile,))

    timeline = batch.runtime_request_timeline(
        sim_time=12.0,
        lookback_window_s=5.0,
        lookahead_window_s=10.0,
        item_limit=2,
    )

    assert timeline["version"] == "v1"
    assert timeline["summary_id"] == "leo_twin.traffic_request_timeline.v1"
    assert timeline["source"] == "TrafficDemandBatch.records"
    assert timeline["metric_model"] == "FLOW_LEVEL_REQUEST_SCHEDULE"
    assert timeline["packet_level_simulation"] is False
    assert timeline["frontend_inference_required"] is False
    assert timeline["current_sim_time"] == 12.0
    assert timeline["request_count"] == 3
    assert timeline["state_counts"] == {
        "PAST": 1,
        "RECENTLY_ARRIVED": 1,
        "PENDING": 1,
    }
    assert timeline["recent_request_count"] == 1
    assert timeline["pending_request_count"] == 1
    assert timeline["past_request_count"] == 1
    assert timeline["window"] == {
        "lookback_window_s": 5.0,
        "lookahead_window_s": 10.0,
        "window_start_s": 7.0,
        "window_end_s": 22.0,
    }
    assert timeline["window_request_count"] == 2
    assert timeline["item_count"] == 2
    assert timeline["hidden_window_request_count"] == 0
    first, second = timeline["items"]
    assert first["arrival_time"] == 10.0
    assert first["time_offset_s"] == -2.0
    assert first["request_state"] == "RECENTLY_ARRIVED"
    assert first["service_state"] == "ARRIVED_IN_RECENT_WINDOW"
    assert first["traffic_class"] == "COMPUTE_SERVICE"
    assert first["destination_type"] == "COMPUTE_NODE"
    assert first["has_compute_task"] is True
    assert first["has_output_flow"] is True
    assert second["arrival_time"] == 20.0
    assert second["time_offset_s"] == 8.0
    assert second["request_state"] == "PENDING"
    assert second["service_state"] == "SCHEDULED"
    assert json.loads(json.dumps(timeline, sort_keys=True))["summary_id"] == (
        "leo_twin.traffic_request_timeline.v1"
    )


def test_runtime_business_activity_window_reports_time_varying_user_state() -> None:
    profiles = (
        TrafficDemandProfile(
            traffic_class=TrafficClass.COMPUTE_SERVICE,
            source_ids=("user-001",),
            destination_ids=("sat-compute-001",),
            request_count=3,
            arrival_interval=10.0,
            input_data_size=6.0,
            output_data_size=2.0,
            priority=5,
            destination_type=TrafficDestinationType.COMPUTE_NODE,
            output_destination_ids=("user-001",),
            id_prefix="biz",
        ),
        TrafficDemandProfile(
            traffic_class=TrafficClass.DATA_TRANSFER,
            source_ids=("user-002",),
            destination_ids=("gateway-001",),
            request_count=2,
            arrival_interval=30.0,
            input_data_size=1.5,
            start_time=8.0,
            priority=2,
            destination_type=TrafficDestinationType.SERVICE_ENDPOINT,
            id_prefix="data",
        ),
    )
    batch = generate_traffic_demand(profiles)

    first = batch.runtime_business_activity_window(
        sim_time=12.0,
        lookback_window_s=10.0,
        lookahead_window_s=12.0,
        assumed_service_duration_s=5.0,
        user_limit=8,
    )
    second = batch.runtime_business_activity_window(
        sim_time=12.0,
        lookback_window_s=10.0,
        lookahead_window_s=12.0,
        assumed_service_duration_s=5.0,
        user_limit=8,
    )

    assert first == second
    assert first["summary_id"] == "leo_twin.traffic_business_activity_window.v1"
    assert first["source"] == "TrafficDemandBatch.records"
    assert first["metric_model"] == "FLOW_LEVEL_BUSINESS_ACTIVITY_WINDOW"
    assert first["packet_level_simulation"] is False
    assert first["frontend_inference_required"] is False
    assert first["current_sim_time"] == 12.0
    assert first["request_count"] == 5
    assert first["user_count"] == 2
    assert first["active_user_count"] == 2
    assert first["recent_user_count"] == 0
    assert first["pending_user_count"] == 0
    assert first["idle_user_count"] == 0
    assert first["window"] == {
        "lookback_window_s": 10.0,
        "lookahead_window_s": 12.0,
        "window_start_s": 2.0,
        "window_end_s": 24.0,
        "assumed_service_duration_s": 5.0,
    }
    assert first["state_counts"] == {
        "ACTIVE_BUSINESS": 2,
        "RECENT_BUSINESS": 0,
        "PENDING_BUSINESS": 0,
        "IDLE": 0,
    }

    rows = {row["user_id"]: row for row in first["items"]}
    assert rows["user-001"]["business_state"] == "ACTIVE_BUSINESS"
    assert rows["user-001"]["active_request_count"] == 1
    assert rows["user-001"]["pending_request_count"] == 1
    assert rows["user-001"]["past_request_count"] == 1
    assert rows["user-001"]["compute_request_count"] == 3
    assert rows["user-001"]["communication_request_count"] == 0
    assert rows["user-001"]["current_or_next_business_type"] == "COMPUTE_SERVICE"
    assert rows["user-001"]["primary_target_id"] == "sat-compute-001"
    assert rows["user-001"]["selected_satellite_id"] == "sat-compute-001"
    assert rows["user-001"]["next_arrival_time"] == 20.0
    assert rows["user-001"]["time_to_next_request_s"] == 8.0
    assert rows["user-001"]["active_flow_ids"] == (
        "biz-00-compute_service-00001-input",
    )
    assert rows["user-001"]["pending_flow_ids"] == (
        "biz-00-compute_service-00002-input",
    )

    assert rows["user-002"]["business_state"] == "ACTIVE_BUSINESS"
    assert rows["user-002"]["platform_type"] == "GROUND_USER_TERMINAL"
    assert rows["user-002"]["service_classes"] == ("DATA_TRANSFER",)
    assert rows["user-002"]["primary_target_id"] == "gateway-001"
    assert rows["user-002"]["selected_satellite_id"] == ""
    assert rows["user-002"]["time_to_next_request_s"] == 26.0
    assert json.loads(json.dumps(first, sort_keys=True))["summary_id"] == (
        "leo_twin.traffic_business_activity_window.v1"
    )


def test_runtime_business_activity_window_limits_window_rows() -> None:
    profile = TrafficDemandProfile(
        traffic_class=TrafficClass.DATA_TRANSFER,
        source_ids=("user-001", "user-002"),
        destination_ids=("gateway-001",),
        request_count=2,
        arrival_interval=1.0,
        input_data_size=1.0,
        priority=1,
        id_prefix="limit",
    )
    batch = generate_traffic_demand((profile,))

    window = batch.runtime_business_activity_window(
        sim_time=1.0,
        lookback_window_s=1.0,
        lookahead_window_s=1.0,
        assumed_service_duration_s=10.0,
        user_limit=1,
    )

    assert window["window_user_count"] == 2
    assert window["item_count"] == 1
    assert window["hidden_window_user_count"] == 1
    assert len(window["items"]) == 1

    with pytest.raises(ValueError, match="user_limit"):
        batch.runtime_business_activity_window(sim_time=1.0, user_limit=0)


def test_burst_arrival_profile_groups_requests_deterministically() -> None:
    profile = TrafficDemandProfile(
        traffic_class=TrafficClass.DATA_TRANSFER,
        source_ids=("user-a",),
        destination_ids=("gateway-a",),
        request_count=7,
        arrival_interval=20.0,
        input_data_size=1.0,
        start_time=3.0,
        arrival_profile=TrafficArrivalProfile.BURST,
        burst_size=3,
        burst_spacing=0.5,
    )

    batch = generate_traffic_demand((profile,))

    assert tuple(record.arrival_time for record in batch.records) == (
        3.0,
        3.5,
        4.0,
        23.0,
        23.5,
        24.0,
        43.0,
    )


def test_diurnal_arrival_profile_is_deterministic_and_time_varying() -> None:
    profile = TrafficDemandProfile(
        traffic_class=TrafficClass.TELEMETRY,
        source_ids=("sensor-a",),
        destination_ids=("gateway-a",),
        request_count=5,
        arrival_interval=10.0,
        input_data_size=1.0,
        arrival_profile=TrafficArrivalProfile.DIURNAL,
        diurnal_period=40.0,
        diurnal_peak_time=0.0,
        diurnal_amplitude=0.5,
    )

    first = generate_traffic_demand((profile,))
    second = generate_traffic_demand((profile,))
    arrival_times = tuple(round(record.arrival_time, 6) for record in first.records)

    assert first == second
    assert arrival_times == (0.0, 5.0, 10.732233, 18.519147, 28.451816)
    assert arrival_times != (0.0, 10.0, 20.0, 30.0, 40.0)


def test_region_weighted_profile_uses_seeded_endpoint_selection() -> None:
    profile = TrafficDemandProfile(
        traffic_class=TrafficClass.DATA_TRANSFER,
        source_ids=("region-low", "region-high"),
        destination_ids=("gateway-a", "gateway-b"),
        request_count=8,
        arrival_interval=1.0,
        input_data_size=1.0,
        arrival_profile=TrafficArrivalProfile.REGION_WEIGHTED,
        seed=42,
        source_region_weights=(0.05, 0.95),
        destination_region_weights=(0.2, 0.8),
    )

    first = generate_traffic_demand((profile,))
    second = generate_traffic_demand((profile,))

    assert first == second
    assert tuple(flow.source_id for flow in first.flow_requests) == (
        "region-high",
        "region-high",
        "region-high",
        "region-high",
        "region-high",
        "region-high",
        "region-low",
        "region-high",
    )
    assert tuple(flow.target_id for flow in first.flow_requests) == (
        "gateway-b",
        "gateway-b",
        "gateway-b",
        "gateway-b",
        "gateway-a",
        "gateway-a",
        "gateway-b",
        "gateway-b",
    )
    assert tuple(record.arrival_time for record in first.records) == (
        0.0,
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
    )


def test_traffic_demand_profile_rejects_invalid_parameters() -> None:
    with pytest.raises(ValueError, match="arrival_interval"):
        TrafficDemandProfile(
            traffic_class=TrafficClass.DATA_TRANSFER,
            source_ids=("user-a",),
            destination_ids=("gateway-a",),
            request_count=1,
            arrival_interval=0.0,
            input_data_size=1.0,
        )

    with pytest.raises(ValueError, match="source_ids"):
        TrafficDemandProfile(
            traffic_class=TrafficClass.DATA_TRANSFER,
            source_ids=(),
            destination_ids=("gateway-a",),
            request_count=1,
            arrival_interval=1.0,
            input_data_size=1.0,
        )

    with pytest.raises(TypeError, match="priority"):
        TrafficDemandProfile(
            traffic_class=TrafficClass.DATA_TRANSFER,
            source_ids=("user-a",),
            destination_ids=("gateway-a",),
            request_count=1,
            arrival_interval=1.0,
            input_data_size=1.0,
            priority=True,
        )

    with pytest.raises(ValueError, match="burst_size"):
        TrafficDemandProfile(
            traffic_class=TrafficClass.DATA_TRANSFER,
            source_ids=("user-a",),
            destination_ids=("gateway-a",),
            request_count=1,
            arrival_interval=1.0,
            input_data_size=1.0,
            burst_size=0,
        )

    with pytest.raises(ValueError, match="diurnal_amplitude"):
        TrafficDemandProfile(
            traffic_class=TrafficClass.DATA_TRANSFER,
            source_ids=("user-a",),
            destination_ids=("gateway-a",),
            request_count=1,
            arrival_interval=1.0,
            input_data_size=1.0,
            diurnal_amplitude=1.5,
        )

    with pytest.raises(ValueError, match="source_region_weights"):
        TrafficDemandProfile(
            traffic_class=TrafficClass.DATA_TRANSFER,
            source_ids=("user-a", "user-b"),
            destination_ids=("gateway-a",),
            request_count=1,
            arrival_interval=1.0,
            input_data_size=1.0,
            source_region_weights=(1.0,),
        )


def test_service_mix_rejects_invalid_weights() -> None:
    with pytest.raises(ValueError, match="positive weight"):
        TrafficServiceMixConfig(
            total_request_count=1,
            arrival_interval=1.0,
            items=(
                TrafficServiceMixItem(
                    traffic_class=TrafficClass.DATA_TRANSFER,
                    weight=0.0,
                    source_ids=("user-a",),
                    destination_ids=("gateway-a",),
                    input_data_size=1.0,
                ),
            ),
        )

    with pytest.raises(ValueError, match="weight"):
        TrafficServiceMixItem(
            traffic_class=TrafficClass.DATA_TRANSFER,
            weight=-1.0,
            source_ids=("user-a",),
            destination_ids=("gateway-a",),
            input_data_size=1.0,
        )
