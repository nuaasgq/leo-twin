"""Product-level cache/offload/migration contract v1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


CACHE_OFFLOAD_MIGRATION_CONTRACT_V1_ID = (
    "leo_twin.cache_offload_migration_contract.v1"
)


class ComputeServiceActionKind(StrEnum):
    """Product-level actions for compute-network service optimization."""

    CACHE_LOOKUP = "CACHE_LOOKUP"
    CACHE_FILL = "CACHE_FILL"
    TASK_OFFLOAD = "TASK_OFFLOAD"
    SERVICE_MIGRATION = "SERVICE_MIGRATION"


class ComputeServiceActionStatus(StrEnum):
    """Canonical action status for observability."""

    NOT_EVALUATED = "NOT_EVALUATED"
    ELIGIBLE = "ELIGIBLE"
    SELECTED = "SELECTED"
    SKIPPED = "SKIPPED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ComputeServiceActionContract:
    """One action family inside the cache/offload/migration contract."""

    action: ComputeServiceActionKind
    decision_model: str
    eligibility_fields: tuple[str, ...]
    decision_fields: tuple[str, ...]
    runtime_observability_fields: tuple[str, ...]
    excluded_semantics: tuple[str, ...]
    model_note: str

    def __post_init__(self) -> None:
        if not isinstance(self.action, ComputeServiceActionKind):
            object.__setattr__(
                self,
                "action",
                ComputeServiceActionKind(str(self.action)),
            )
        _require_non_empty_str(self.decision_model, "decision_model")
        object.__setattr__(
            self,
            "eligibility_fields",
            _normalize_str_tuple(self.eligibility_fields, "eligibility_fields"),
        )
        object.__setattr__(
            self,
            "decision_fields",
            _normalize_str_tuple(self.decision_fields, "decision_fields"),
        )
        object.__setattr__(
            self,
            "runtime_observability_fields",
            _normalize_str_tuple(
                self.runtime_observability_fields,
                "runtime_observability_fields",
            ),
        )
        object.__setattr__(
            self,
            "excluded_semantics",
            _normalize_str_tuple(self.excluded_semantics, "excluded_semantics"),
        )
        _require_non_empty_str(self.model_note, "model_note")

    def to_dict(self) -> dict[str, object]:
        return {
            "action": self.action.value,
            "decision_model": self.decision_model,
            "eligibility_fields": self.eligibility_fields,
            "decision_fields": self.decision_fields,
            "runtime_observability_fields": self.runtime_observability_fields,
            "excluded_semantics": self.excluded_semantics,
            "model_note": self.model_note,
        }


@dataclass(frozen=True)
class CacheOffloadMigrationContractV1:
    """Versioned product contract for future cache/offload/migration behavior."""

    contract_id: str
    version: str
    optimization_scope: str
    action_contracts: tuple[ComputeServiceActionContract, ...]
    canonical_statuses: tuple[ComputeServiceActionStatus, ...]
    deterministic_inputs: tuple[str, ...]
    runtime_event_inputs: tuple[str, ...]
    runtime_state_outputs: tuple[str, ...]
    excluded_semantics: tuple[str, ...]
    model_note: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.contract_id, "contract_id")
        _require_non_empty_str(self.version, "version")
        _require_non_empty_str(self.optimization_scope, "optimization_scope")
        if not self.action_contracts:
            raise ValueError("action_contracts must not be empty")
        if any(
            not isinstance(contract, ComputeServiceActionContract)
            for contract in self.action_contracts
        ):
            raise TypeError(
                "action_contracts must contain ComputeServiceActionContract"
            )
        if not self.canonical_statuses:
            raise ValueError("canonical_statuses must not be empty")
        object.__setattr__(
            self,
            "canonical_statuses",
            tuple(
                status
                if isinstance(status, ComputeServiceActionStatus)
                else ComputeServiceActionStatus(str(status))
                for status in self.canonical_statuses
            ),
        )
        object.__setattr__(
            self,
            "deterministic_inputs",
            _normalize_str_tuple(self.deterministic_inputs, "deterministic_inputs"),
        )
        object.__setattr__(
            self,
            "runtime_event_inputs",
            _normalize_str_tuple(self.runtime_event_inputs, "runtime_event_inputs"),
        )
        object.__setattr__(
            self,
            "runtime_state_outputs",
            _normalize_str_tuple(self.runtime_state_outputs, "runtime_state_outputs"),
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
            "optimization_scope": self.optimization_scope,
            "action_contracts": tuple(
                contract.to_dict() for contract in self.action_contracts
            ),
            "canonical_statuses": tuple(
                status.value for status in self.canonical_statuses
            ),
            "deterministic_inputs": self.deterministic_inputs,
            "runtime_event_inputs": self.runtime_event_inputs,
            "runtime_state_outputs": self.runtime_state_outputs,
            "excluded_semantics": self.excluded_semantics,
            "model_note": self.model_note,
        }


def default_cache_offload_migration_contract_v1() -> CacheOffloadMigrationContractV1:
    """Build the default SEES cache/offload/migration contract."""

    return CacheOffloadMigrationContractV1(
        contract_id=CACHE_OFFLOAD_MIGRATION_CONTRACT_V1_ID,
        version="v1",
        optimization_scope=(
            "CONTRACT_AND_OBSERVABILITY_ONLY_FOR_SATELLITE_HOSTED_COMPUTE_SERVICES"
        ),
        action_contracts=(
            ComputeServiceActionContract(
                action=ComputeServiceActionKind.CACHE_LOOKUP,
                decision_model="DETERMINISTIC_CACHE_KEY_AND_TTL_POLICY",
                eligibility_fields=(
                    "task.cache_key",
                    "service.input_flow_id",
                    "selected_compute_node_id",
                ),
                decision_fields=(
                    "cache_lookup_status",
                    "cache_hit",
                    "cache_node_id",
                    "cache_age_s",
                ),
                runtime_observability_fields=(
                    "cache_lookup_status",
                    "cache_hit",
                    "cache_node_id",
                    "cache_age_s",
                ),
                excluded_semantics=(
                    "CONTENT_ADDRESSABLE_STORAGE_ENGINE",
                    "CACHE_COHERENCY_PROTOCOL",
                    "PROBABILISTIC_CACHE_REPLACEMENT",
                ),
                model_note=(
                    "Cache lookup is a future deterministic service-level "
                    "decision. It is not active runtime behavior in v1."
                ),
            ),
            ComputeServiceActionContract(
                action=ComputeServiceActionKind.CACHE_FILL,
                decision_model="DETERMINISTIC_RESULT_SIZE_AND_STORAGE_POLICY",
                eligibility_fields=(
                    "TaskRequest.output_data_mb",
                    "ComputeNode.storage_gb",
                    "service_complete",
                ),
                decision_fields=(
                    "cache_fill_status",
                    "cache_fill_node_id",
                    "cache_fill_size_mb",
                    "cache_ttl_s",
                ),
                runtime_observability_fields=(
                    "cache_fill_status",
                    "cache_fill_node_id",
                    "cache_fill_size_mb",
                    "cache_ttl_s",
                ),
                excluded_semantics=(
                    "STORAGE_IO_TIMING_MODEL",
                    "WEAR_LEVELING",
                    "DISTRIBUTED_CACHE_REPLICATION",
                ),
                model_note=(
                    "Cache fill is a future result-retention decision bounded "
                    "by deterministic output size and storage capacity."
                ),
            ),
            ComputeServiceActionContract(
                action=ComputeServiceActionKind.TASK_OFFLOAD,
                decision_model="DETERMINISTIC_ROUTE_AND_RESOURCE_BENEFIT_POLICY",
                eligibility_fields=(
                    "service_placement_candidate_count",
                    "service_placement_capable_candidate_count",
                    "input_network_latency_s",
                    "compute_execution_delay_s",
                ),
                decision_fields=(
                    "offload_status",
                    "offload_source_node_id",
                    "offload_target_node_id",
                    "offload_reason",
                ),
                runtime_observability_fields=(
                    "offload_status",
                    "offload_source_node_id",
                    "offload_target_node_id",
                    "offload_reason",
                ),
                excluded_semantics=(
                    "LIVE_PROCESS_MIGRATION",
                    "THREAD_LEVEL_WORK_STEALING",
                    "PACKET_LEVEL_OFFLOAD_CONTROL",
                ),
                model_note=(
                    "Task offload is a future flow-level decision over route "
                    "and resource summaries, not packet-level control."
                ),
            ),
            ComputeServiceActionContract(
                action=ComputeServiceActionKind.SERVICE_MIGRATION,
                decision_model="DETERMINISTIC_STATE_TRANSFER_COST_POLICY",
                eligibility_fields=(
                    "service_state_size_mb",
                    "current_compute_node_id",
                    "candidate_compute_node_id",
                    "remaining_execution_delay_s",
                ),
                decision_fields=(
                    "migration_status",
                    "migration_source_node_id",
                    "migration_target_node_id",
                    "migration_cost_s",
                ),
                runtime_observability_fields=(
                    "migration_status",
                    "migration_source_node_id",
                    "migration_target_node_id",
                    "migration_cost_s",
                ),
                excluded_semantics=(
                    "REAL_PROCESS_CHECKPOINT_RESTORE",
                    "MEMORY_PAGE_TRANSFER",
                    "CONSISTENCY_PROTOCOL",
                ),
                model_note=(
                    "Service migration is a future deterministic state-transfer "
                    "abstraction. It does not move real execution state in v1."
                ),
            ),
        ),
        canonical_statuses=(
            ComputeServiceActionStatus.NOT_EVALUATED,
            ComputeServiceActionStatus.ELIGIBLE,
            ComputeServiceActionStatus.SELECTED,
            ComputeServiceActionStatus.SKIPPED,
            ComputeServiceActionStatus.REJECTED,
        ),
        deterministic_inputs=(
            "TaskRequest.task_id",
            "TaskRequest.input_data_mb",
            "TaskRequest.output_data_mb",
            "ComputeNodeState.available_storage_gb",
            "service_latency_history_v1",
            "service_placement_contract_v2",
        ),
        runtime_event_inputs=(
            "TASK_ARRIVAL",
            "TASK_START",
            "TASK_FINISH",
            "FLOW_COMPLETE",
            "METRIC_SAMPLE",
        ),
        runtime_state_outputs=(
            "service_latency_history_v1",
            "compute_task_timeline_summary_v1",
            "node_detail_summary_v1",
            "MetricRecord",
        ),
        excluded_semantics=(
            "REAL_CACHE_ENGINE",
            "REAL_CODE_EXECUTION",
            "THREAD_OR_PROCESS_MIGRATION",
            "PACKET_LEVEL_CONTROL_PLANE",
            "DISTRIBUTED_CONSENSUS",
        ),
        model_note=(
            "This v1 contract defines deterministic product semantics and "
            "observability fields for future cache, offload, and migration "
            "features. It intentionally adds no runtime behavior."
        ),
    )


def cache_offload_migration_contract_v1_to_dict(
    contract: CacheOffloadMigrationContractV1 | None = None,
) -> dict[str, object]:
    """Return the default or supplied contract as JSON-compatible data."""

    selected = (
        default_cache_offload_migration_contract_v1()
        if contract is None
        else contract
    )
    if not isinstance(selected, CacheOffloadMigrationContractV1):
        raise TypeError("contract must be CacheOffloadMigrationContractV1 or None")
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
    "CACHE_OFFLOAD_MIGRATION_CONTRACT_V1_ID",
    "CacheOffloadMigrationContractV1",
    "ComputeServiceActionContract",
    "ComputeServiceActionKind",
    "ComputeServiceActionStatus",
    "cache_offload_migration_contract_v1_to_dict",
    "default_cache_offload_migration_contract_v1",
]
