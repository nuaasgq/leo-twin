from __future__ import annotations

import json

import pytest

from leo_twin.models.compute import (
    ComputeNode,
    ServicePlacementQueueState,
    place_compute_service,
)
from leo_twin.models.orbit import AutoPlaneAllocator
from leo_twin.schema import (
    SERVICE_PLACEMENT_CONTRACT_V2_ID,
    ServicePlacementDecisionStatus,
    ServicePlacementRejectionReason,
    TaskRequest,
    service_placement_contract_v2_to_dict,
)
from leo_twin.services.derived_summary import build_backend_derived_summary


def _task(
    task_id: str = "task-a",
    demand: float = 20.0,
    *,
    submit_time: float = 0.0,
    fp32_ops: float = 0.0,
    int8_ops: float = 0.0,
    memory_gb: float = 0.0,
) -> TaskRequest:
    return TaskRequest(
        task_id=task_id,
        source_id="user-a",
        submit_time=submit_time,
        compute_demand=demand,
        data_size=1.0,
        fp32_ops=fp32_ops,
        int8_ops=int8_ops,
        memory_gb=memory_gb,
    )


def test_service_placement_contract_v2_is_deterministic_and_json_ready() -> None:
    first = service_placement_contract_v2_to_dict()
    second = service_placement_contract_v2_to_dict()

    assert first == second
    assert first["contract_id"] == SERVICE_PLACEMENT_CONTRACT_V2_ID
    assert first["version"] == "v2"
    assert first["default_policy"] == "MIN_ESTIMATED_FINISH_TIME"
    assert first["candidate_order"] == ("finish_time", "start_time", "node_id")
    assert "QUEUE_LIMIT_EXCEEDED" in first["rejection_reasons"]
    assert json.loads(json.dumps(first, sort_keys=True))["contract_id"] == (
        SERVICE_PLACEMENT_CONTRACT_V2_ID
    )


def test_place_compute_service_selects_min_estimated_finish_time() -> None:
    task = _task(demand=80.0)
    nodes = (
        ComputeNode("sat-002", capacity=20.0),
        ComputeNode("sat-001", capacity=40.0),
    )

    decision = place_compute_service(task, nodes, ready_time=1.0)

    assert decision.status == ServicePlacementDecisionStatus.PLACED
    assert decision.selected_node_id == "sat-001"
    assert decision.start_time == 1.0
    assert decision.finish_time == pytest.approx(3.0)
    assert decision.queue_delay == 0.0
    assert decision.execution_delay == pytest.approx(2.0)
    assert decision.bottleneck_resource == "cpu_gflops_fp32"
    assert decision.candidate_count == 2
    assert decision.capable_candidate_count == 2
    assert tuple(candidate.node_id for candidate in decision.candidates) == (
        "sat-001",
        "sat-002",
    )


def test_place_compute_service_uses_queue_state_in_finish_time() -> None:
    task = _task(demand=100.0)
    nodes = (
        ComputeNode("sat-a", capacity=100.0),
        ComputeNode("sat-b", capacity=20.0),
    )
    queue_states = (
        ServicePlacementQueueState("sat-a", available_at=4.0, queued_task_count=1),
    )

    decision = place_compute_service(
        task,
        nodes,
        ready_time=1.0,
        queue_states=queue_states,
    )

    assert decision.status == ServicePlacementDecisionStatus.QUEUED
    assert decision.selected_node_id == "sat-a"
    assert decision.start_time == 4.0
    assert decision.finish_time == pytest.approx(5.0)
    assert decision.queue_delay == pytest.approx(3.0)
    assert decision.execution_delay == pytest.approx(1.0)


def test_place_compute_service_rejects_when_no_candidate_has_required_lane() -> None:
    task = _task(demand=0.0, fp32_ops=2_000_000_000_000.0)
    nodes = (
        ComputeNode("sat-a", capacity=40.0),
        ComputeNode("sat-b", capacity=50.0),
    )

    decision = place_compute_service(task, nodes)

    assert decision.status == ServicePlacementDecisionStatus.REJECTED
    assert decision.rejection_reason == ServicePlacementRejectionReason.NO_CAPABLE_NODE
    assert decision.selected_node_id is None
    assert decision.candidate_count == 2
    assert decision.capable_candidate_count == 0
    assert {
        candidate.rejection_reason for candidate in decision.candidates
    } == {ServicePlacementRejectionReason.CAPACITY_LIMIT_EXCEEDED}


def test_place_compute_service_skips_full_queue_and_selects_available_node() -> None:
    task = _task(demand=100.0)
    nodes = (
        ComputeNode("sat-a", capacity=100.0),
        ComputeNode("sat-b", capacity=50.0),
    )
    queue_states = (
        ServicePlacementQueueState("sat-a", available_at=4.0, queued_task_count=2),
    )

    decision = place_compute_service(
        task,
        nodes,
        ready_time=1.0,
        queue_states=queue_states,
        max_queue_depth=2,
    )

    assert decision.status == ServicePlacementDecisionStatus.PLACED
    assert decision.selected_node_id == "sat-b"
    assert decision.finish_time == pytest.approx(3.0)
    assert decision.capable_candidate_count == 1
    rejected = {
        candidate.node_id: candidate.rejection_reason
        for candidate in decision.candidates
        if not candidate.accepted
    }
    assert rejected == {
        "sat-a": ServicePlacementRejectionReason.QUEUE_LIMIT_EXCEEDED
    }


def test_backend_summary_exposes_service_placement_contract_v2() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=72, plane_count=12)

    summary = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=72,
        user_count=100,
        compute_node_count=72,
        compute_capacity=40.0,
        flow_count=20,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
    )

    contract = summary["service_placement_contract_v2"]
    assert isinstance(contract, dict)
    assert contract["contract_id"] == SERVICE_PLACEMENT_CONTRACT_V2_ID
    assert contract["configured_policy"] == {
        "compute_node_count": 72,
        "default_policy": "MIN_ESTIMATED_FINISH_TIME",
        "queue_state_source": "RouteAwareComputeEngine._available_at",
        "max_queue_depth": None,
        "candidate_count_policy": (
            "Route path compute nodes are preferred when available; otherwise "
            "all configured satellite compute nodes remain candidates."
        ),
    }
