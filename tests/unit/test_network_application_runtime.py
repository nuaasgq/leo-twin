from __future__ import annotations

import pytest

from leo_twin.models.network import (
    ApplicationProfile,
    default_application_runtime,
)
from leo_twin.schema import ApplicationProtocol, FlowRequest


def _request(demand_capacity: float = 20.0) -> FlowRequest:
    return FlowRequest(
        flow_id="flow-001",
        source_id="user-001",
        target_id="compute-001",
        demand_capacity=demand_capacity,
    )


def test_default_application_profiles_transform_flow_demand_deterministically() -> None:
    task = default_application_runtime(ApplicationProtocol.TASK_OFFLOAD_FLOW).apply(
        _request()
    )
    http = default_application_runtime(ApplicationProtocol.HTTP).apply(_request())
    mqtt = default_application_runtime(ApplicationProtocol.MQTT).apply(_request())
    telemetry = default_application_runtime(ApplicationProtocol.TELEMETRY).apply(
        _request()
    )

    assert task.demand_capacity == 20.0
    assert http.demand_capacity == pytest.approx(23.0)
    assert mqtt.demand_capacity == pytest.approx(15.0)
    assert telemetry.demand_capacity == pytest.approx(10.0)
    assert mqtt == default_application_runtime(ApplicationProtocol.MQTT).apply(
        _request()
    )


def test_application_runtime_exposes_traceable_decision_fields() -> None:
    runtime = default_application_runtime(ApplicationProtocol.MQTT)

    decision = runtime.decision(_request())

    assert decision.protocol == ApplicationProtocol.MQTT
    assert decision.effective_demand_capacity == pytest.approx(15.0)
    assert decision.demand_capacity_multiplier == 0.75
    assert decision.session_setup_latency_s == 0.005
    assert decision.interaction_model == "publish_subscribe"


def test_application_profile_rejects_invalid_parameters() -> None:
    with pytest.raises(ValueError, match="demand_capacity_multiplier"):
        ApplicationProfile(
            protocol=ApplicationProtocol.HTTP,
            demand_capacity_multiplier=0.0,
        )

    with pytest.raises(ValueError, match="session_setup_latency_s"):
        ApplicationProfile(
            protocol=ApplicationProtocol.HTTP,
            demand_capacity_multiplier=1.0,
            session_setup_latency_s=-1.0,
        )
