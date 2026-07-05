"""Deterministic communication-compute service placement model."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Iterable

from leo_twin.models.compute.contracts import ComputeNode
from leo_twin.models.compute.resources import estimate_task_service_time
from leo_twin.schema import TaskRequest
from leo_twin.schema.service_placement_contract import (
    ServicePlacementDecisionStatus,
    ServicePlacementPolicy,
    ServicePlacementRejectionReason,
)


@dataclass(frozen=True)
class ServicePlacementQueueState:
    """Explicit queue state for one candidate compute node."""

    node_id: str
    available_at: float = 0.0
    queued_task_count: int = 0

    def __post_init__(self) -> None:
        _require_non_empty_str(self.node_id, "node_id")
        _require_non_negative_number(self.available_at, "available_at")
        _require_non_negative_int(self.queued_task_count, "queued_task_count")
        object.__setattr__(self, "available_at", float(self.available_at))


@dataclass(frozen=True)
class ServicePlacementCandidate:
    """Per-candidate deterministic placement evaluation."""

    node_id: str
    status: ServicePlacementDecisionStatus
    rejection_reason: ServicePlacementRejectionReason | None = None
    available_at: float = 0.0
    queued_task_count: int = 0
    ready_time: float = 0.0
    start_time: float | None = None
    finish_time: float | None = None
    queue_delay: float | None = None
    execution_delay: float | None = None
    bottleneck_resource: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_str(self.node_id, "node_id")
        if not isinstance(self.status, ServicePlacementDecisionStatus):
            object.__setattr__(
                self,
                "status",
                ServicePlacementDecisionStatus(str(self.status)),
            )
        if self.rejection_reason is not None and not isinstance(
            self.rejection_reason,
            ServicePlacementRejectionReason,
        ):
            object.__setattr__(
                self,
                "rejection_reason",
                ServicePlacementRejectionReason(str(self.rejection_reason)),
            )
        _require_non_negative_number(self.available_at, "available_at")
        _require_non_negative_int(self.queued_task_count, "queued_task_count")
        _require_non_negative_number(self.ready_time, "ready_time")
        for field_name in (
            "start_time",
            "finish_time",
            "queue_delay",
            "execution_delay",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_non_negative_number(value, field_name)
        if self.bottleneck_resource is not None:
            _require_non_empty_str(self.bottleneck_resource, "bottleneck_resource")

    @property
    def accepted(self) -> bool:
        return self.rejection_reason is None

    def to_dict(self) -> dict[str, object]:
        return {
            "node_id": self.node_id,
            "status": self.status.value,
            "rejection_reason": (
                None
                if self.rejection_reason is None
                else self.rejection_reason.value
            ),
            "available_at": self.available_at,
            "queued_task_count": self.queued_task_count,
            "ready_time": self.ready_time,
            "start_time": self.start_time,
            "finish_time": self.finish_time,
            "queue_delay": self.queue_delay,
            "execution_delay": self.execution_delay,
            "bottleneck_resource": self.bottleneck_resource,
        }


@dataclass(frozen=True)
class ServicePlacementDecision:
    """Deterministic placement decision for one compute service task."""

    task_id: str
    status: ServicePlacementDecisionStatus
    policy: ServicePlacementPolicy
    ready_time: float
    selected_node_id: str | None = None
    start_time: float | None = None
    finish_time: float | None = None
    queue_delay: float | None = None
    execution_delay: float | None = None
    bottleneck_resource: str | None = None
    rejection_reason: ServicePlacementRejectionReason | None = None
    candidate_count: int = 0
    capable_candidate_count: int = 0
    candidates: tuple[ServicePlacementCandidate, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty_str(self.task_id, "task_id")
        if not isinstance(self.status, ServicePlacementDecisionStatus):
            object.__setattr__(
                self,
                "status",
                ServicePlacementDecisionStatus(str(self.status)),
            )
        if not isinstance(self.policy, ServicePlacementPolicy):
            object.__setattr__(
                self,
                "policy",
                ServicePlacementPolicy(str(self.policy)),
            )
        _require_non_negative_number(self.ready_time, "ready_time")
        if self.selected_node_id is not None:
            _require_non_empty_str(self.selected_node_id, "selected_node_id")
        for field_name in (
            "start_time",
            "finish_time",
            "queue_delay",
            "execution_delay",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_non_negative_number(value, field_name)
        if self.bottleneck_resource is not None:
            _require_non_empty_str(self.bottleneck_resource, "bottleneck_resource")
        if self.rejection_reason is not None and not isinstance(
            self.rejection_reason,
            ServicePlacementRejectionReason,
        ):
            object.__setattr__(
                self,
                "rejection_reason",
                ServicePlacementRejectionReason(str(self.rejection_reason)),
            )
        _require_non_negative_int(self.candidate_count, "candidate_count")
        _require_non_negative_int(
            self.capable_candidate_count,
            "capable_candidate_count",
        )
        if not isinstance(self.candidates, tuple):
            raise TypeError("candidates must be a tuple")
        if any(not isinstance(item, ServicePlacementCandidate) for item in self.candidates):
            raise TypeError("candidates must contain ServicePlacementCandidate")

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "policy": self.policy.value,
            "ready_time": self.ready_time,
            "selected_node_id": self.selected_node_id,
            "start_time": self.start_time,
            "finish_time": self.finish_time,
            "queue_delay": self.queue_delay,
            "execution_delay": self.execution_delay,
            "bottleneck_resource": self.bottleneck_resource,
            "rejection_reason": (
                None
                if self.rejection_reason is None
                else self.rejection_reason.value
            ),
            "candidate_count": self.candidate_count,
            "capable_candidate_count": self.capable_candidate_count,
            "candidates": tuple(candidate.to_dict() for candidate in self.candidates),
        }


def place_compute_service(
    task: TaskRequest,
    nodes: Iterable[ComputeNode],
    *,
    queue_states: Iterable[ServicePlacementQueueState] = (),
    ready_time: float | None = None,
    policy: ServicePlacementPolicy | str = ServicePlacementPolicy.MIN_ESTIMATED_FINISH_TIME,
    max_queue_depth: int | None = None,
) -> ServicePlacementDecision:
    """Return a deterministic service placement decision for one task."""

    if not isinstance(task, TaskRequest):
        raise TypeError("task must be TaskRequest")
    selected_policy = _coerce_policy(policy)
    if selected_policy != ServicePlacementPolicy.MIN_ESTIMATED_FINISH_TIME:
        raise ValueError(f"unsupported service placement policy: {selected_policy}")
    selected_ready_time = task.submit_time if ready_time is None else ready_time
    _require_non_negative_number(selected_ready_time, "ready_time")
    if max_queue_depth is not None:
        _require_non_negative_int(max_queue_depth, "max_queue_depth")

    ordered_nodes = tuple(sorted(nodes, key=lambda item: item.node_id))
    if any(not isinstance(node, ComputeNode) for node in ordered_nodes):
        raise TypeError("nodes must contain ComputeNode")
    if len({node.node_id for node in ordered_nodes}) != len(ordered_nodes):
        raise ValueError("node ids must be unique")

    queue_by_node = _queue_states_by_node(queue_states, ordered_nodes)
    if not ordered_nodes:
        return _rejected_decision(
            task=task,
            policy=selected_policy,
            ready_time=float(selected_ready_time),
            candidates=(),
            reason=ServicePlacementRejectionReason.NO_NODES,
        )

    evaluated = tuple(
        _evaluate_candidate(
            task=task,
            node=node,
            queue_state=queue_by_node[node.node_id],
            ready_time=float(selected_ready_time),
            max_queue_depth=max_queue_depth,
        )
        for node in ordered_nodes
    )
    accepted = tuple(candidate for candidate in evaluated if candidate.accepted)
    if not accepted:
        return _rejected_decision(
            task=task,
            policy=selected_policy,
            ready_time=float(selected_ready_time),
            candidates=evaluated,
            reason=ServicePlacementRejectionReason.NO_CAPABLE_NODE,
        )

    selected = min(
        accepted,
        key=lambda candidate: (
            float(candidate.finish_time),
            float(candidate.start_time),
            candidate.node_id,
        ),
    )
    status = (
        ServicePlacementDecisionStatus.QUEUED
        if float(selected.queue_delay) > 0.0
        else ServicePlacementDecisionStatus.PLACED
    )
    return ServicePlacementDecision(
        task_id=task.task_id,
        status=status,
        policy=selected_policy,
        ready_time=float(selected_ready_time),
        selected_node_id=selected.node_id,
        start_time=selected.start_time,
        finish_time=selected.finish_time,
        queue_delay=selected.queue_delay,
        execution_delay=selected.execution_delay,
        bottleneck_resource=selected.bottleneck_resource,
        candidate_count=len(evaluated),
        capable_candidate_count=len(accepted),
        candidates=evaluated,
    )


def _evaluate_candidate(
    *,
    task: TaskRequest,
    node: ComputeNode,
    queue_state: ServicePlacementQueueState,
    ready_time: float,
    max_queue_depth: int | None,
) -> ServicePlacementCandidate:
    start_time = max(ready_time, queue_state.available_at)
    will_wait = start_time > ready_time
    if (
        max_queue_depth is not None
        and will_wait
        and queue_state.queued_task_count >= max_queue_depth
    ):
        return ServicePlacementCandidate(
            node_id=node.node_id,
            status=ServicePlacementDecisionStatus.REJECTED,
            rejection_reason=ServicePlacementRejectionReason.QUEUE_LIMIT_EXCEEDED,
            available_at=queue_state.available_at,
            queued_task_count=queue_state.queued_task_count,
            ready_time=ready_time,
        )
    try:
        estimate = estimate_task_service_time(node, task)
    except ValueError:
        return ServicePlacementCandidate(
            node_id=node.node_id,
            status=ServicePlacementDecisionStatus.REJECTED,
            rejection_reason=ServicePlacementRejectionReason.CAPACITY_LIMIT_EXCEEDED,
            available_at=queue_state.available_at,
            queued_task_count=queue_state.queued_task_count,
            ready_time=ready_time,
        )
    finish_time = start_time + estimate.service_time
    queue_delay = max(0.0, start_time - ready_time)
    status = (
        ServicePlacementDecisionStatus.QUEUED
        if queue_delay > 0.0
        else ServicePlacementDecisionStatus.PLACED
    )
    return ServicePlacementCandidate(
        node_id=node.node_id,
        status=status,
        available_at=queue_state.available_at,
        queued_task_count=queue_state.queued_task_count,
        ready_time=ready_time,
        start_time=start_time,
        finish_time=finish_time,
        queue_delay=queue_delay,
        execution_delay=estimate.service_time,
        bottleneck_resource=estimate.bottleneck_resource,
    )


def _queue_states_by_node(
    queue_states: Iterable[ServicePlacementQueueState],
    nodes: tuple[ComputeNode, ...],
) -> dict[str, ServicePlacementQueueState]:
    node_ids = {node.node_id for node in nodes}
    default_states = {
        node.node_id: ServicePlacementQueueState(node.node_id) for node in nodes
    }
    for state in queue_states:
        if not isinstance(state, ServicePlacementQueueState):
            raise TypeError("queue_states must contain ServicePlacementQueueState")
        if state.node_id not in node_ids:
            raise ValueError(f"queue state references unknown node: {state.node_id}")
        default_states[state.node_id] = state
    return default_states


def _rejected_decision(
    *,
    task: TaskRequest,
    policy: ServicePlacementPolicy,
    ready_time: float,
    candidates: tuple[ServicePlacementCandidate, ...],
    reason: ServicePlacementRejectionReason,
) -> ServicePlacementDecision:
    return ServicePlacementDecision(
        task_id=task.task_id,
        status=ServicePlacementDecisionStatus.REJECTED,
        policy=policy,
        ready_time=ready_time,
        rejection_reason=reason,
        candidate_count=len(candidates),
        capable_candidate_count=0,
        candidates=candidates,
    )


def _coerce_policy(policy: ServicePlacementPolicy | str) -> ServicePlacementPolicy:
    if isinstance(policy, ServicePlacementPolicy):
        return policy
    return ServicePlacementPolicy(str(policy))


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


def _require_non_negative_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_non_negative_int(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


__all__ = [
    "ServicePlacementCandidate",
    "ServicePlacementDecision",
    "ServicePlacementQueueState",
    "place_compute_service",
]
