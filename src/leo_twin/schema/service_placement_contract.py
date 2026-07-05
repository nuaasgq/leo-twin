"""Product-level service placement contract v2."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


SERVICE_PLACEMENT_CONTRACT_V2_ID = "leo_twin.service_placement_contract.v2"


class ServicePlacementPolicy(StrEnum):
    """Deterministic policies for selecting a compute service node."""

    MIN_ESTIMATED_FINISH_TIME = "MIN_ESTIMATED_FINISH_TIME"


class ServicePlacementDecisionStatus(StrEnum):
    """Canonical service placement decision status."""

    PLACED = "PLACED"
    QUEUED = "QUEUED"
    REJECTED = "REJECTED"


class ServicePlacementRejectionReason(StrEnum):
    """Canonical reasons a placement candidate or request can be rejected."""

    NO_NODES = "NO_NODES"
    NO_CAPABLE_NODE = "NO_CAPABLE_NODE"
    CAPACITY_LIMIT_EXCEEDED = "CAPACITY_LIMIT_EXCEEDED"
    QUEUE_LIMIT_EXCEEDED = "QUEUE_LIMIT_EXCEEDED"


@dataclass(frozen=True)
class ServicePlacementContractV2:
    """Versioned product contract for communication-compute service placement."""

    contract_id: str
    version: str
    placement_model: str
    default_policy: ServicePlacementPolicy
    candidate_source: str
    candidate_order: tuple[str, ...]
    decision_fields: tuple[str, ...]
    rejection_reasons: tuple[ServicePlacementRejectionReason, ...]
    queue_semantics: str
    deterministic_inputs: tuple[str, ...]
    excluded_semantics: tuple[str, ...]
    model_note: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.contract_id, "contract_id")
        _require_non_empty_str(self.version, "version")
        _require_non_empty_str(self.placement_model, "placement_model")
        if not isinstance(self.default_policy, ServicePlacementPolicy):
            object.__setattr__(
                self,
                "default_policy",
                ServicePlacementPolicy(str(self.default_policy)),
            )
        _require_non_empty_str(self.candidate_source, "candidate_source")
        object.__setattr__(
            self,
            "candidate_order",
            _normalize_str_tuple(self.candidate_order, "candidate_order"),
        )
        object.__setattr__(
            self,
            "decision_fields",
            _normalize_str_tuple(self.decision_fields, "decision_fields"),
        )
        if not self.rejection_reasons:
            raise ValueError("rejection_reasons must not be empty")
        object.__setattr__(
            self,
            "rejection_reasons",
            tuple(
                reason
                if isinstance(reason, ServicePlacementRejectionReason)
                else ServicePlacementRejectionReason(str(reason))
                for reason in self.rejection_reasons
            ),
        )
        _require_non_empty_str(self.queue_semantics, "queue_semantics")
        object.__setattr__(
            self,
            "deterministic_inputs",
            _normalize_str_tuple(self.deterministic_inputs, "deterministic_inputs"),
        )
        object.__setattr__(
            self,
            "excluded_semantics",
            _normalize_str_tuple(self.excluded_semantics, "excluded_semantics"),
        )
        _require_non_empty_str(self.model_note, "model_note")

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "version": self.version,
            "placement_model": self.placement_model,
            "default_policy": self.default_policy.value,
            "candidate_source": self.candidate_source,
            "candidate_order": self.candidate_order,
            "decision_fields": self.decision_fields,
            "rejection_reasons": tuple(reason.value for reason in self.rejection_reasons),
            "queue_semantics": self.queue_semantics,
            "deterministic_inputs": self.deterministic_inputs,
            "excluded_semantics": self.excluded_semantics,
            "model_note": self.model_note,
        }


def default_service_placement_contract_v2() -> ServicePlacementContractV2:
    """Build the default SEES service placement contract v2."""

    return ServicePlacementContractV2(
        contract_id=SERVICE_PLACEMENT_CONTRACT_V2_ID,
        version="v2",
        placement_model="DETERMINISTIC_MIN_ESTIMATED_FINISH_TIME",
        default_policy=ServicePlacementPolicy.MIN_ESTIMATED_FINISH_TIME,
        candidate_source=(
            "Route path compute nodes when network context is available; "
            "otherwise all configured satellite-hosted compute nodes."
        ),
        candidate_order=("finish_time", "start_time", "node_id"),
        decision_fields=(
            "task_id",
            "status",
            "selected_node_id",
            "ready_time",
            "start_time",
            "finish_time",
            "queue_delay",
            "execution_delay",
            "bottleneck_resource",
            "rejection_reason",
        ),
        rejection_reasons=(
            ServicePlacementRejectionReason.NO_NODES,
            ServicePlacementRejectionReason.NO_CAPABLE_NODE,
            ServicePlacementRejectionReason.CAPACITY_LIMIT_EXCEEDED,
            ServicePlacementRejectionReason.QUEUE_LIMIT_EXCEEDED,
        ),
        queue_semantics=(
            "A node queue state supplies available_at and queued_task_count. "
            "A selected request is QUEUED when start_time is later than ready_time."
        ),
        deterministic_inputs=(
            "TaskRequest.resource_demand",
            "ComputeNode.resource_vector",
            "ServicePlacementQueueState.available_at",
            "ServicePlacementQueueState.queued_task_count",
            "service_placement_policy",
            "max_queue_depth",
        ),
        excluded_semantics=(
            "PREEMPTION",
            "THREAD_LEVEL_EXECUTION",
            "PACKET_LEVEL_QUEUEING",
            "POWER_THERMAL_AWARE_PLACEMENT",
            "STOCHASTIC_LOAD_BALANCING",
        ),
        model_note=(
            "Service placement is a deterministic flow-level abstraction. It "
            "chooses satellite compute nodes using estimated finish time and "
            "explicit queue state, but does not execute code or model packets."
        ),
    )


def service_placement_contract_v2_to_dict(
    contract: ServicePlacementContractV2 | None = None,
) -> dict[str, object]:
    """Return the default or supplied placement contract as JSON-compatible data."""

    selected = default_service_placement_contract_v2() if contract is None else contract
    if not isinstance(selected, ServicePlacementContractV2):
        raise TypeError("contract must be ServicePlacementContractV2 or None")
    return selected.to_dict()


def _normalize_str_tuple(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    normalized = tuple(str(value) for value in values)
    if any(not value for value in normalized):
        raise ValueError(f"{field_name} must not contain empty values")
    return normalized


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


__all__ = [
    "SERVICE_PLACEMENT_CONTRACT_V2_ID",
    "ServicePlacementContractV2",
    "ServicePlacementDecisionStatus",
    "ServicePlacementPolicy",
    "ServicePlacementRejectionReason",
    "default_service_placement_contract_v2",
    "service_placement_contract_v2_to_dict",
]
