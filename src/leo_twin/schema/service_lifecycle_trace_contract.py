"""Product-level service lifecycle trace contract v2."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


SERVICE_LIFECYCLE_TRACE_CONTRACT_V2_ID = (
    "leo_twin.service_lifecycle_trace_contract.v2"
)


class ServiceLifecycleStageKind(StrEnum):
    """Canonical communication-compute service lifecycle stages."""

    INPUT_NETWORK = "INPUT_NETWORK"
    COMPUTE_QUEUE = "COMPUTE_QUEUE"
    COMPUTE_EXECUTION = "COMPUTE_EXECUTION"
    OUTPUT_NETWORK = "OUTPUT_NETWORK"
    TERMINAL = "TERMINAL"


class ServiceLifecycleStageStatus(StrEnum):
    """Observation status for one lifecycle stage."""

    OBSERVED = "OBSERVED"
    PENDING = "PENDING"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


class ServiceLifecycleTerminalState(StrEnum):
    """Product-facing terminal state for one service trace."""

    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


@dataclass(frozen=True)
class ServiceLifecycleStageContract:
    """One stage declared by the service lifecycle trace contract."""

    stage: ServiceLifecycleStageKind
    source_fields: tuple[str, ...]
    output_fields: tuple[str, ...]
    semantics: str

    def __post_init__(self) -> None:
        if not isinstance(self.stage, ServiceLifecycleStageKind):
            object.__setattr__(
                self,
                "stage",
                ServiceLifecycleStageKind(str(self.stage)),
            )
        object.__setattr__(
            self,
            "source_fields",
            _normalize_str_tuple(self.source_fields, "source_fields"),
        )
        object.__setattr__(
            self,
            "output_fields",
            _normalize_str_tuple(self.output_fields, "output_fields"),
        )
        _require_non_empty_str(self.semantics, "semantics")

    def to_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage.value,
            "source_fields": self.source_fields,
            "output_fields": self.output_fields,
            "semantics": self.semantics,
        }


@dataclass(frozen=True)
class ServiceLifecycleTraceContractV2:
    """Contract for backend-owned service lifecycle trace rows."""

    contract_id: str
    source_summary: str
    trace_kind: str
    stage_contracts: tuple[ServiceLifecycleStageContract, ...]
    terminal_states: tuple[ServiceLifecycleTerminalState, ...]
    excluded_semantics: tuple[str, ...]
    model_note: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.contract_id, "contract_id")
        _require_non_empty_str(self.source_summary, "source_summary")
        _require_non_empty_str(self.trace_kind, "trace_kind")
        if not self.stage_contracts:
            raise ValueError("stage_contracts must not be empty")
        for item in self.stage_contracts:
            if not isinstance(item, ServiceLifecycleStageContract):
                raise TypeError(
                    "stage_contracts must contain ServiceLifecycleStageContract"
                )
        if not self.terminal_states:
            raise ValueError("terminal_states must not be empty")
        object.__setattr__(
            self,
            "terminal_states",
            tuple(
                item
                if isinstance(item, ServiceLifecycleTerminalState)
                else ServiceLifecycleTerminalState(str(item))
                for item in self.terminal_states
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
            "contract_id": self.contract_id,
            "source_summary": self.source_summary,
            "trace_kind": self.trace_kind,
            "stage_contracts": tuple(item.to_dict() for item in self.stage_contracts),
            "terminal_states": tuple(item.value for item in self.terminal_states),
            "excluded_semantics": self.excluded_semantics,
            "model_note": self.model_note,
        }


def default_service_lifecycle_trace_contract_v2() -> ServiceLifecycleTraceContractV2:
    """Return the deterministic product contract for service lifecycle traces."""

    return ServiceLifecycleTraceContractV2(
        contract_id=SERVICE_LIFECYCLE_TRACE_CONTRACT_V2_ID,
        source_summary="service_latency_history_v1",
        trace_kind="COMMUNICATION_COMPUTE_SERVICE_TRACE",
        stage_contracts=(
            ServiceLifecycleStageContract(
                stage=ServiceLifecycleStageKind.INPUT_NETWORK,
                source_fields=("input_flow_id", "input_route_id"),
                output_fields=("duration_s", "route_id", "flow_id"),
                semantics="Input data network transfer before compute execution.",
            ),
            ServiceLifecycleStageContract(
                stage=ServiceLifecycleStageKind.COMPUTE_QUEUE,
                source_fields=("compute_queue_delay_s",),
                output_fields=("duration_s", "compute_node_id"),
                semantics="Deterministic wait before a compute node starts the task.",
            ),
            ServiceLifecycleStageContract(
                stage=ServiceLifecycleStageKind.COMPUTE_EXECUTION,
                source_fields=("compute_execution_delay_s",),
                output_fields=("duration_s", "compute_node_id"),
                semantics="Deterministic compute execution delay on the selected node.",
            ),
            ServiceLifecycleStageContract(
                stage=ServiceLifecycleStageKind.OUTPUT_NETWORK,
                source_fields=("output_flow_id", "output_route_id"),
                output_fields=("duration_s", "route_id", "flow_id"),
                semantics="Output/result network transfer after compute finishes.",
            ),
            ServiceLifecycleStageContract(
                stage=ServiceLifecycleStageKind.TERMINAL,
                source_fields=("complete", "total_latency_s"),
                output_fields=("terminal_state", "terminal_state_reason"),
                semantics="Backend-owned terminal state for the service trace.",
            ),
        ),
        terminal_states=(
            ServiceLifecycleTerminalState.RUNNING,
            ServiceLifecycleTerminalState.COMPLETE,
            ServiceLifecycleTerminalState.INCOMPLETE,
        ),
        excluded_semantics=(
            "PACKET_LEVEL_TIMELINE",
            "STOCHASTIC_RETRY",
            "DEADLINE_AWARE_PREEMPTION",
            "EXTERNAL_NETWORK_SIMULATOR",
        ),
        model_note=(
            "Lifecycle traces are deterministic flow-level component observations "
            "derived from service_latency_history_v1."
        ),
    )


def service_lifecycle_trace_contract_v2_to_dict() -> dict[str, object]:
    """Return the JSON-ready service lifecycle trace contract."""

    return default_service_lifecycle_trace_contract_v2().to_dict()


def _normalize_str_tuple(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    normalized = tuple(str(value) for value in values)
    for item in normalized:
        _require_non_empty_str(item, field_name)
    return normalized


def _require_non_empty_str(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty string")
