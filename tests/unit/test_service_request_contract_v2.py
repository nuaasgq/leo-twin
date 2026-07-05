from __future__ import annotations

import json

from leo_twin.models.traffic import (
    TrafficClass,
    TrafficDemandConfig,
    TrafficDemandModel,
    TrafficDemandProfile,
)
from leo_twin.schema import (
    SERVICE_REQUEST_CONTRACT_V2_ID,
    ServiceRequestFieldStatus,
    service_request_contract_v2_to_dict,
)


def test_service_request_contract_v2_is_deterministic_and_json_ready() -> None:
    first = service_request_contract_v2_to_dict()
    second = service_request_contract_v2_to_dict()

    assert first == second
    assert first["contract_id"] == SERVICE_REQUEST_CONTRACT_V2_ID
    assert first["version"] == "v2"
    assert first["request_model"] == "FLOW_LEVEL_USER_SERVICE_REQUEST"
    assert first["supported_classes"] == (
        "DATA_TRANSFER",
        "TELEMETRY",
        "BULK_DOWNLINK",
        "COMPUTE_SERVICE",
        "EMERGENCY",
    )
    assert json.loads(json.dumps(first, sort_keys=True))["contract_id"] == (
        SERVICE_REQUEST_CONTRACT_V2_ID
    )


def test_service_request_contract_v2_declares_required_business_fields() -> None:
    contract = service_request_contract_v2_to_dict()
    fields = {
        field["field"]: field
        for field in contract["fields"]
        if isinstance(field, dict)
    }

    assert {
        "service_id",
        "user_id",
        "service_class",
        "priority",
        "destination_policy",
        "destination_id",
        "input_data_mb",
        "output_data_mb",
        "duration_s",
        "deadline_s",
        "retry_policy",
    } <= set(fields)
    assert fields["service_id"]["required"] is True
    assert fields["service_id"]["implementation_status"] == (
        ServiceRequestFieldStatus.SUPPORTED.value
    )
    assert fields["deadline_s"]["implementation_status"] == (
        ServiceRequestFieldStatus.RESERVED.value
    )
    assert fields["retry_policy"]["runtime_mapping"] == ("NO_RETRY",)


def test_service_request_contract_v2_declares_compute_service_artifacts() -> None:
    contract = service_request_contract_v2_to_dict()
    artifacts = {
        artifact["kind"]: artifact
        for artifact in contract["generated_artifacts"]
        if isinstance(artifact, dict)
    }

    assert artifacts["INPUT_FLOW"]["event_type"] == "FLOW_ARRIVAL"
    assert artifacts["INPUT_FLOW"]["generated_for_classes"] == (
        "DATA_TRANSFER",
        "TELEMETRY",
        "BULK_DOWNLINK",
        "COMPUTE_SERVICE",
        "EMERGENCY",
    )
    assert artifacts["COMPUTE_TASK"]["generated_for_classes"] == (
        "COMPUTE_SERVICE",
    )
    assert artifacts["COMPUTE_TASK"]["id_policy"] == "service_id + '-task'"
    assert artifacts["OUTPUT_FLOW_METADATA"]["event_type"] == (
        "DEFERRED_OUTPUT_FLOW_METADATA"
    )
    assert "PACKET_LEVEL_TRAFFIC" in contract["excluded_semantics"]
    assert "EXTERNAL_SIMULATOR_INTEGRATION" in contract["excluded_semantics"]


def test_service_request_contract_matches_current_traffic_demand_id_policy() -> None:
    batch = TrafficDemandModel(
        config=TrafficDemandConfig(
            profiles=(
                TrafficDemandProfile(
                    traffic_class=TrafficClass.COMPUTE_SERVICE,
                    source_ids=("user-a",),
                    destination_ids=("sat-compute-a",),
                    request_count=1,
                    arrival_interval=5.0,
                    input_data_size=32.0,
                    output_data_size=4.0,
                    priority=7,
                    id_prefix="svc",
                ),
            )
        )
    ).generate()
    record = batch.records[0]

    assert record.input_flow.flow_id == "svc-00-compute_service-00000-input"
    assert record.input_flow.source_id == "user-a"
    assert record.input_flow.target_id == "sat-compute-a"
    assert record.input_flow.priority == 7
    assert record.task is not None
    assert record.task.task_id == "svc-00-compute_service-00000-task"
    assert record.task.flow_id == record.input_flow.flow_id
    assert record.output_flow is not None
    assert record.output_flow.flow_id == "svc-00-compute_service-00000-output"
    assert record.output_flow.input_flow_id == record.input_flow.flow_id
