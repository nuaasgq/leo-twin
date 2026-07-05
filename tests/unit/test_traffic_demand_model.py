from __future__ import annotations

import pytest

from leo_twin.models.traffic import (
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
        TrafficClass.DATA_TRANSFER,
        TrafficClass.DATA_TRANSFER,
        TrafficClass.DATA_TRANSFER,
        TrafficClass.DATA_TRANSFER,
        TrafficClass.DATA_TRANSFER,
        TrafficClass.COMPUTE_SERVICE,
    )
    assert batch.records[5].task is not None
    assert batch.records[5].task.compute_demand == 16.0
    assert batch.records[5].task.fp32_ops == 1_000.0
    assert batch.records[5].task.memory_gb == 2.0
    assert batch.records[5].output_flow is not None
    assert batch.records[5].output_flow.target_id == "user-a"
    assert tuple(event.sim_time for event in batch.flow_arrival_events()) == (
        1.0,
        4.0,
        7.0,
        10.0,
        13.0,
        1.0,
        4.0,
        7.0,
        1.0,
        4.0,
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
