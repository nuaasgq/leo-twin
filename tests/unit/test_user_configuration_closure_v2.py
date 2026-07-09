from __future__ import annotations

from leo_twin.schema.config import SEESConfig
from leo_twin.services.configuration_schema import (
    build_user_configuration_control_surface_evidence_v1,
)
from leo_twin.services.configuration_view import build_user_configuration_view
from leo_twin.services.user_configuration_closure import (
    USER_CONFIGURATION_CLOSURE_V2_ID,
    build_user_configuration_closure_v2,
)


def test_user_configuration_closure_v2_reports_ready_backend_contract() -> None:
    config = SEESConfig()
    surface = build_user_configuration_view(config)
    control = build_user_configuration_control_surface_evidence_v1(config)
    generated = {
        "satellite_count": config.scenario.satellite_count,
        "backend_summary": {
            "configuration_surface_summary": surface,
            "fidelity_summary": {
                "satellite_count": config.scenario.satellite_count,
                "orbit_update_mode": "PER_SATELLITE",
            },
        },
    }

    first = build_user_configuration_closure_v2(
        config,
        generated_config=generated,
        configuration_surface_summary=surface,
        control_surface_evidence=control,
        template_validation=surface["template_validation"],
    )
    second = build_user_configuration_closure_v2(
        config,
        generated_config=generated,
        configuration_surface_summary=surface,
        control_surface_evidence=control,
        template_validation=surface["template_validation"],
    )

    assert first == second
    assert first["version"] == "v2"
    assert first["summary_id"] == USER_CONFIGURATION_CLOSURE_V2_ID
    assert first["schema_id"] == "sees.user_configuration.v2"
    assert first["closure_status"] == "READY"
    assert first["configuration_ready"] is True
    assert first["frontend_inference_required"] is False
    assert first["packet_level_simulation"] is False
    assert first["gate_count"] == 6
    assert first["passed_gate_count"] == 6
    assert first["failed_gate_count"] == 0
    assert {gate["gate_id"] for gate in first["gates"]} == {
        "schema_contract",
        "effective_config_validation",
        "control_surface_coverage",
        "template_validation",
        "frontend_key_file_split",
        "generated_config_binding",
    }
    assert first["operator_next_action"] == (
        "USE_KEY_CONTROLS_OR_EDIT_DETAILED_CONFIG"
    )
    assert first["closure_hash"].startswith("sha256:")


def test_user_configuration_closure_v2_reports_missing_generated_binding() -> None:
    config = SEESConfig()

    summary = build_user_configuration_closure_v2(config, generated_config={})

    assert summary["closure_status"] == "INCOMPLETE"
    assert summary["configuration_ready"] is False
    assert summary["failed_gate_count"] == 1
    failed = tuple(gate for gate in summary["gates"] if gate["status"] == "FAIL")
    assert failed[0]["gate_id"] == "generated_config_binding"
    assert failed[0]["detail"]["generated_config_present"] is False
    assert summary["operator_next_action"] == "REGENERATE_RUNTIME_CONFIG_BINDING"


def test_user_configuration_closure_v2_reports_control_surface_drift() -> None:
    config = SEESConfig()
    surface = build_user_configuration_view(config)
    control = {
        **build_user_configuration_control_surface_evidence_v1(config),
        "coverage_status": "DRIFT_DETECTED",
    }
    generated = {
        "backend_summary": {
            "configuration_surface_summary": surface,
            "fidelity_summary": {"satellite_count": config.scenario.satellite_count},
        },
    }

    summary = build_user_configuration_closure_v2(
        config,
        generated_config=generated,
        configuration_surface_summary=surface,
        control_surface_evidence=control,
        template_validation=surface["template_validation"],
    )

    failed = tuple(gate for gate in summary["gates"] if gate["status"] == "FAIL")
    assert summary["closure_status"] == "INCOMPLETE"
    assert failed[0]["gate_id"] == "control_surface_coverage"
    assert summary["operator_next_action"] == (
        "CHECK_CONFIGURATION_CONTRACT_EVIDENCE"
    )
