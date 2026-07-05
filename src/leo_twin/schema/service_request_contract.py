"""Product-level service request contract v2."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


SERVICE_REQUEST_CONTRACT_V2_ID = "leo_twin.service_request_contract.v2"


class ServiceRequestClass(StrEnum):
    """User-facing service classes currently represented by traffic demand."""

    DATA_TRANSFER = "DATA_TRANSFER"
    TELEMETRY = "TELEMETRY"
    BULK_DOWNLINK = "BULK_DOWNLINK"
    COMPUTE_SERVICE = "COMPUTE_SERVICE"
    EMERGENCY = "EMERGENCY"


class ServiceRequestFieldStatus(StrEnum):
    """Whether a contract field has runtime behavior in the current product."""

    SUPPORTED = "SUPPORTED"
    RESERVED = "RESERVED"


class ServiceRequestGeneratedArtifactKind(StrEnum):
    """Runtime artifacts deterministically generated from one service request."""

    INPUT_FLOW = "INPUT_FLOW"
    COMPUTE_TASK = "COMPUTE_TASK"
    OUTPUT_FLOW_METADATA = "OUTPUT_FLOW_METADATA"


@dataclass(frozen=True)
class ServiceRequestFieldContract:
    """One field in the user-facing service request contract."""

    field: str
    value_type: str
    required: bool
    source: str
    runtime_mapping: tuple[str, ...]
    implementation_status: ServiceRequestFieldStatus
    semantics: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.field, "field")
        _require_non_empty_str(self.value_type, "value_type")
        if not isinstance(self.required, bool):
            raise TypeError("required must be a bool")
        _require_non_empty_str(self.source, "source")
        object.__setattr__(
            self,
            "runtime_mapping",
            _normalize_str_tuple(self.runtime_mapping, "runtime_mapping"),
        )
        if not isinstance(self.implementation_status, ServiceRequestFieldStatus):
            object.__setattr__(
                self,
                "implementation_status",
                ServiceRequestFieldStatus(str(self.implementation_status)),
            )
        _require_non_empty_str(self.semantics, "semantics")

    def to_dict(self) -> dict[str, object]:
        return {
            "field": self.field,
            "value_type": self.value_type,
            "required": self.required,
            "source": self.source,
            "runtime_mapping": self.runtime_mapping,
            "implementation_status": self.implementation_status.value,
            "semantics": self.semantics,
        }


@dataclass(frozen=True)
class ServiceRequestGeneratedArtifactContract:
    """One runtime artifact generated from a service request."""

    kind: ServiceRequestGeneratedArtifactKind
    generated_for_classes: tuple[ServiceRequestClass, ...]
    id_policy: str
    event_type: str
    consumer: str
    source_fields: tuple[str, ...]
    semantics: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ServiceRequestGeneratedArtifactKind):
            object.__setattr__(
                self,
                "kind",
                ServiceRequestGeneratedArtifactKind(str(self.kind)),
            )
        if not self.generated_for_classes:
            raise ValueError("generated_for_classes must not be empty")
        object.__setattr__(
            self,
            "generated_for_classes",
            tuple(
                item if isinstance(item, ServiceRequestClass) else ServiceRequestClass(str(item))
                for item in self.generated_for_classes
            ),
        )
        _require_non_empty_str(self.id_policy, "id_policy")
        _require_non_empty_str(self.event_type, "event_type")
        _require_non_empty_str(self.consumer, "consumer")
        object.__setattr__(
            self,
            "source_fields",
            _normalize_str_tuple(self.source_fields, "source_fields"),
        )
        _require_non_empty_str(self.semantics, "semantics")

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind.value,
            "generated_for_classes": tuple(item.value for item in self.generated_for_classes),
            "id_policy": self.id_policy,
            "event_type": self.event_type,
            "consumer": self.consumer,
            "source_fields": self.source_fields,
            "semantics": self.semantics,
        }


@dataclass(frozen=True)
class ServiceRequestContractV2:
    """Versioned product contract for user business service requests."""

    contract_id: str
    version: str
    request_model: str
    supported_classes: tuple[ServiceRequestClass, ...]
    fields: tuple[ServiceRequestFieldContract, ...]
    generated_artifacts: tuple[ServiceRequestGeneratedArtifactContract, ...]
    destination_policies: tuple[str, ...]
    default_retry_policy: str
    deterministic_identity_policy: str
    current_runtime_mapping: tuple[str, ...]
    excluded_semantics: tuple[str, ...]
    model_note: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.contract_id, "contract_id")
        _require_non_empty_str(self.version, "version")
        _require_non_empty_str(self.request_model, "request_model")
        if not self.supported_classes:
            raise ValueError("supported_classes must not be empty")
        object.__setattr__(
            self,
            "supported_classes",
            tuple(
                item if isinstance(item, ServiceRequestClass) else ServiceRequestClass(str(item))
                for item in self.supported_classes
            ),
        )
        if not self.fields:
            raise ValueError("fields must not be empty")
        for field in self.fields:
            if not isinstance(field, ServiceRequestFieldContract):
                raise TypeError("fields must contain ServiceRequestFieldContract values")
        if not self.generated_artifacts:
            raise ValueError("generated_artifacts must not be empty")
        for artifact in self.generated_artifacts:
            if not isinstance(artifact, ServiceRequestGeneratedArtifactContract):
                raise TypeError(
                    "generated_artifacts must contain "
                    "ServiceRequestGeneratedArtifactContract values"
                )
        object.__setattr__(
            self,
            "destination_policies",
            _normalize_str_tuple(self.destination_policies, "destination_policies"),
        )
        _require_non_empty_str(self.default_retry_policy, "default_retry_policy")
        _require_non_empty_str(
            self.deterministic_identity_policy,
            "deterministic_identity_policy",
        )
        object.__setattr__(
            self,
            "current_runtime_mapping",
            _normalize_str_tuple(self.current_runtime_mapping, "current_runtime_mapping"),
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
            "request_model": self.request_model,
            "supported_classes": tuple(item.value for item in self.supported_classes),
            "fields": tuple(field.to_dict() for field in self.fields),
            "generated_artifacts": tuple(
                artifact.to_dict() for artifact in self.generated_artifacts
            ),
            "destination_policies": self.destination_policies,
            "default_retry_policy": self.default_retry_policy,
            "deterministic_identity_policy": self.deterministic_identity_policy,
            "current_runtime_mapping": self.current_runtime_mapping,
            "excluded_semantics": self.excluded_semantics,
            "model_note": self.model_note,
        }


def default_service_request_contract_v2() -> ServiceRequestContractV2:
    """Build the default SEES service request contract v2."""

    all_classes = (
        ServiceRequestClass.DATA_TRANSFER,
        ServiceRequestClass.TELEMETRY,
        ServiceRequestClass.BULK_DOWNLINK,
        ServiceRequestClass.COMPUTE_SERVICE,
        ServiceRequestClass.EMERGENCY,
    )
    return ServiceRequestContractV2(
        contract_id=SERVICE_REQUEST_CONTRACT_V2_ID,
        version="v2",
        request_model="FLOW_LEVEL_USER_SERVICE_REQUEST",
        supported_classes=all_classes,
        fields=(
            ServiceRequestFieldContract(
                field="service_id",
                value_type="string",
                required=True,
                source="GENERATED_IDENTITY",
                runtime_mapping=(
                    "TrafficDemandProfile.id_prefix",
                    "profile_index",
                    "TrafficClass",
                    "request_index",
                ),
                implementation_status=ServiceRequestFieldStatus.SUPPORTED,
                semantics=(
                    "Stable business request identity used as the base for "
                    "generated flow, task, and output-flow ids."
                ),
            ),
            ServiceRequestFieldContract(
                field="user_id",
                value_type="string",
                required=True,
                source="TrafficDemandProfile.source_ids",
                runtime_mapping=("FlowRequest.source_id", "TaskRequest.source_id"),
                implementation_status=ServiceRequestFieldStatus.SUPPORTED,
                semantics="Ground user or source node that originates the service request.",
            ),
            ServiceRequestFieldContract(
                field="service_class",
                value_type="enum",
                required=True,
                source="TrafficDemandProfile.traffic_class",
                runtime_mapping=(
                    "TrafficDemandRecord.traffic_class",
                    "FlowRequest.application_id",
                ),
                implementation_status=ServiceRequestFieldStatus.SUPPORTED,
                semantics="Business class that chooses flow-only or compute-service shape.",
            ),
            ServiceRequestFieldContract(
                field="priority",
                value_type="integer",
                required=True,
                source="TrafficDemandProfile.priority",
                runtime_mapping=("FlowRequest.priority", "TaskRequest.priority"),
                implementation_status=ServiceRequestFieldStatus.SUPPORTED,
                semantics="Deterministic event priority and runtime request priority.",
            ),
            ServiceRequestFieldContract(
                field="destination_policy",
                value_type="enum",
                required=True,
                source="TrafficDemandProfile.destination_type",
                runtime_mapping=(
                    "TrafficDestinationType",
                    "traffic_demand_summary.destination_selection_policy",
                ),
                implementation_status=ServiceRequestFieldStatus.SUPPORTED,
                semantics="Backend-owned policy for selecting service destination ids.",
            ),
            ServiceRequestFieldContract(
                field="destination_id",
                value_type="string",
                required=True,
                source="TrafficDemandProfile.destination_ids",
                runtime_mapping=("FlowRequest.target_id",),
                implementation_status=ServiceRequestFieldStatus.SUPPORTED,
                semantics="Selected network or compute destination for the input flow.",
            ),
            ServiceRequestFieldContract(
                field="input_data_mb",
                value_type="number",
                required=True,
                source="TrafficDemandProfile.input_data_size",
                runtime_mapping=(
                    "FlowRequest.demand_capacity",
                    "TaskRequest.data_size",
                    "TaskRequest.input_data_mb",
                ),
                implementation_status=ServiceRequestFieldStatus.SUPPORTED,
                semantics=(
                    "Flow-level input size proxy used for route demand and "
                    "compute-service input transfer accounting."
                ),
            ),
            ServiceRequestFieldContract(
                field="output_data_mb",
                value_type="number",
                required=False,
                source="TrafficDemandProfile.output_data_size",
                runtime_mapping=(
                    "ComputeOutputFlowMetadata.data_size",
                    "TaskRequest.output_data_mb",
                ),
                implementation_status=ServiceRequestFieldStatus.SUPPORTED,
                semantics="Deferred result data size for compute-service output flow metadata.",
            ),
            ServiceRequestFieldContract(
                field="duration_s",
                value_type="number|null",
                required=False,
                source="ServiceRequestContractV2",
                runtime_mapping=("RESERVED_FOR_V2_ARRIVAL_PROFILES",),
                implementation_status=ServiceRequestFieldStatus.RESERVED,
                semantics=(
                    "Reserved service-intent duration. Current flow-level runtime "
                    "does not hold a request open by duration."
                ),
            ),
            ServiceRequestFieldContract(
                field="deadline_s",
                value_type="number|null",
                required=False,
                source="ServiceRequestContractV2",
                runtime_mapping=("TaskRequest.deadline",),
                implementation_status=ServiceRequestFieldStatus.RESERVED,
                semantics=(
                    "Reserved deadline intent. TaskRequest can carry a deadline, "
                    "but traffic profiles do not yet schedule deadline-aware behavior."
                ),
            ),
            ServiceRequestFieldContract(
                field="retry_policy",
                value_type="enum",
                required=False,
                source="ServiceRequestContractV2.default_retry_policy",
                runtime_mapping=("NO_RETRY",),
                implementation_status=ServiceRequestFieldStatus.RESERVED,
                semantics="Reserved retry intent; current service requests do not resubmit failures.",
            ),
        ),
        generated_artifacts=(
            ServiceRequestGeneratedArtifactContract(
                kind=ServiceRequestGeneratedArtifactKind.INPUT_FLOW,
                generated_for_classes=all_classes,
                id_policy=(
                    "flow-only classes use service_id; COMPUTE_SERVICE uses "
                    "service_id + '-input'."
                ),
                event_type="FLOW_ARRIVAL",
                consumer="Network",
                source_fields=("service_id", "user_id", "destination_id", "input_data_mb"),
                semantics="Input network flow that begins the service request lifecycle.",
            ),
            ServiceRequestGeneratedArtifactContract(
                kind=ServiceRequestGeneratedArtifactKind.COMPUTE_TASK,
                generated_for_classes=(ServiceRequestClass.COMPUTE_SERVICE,),
                id_policy="service_id + '-task'",
                event_type="TASK_ARRIVAL",
                consumer="Compute",
                source_fields=("service_id", "user_id", "input_data_mb", "priority"),
                semantics=(
                    "Compute task correlated with the input flow; task.flow_id "
                    "points back to the input flow id."
                ),
            ),
            ServiceRequestGeneratedArtifactContract(
                kind=ServiceRequestGeneratedArtifactKind.OUTPUT_FLOW_METADATA,
                generated_for_classes=(ServiceRequestClass.COMPUTE_SERVICE,),
                id_policy="service_id + '-output'",
                event_type="DEFERRED_OUTPUT_FLOW_METADATA",
                consumer="Communication-compute lifecycle",
                source_fields=("service_id", "output_data_mb", "priority"),
                semantics=(
                    "Deterministic metadata for a result flow emitted after "
                    "compute-service execution completes."
                ),
            ),
        ),
        destination_policies=(
            "ROUND_ROBIN_GROUND_ENDPOINTS",
            "ROUND_ROBIN_SATELLITES",
            "ROUND_ROBIN_COMPUTE_NODES",
            "ROUND_ROBIN_SERVICE_ENDPOINTS",
        ),
        default_retry_policy="NO_RETRY",
        deterministic_identity_policy=(
            "service_id = id_prefix + profile_index + traffic_class + request_index; "
            "all generated ids derive from that base id."
        ),
        current_runtime_mapping=(
            "TrafficDemandProfile expands into TrafficDemandRecord",
            "TrafficDemandRecord.input_flow schedules FLOW_ARRIVAL",
            "TrafficDemandRecord.task schedules TASK_ARRIVAL for COMPUTE_SERVICE",
            "TrafficDemandRecord.output_flow stores deferred result-flow metadata",
        ),
        excluded_semantics=(
            "PACKET_LEVEL_TRAFFIC",
            "STOCHASTIC_RETRY",
            "DEADLINE_AWARE_SCHEDULING",
            "DURATION_HOLDING_BEHAVIOR",
            "APPLICATION_PAYLOAD_CONTENT",
            "EXTERNAL_SIMULATOR_INTEGRATION",
        ),
        model_note=(
            "Service requests are product-level business intents that compile "
            "into deterministic flow-level and task-level runtime requests. "
            "They do not model packets, RF payload content, or external simulators."
        ),
    )


def service_request_contract_v2_to_dict(
    contract: ServiceRequestContractV2 | None = None,
) -> dict[str, object]:
    """Return the default or supplied service request contract as data."""

    selected = default_service_request_contract_v2() if contract is None else contract
    if not isinstance(selected, ServiceRequestContractV2):
        raise TypeError("contract must be ServiceRequestContractV2 or None")
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
    "SERVICE_REQUEST_CONTRACT_V2_ID",
    "ServiceRequestClass",
    "ServiceRequestContractV2",
    "ServiceRequestFieldContract",
    "ServiceRequestFieldStatus",
    "ServiceRequestGeneratedArtifactContract",
    "ServiceRequestGeneratedArtifactKind",
    "default_service_request_contract_v2",
    "service_request_contract_v2_to_dict",
]
