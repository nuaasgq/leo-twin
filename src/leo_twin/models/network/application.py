"""Deterministic flow-level application protocol runtime."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from leo_twin.schema import ApplicationProtocol, FlowRequest


@dataclass(frozen=True)
class ApplicationProfile:
    """Configuration for one flow-level application protocol profile."""

    protocol: ApplicationProtocol
    demand_capacity_multiplier: float
    session_setup_latency_s: float = 0.0
    interaction_model: str = "request_response"

    def __post_init__(self) -> None:
        if not isinstance(self.protocol, ApplicationProtocol):
            object.__setattr__(self, "protocol", ApplicationProtocol(str(self.protocol)))
        _require_positive_number(
            self.demand_capacity_multiplier,
            "demand_capacity_multiplier",
        )
        _require_non_negative_number(
            self.session_setup_latency_s,
            "session_setup_latency_s",
        )
        if not isinstance(self.interaction_model, str) or not self.interaction_model:
            raise TypeError("interaction_model must be a non-empty str")


@dataclass(frozen=True)
class ApplicationDecision:
    """Deterministic application-layer decision for one flow request."""

    protocol: ApplicationProtocol
    flow_id: str
    effective_demand_capacity: float
    demand_capacity_multiplier: float
    session_setup_latency_s: float
    interaction_model: str


class ApplicationRuntime:
    """Apply an application protocol profile to flow route requests."""

    def __init__(self, profile: ApplicationProfile) -> None:
        self._profile = profile

    @property
    def profile(self) -> ApplicationProfile:
        return self._profile

    def decision(self, request: FlowRequest) -> ApplicationDecision:
        """Return the deterministic application-layer decision for a request."""

        return ApplicationDecision(
            protocol=self._profile.protocol,
            flow_id=request.flow_id,
            effective_demand_capacity=(
                request.demand_capacity * self._profile.demand_capacity_multiplier
            ),
            demand_capacity_multiplier=self._profile.demand_capacity_multiplier,
            session_setup_latency_s=self._profile.session_setup_latency_s,
            interaction_model=self._profile.interaction_model,
        )

    def apply(self, request: FlowRequest) -> FlowRequest:
        """Return a request whose capacity demand reflects the application profile."""

        decision = self.decision(request)
        return FlowRequest(
            flow_id=request.flow_id,
            source_id=request.source_id,
            target_id=request.target_id,
            demand_capacity=decision.effective_demand_capacity,
        )


def default_application_runtime(protocol: ApplicationProtocol) -> ApplicationRuntime:
    """Return a deterministic default application runtime."""

    if not isinstance(protocol, ApplicationProtocol):
        protocol = ApplicationProtocol(str(protocol))
    if protocol == ApplicationProtocol.HTTP:
        return ApplicationRuntime(
            ApplicationProfile(
                protocol=ApplicationProtocol.HTTP,
                demand_capacity_multiplier=1.15,
                session_setup_latency_s=0.02,
                interaction_model="request_response",
            )
        )
    if protocol == ApplicationProtocol.MQTT:
        return ApplicationRuntime(
            ApplicationProfile(
                protocol=ApplicationProtocol.MQTT,
                demand_capacity_multiplier=0.75,
                session_setup_latency_s=0.005,
                interaction_model="publish_subscribe",
            )
        )
    if protocol == ApplicationProtocol.TELEMETRY:
        return ApplicationRuntime(
            ApplicationProfile(
                protocol=ApplicationProtocol.TELEMETRY,
                demand_capacity_multiplier=0.5,
                session_setup_latency_s=0.0,
                interaction_model="periodic_push",
            )
        )
    return ApplicationRuntime(
        ApplicationProfile(
            protocol=ApplicationProtocol.TASK_OFFLOAD_FLOW,
            demand_capacity_multiplier=1.0,
            session_setup_latency_s=0.0,
            interaction_model="job_lifecycle",
        )
    )


def _require_positive_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(float(value)) or value <= 0.0:
        raise ValueError(f"{field_name} must be finite and positive")


def _require_non_negative_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(float(value)) or value < 0.0:
        raise ValueError(f"{field_name} must be finite and non-negative")
