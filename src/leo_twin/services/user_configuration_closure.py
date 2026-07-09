"""Backend-owned user configuration closure summary v2."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from leo_twin.schema.config import SEESConfig, config_to_dict
from leo_twin.services.configuration_schema import (
    USER_CONFIGURATION_SCHEMA_V2_ID,
    build_user_configuration_control_surface_evidence_v1,
    build_user_configuration_schema_v2,
    validate_user_configuration_mapping_v2,
)
from leo_twin.services.configuration_view import (
    build_user_configuration_template_validation_evidence,
    build_user_configuration_view,
)
from leo_twin.services.runtime_reproducibility import stable_hash_payload


USER_CONFIGURATION_CLOSURE_V2_ID = "sees.user_configuration_closure.v2"

UserConfigurationClosureV2 = dict[str, object]


def build_user_configuration_closure_v2(
    config: SEESConfig,
    *,
    generated_config: Mapping[str, Any] | None = None,
    configuration_surface_summary: Mapping[str, Any] | None = None,
    control_surface_evidence: Mapping[str, Any] | None = None,
    template_validation: Mapping[str, Any] | None = None,
) -> UserConfigurationClosureV2:
    """Build a compact readiness summary for the full user config system."""

    if not isinstance(config, SEESConfig):
        raise TypeError("config must be SEESConfig")

    effective_config = config_to_dict(config)
    schema = build_user_configuration_schema_v2(config)
    validation = validate_user_configuration_mapping_v2(effective_config)
    surface = (
        build_user_configuration_view(config)
        if configuration_surface_summary is None
        else dict(configuration_surface_summary)
    )
    control = (
        build_user_configuration_control_surface_evidence_v1(config)
        if control_surface_evidence is None
        else dict(control_surface_evidence)
    )
    templates = (
        build_user_configuration_template_validation_evidence()
        if template_validation is None
        else dict(template_validation)
    )
    generated = dict(generated_config) if isinstance(generated_config, Mapping) else {}
    gates = (
        _gate(
            "schema_contract",
            schema.get("schema_id") == USER_CONFIGURATION_SCHEMA_V2_ID
            and _int(schema.get("field_count")) > 0,
            "User configuration schema v2 is available and non-empty.",
            {
                "schema_id": str(schema.get("schema_id", "")),
                "field_count": _int(schema.get("field_count")),
            },
        ),
        _gate(
            "effective_config_validation",
            validation.get("ok") is True,
            "Current SEESConfig validates through the same user config loader.",
            {
                "error_count": _int(validation.get("error_count")),
                "normalized_config_hash": str(
                    validation.get("normalized_config_hash", "")
                ),
            },
        ),
        _gate(
            "control_surface_coverage",
            control.get("coverage_status") == "COMPLETE",
            "Control panel key fields are covered by the backend schema.",
            {
                "coverage_status": str(control.get("coverage_status", "")),
                "key_field_count": _int(control.get("key_field_count")),
                "covered_key_field_count": _int(
                    control.get("covered_key_field_count")
                ),
            },
        ),
        _gate(
            "template_validation",
            templates.get("all_templates_valid") is True,
            "Approved executable templates validate with the backend loader.",
            {
                "template_count": _int(templates.get("template_count")),
                "valid_template_count": _int(templates.get("valid_template_count")),
                "invalid_template_count": _int(
                    templates.get("invalid_template_count")
                ),
            },
        ),
        _gate(
            "frontend_key_file_split",
            _int(surface.get("key_field_count")) > 0
            and _int(surface.get("detailed_field_count")) >= _int(
                surface.get("key_field_count")
            )
            and str(surface.get("frontend_policy", ""))
            == "CONTROL_PANEL_KEY_FIELDS_ONLY",
            "Backend declares key frontend fields and detailed file-only fields.",
            {
                "frontend_policy": str(surface.get("frontend_policy", "")),
                "key_field_count": _int(surface.get("key_field_count")),
                "detailed_field_count": _int(surface.get("detailed_field_count")),
                "file_only_field_count": len(_values(surface.get("file_only_fields"))),
            },
        ),
        _gate(
            "generated_config_binding",
            _generated_config_binding_ok(generated),
            "Generated scenario config carries backend configuration semantics.",
            _generated_config_binding_detail(generated),
        ),
    )
    failed_gates = tuple(gate for gate in gates if gate["status"] != "PASS")
    closure_status = "READY" if not failed_gates else "INCOMPLETE"
    payload: dict[str, object] = {
        "version": "v2",
        "summary_id": USER_CONFIGURATION_CLOSURE_V2_ID,
        "source": (
            "user_configuration_schema_v2 + configuration_surface_summary + "
            "generated_config"
        ),
        "schema_id": USER_CONFIGURATION_SCHEMA_V2_ID,
        "closure_scope": "FULL_CONFIG_FILE_AND_KEY_FRONTEND_CONTROL_SURFACE",
        "closure_status": closure_status,
        "configuration_ready": closure_status == "READY",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        "unknown_key_policy": str(schema.get("unknown_key_policy", "")),
        "defaulting_policy": str(schema.get("defaulting_policy", "")),
        "frontend_policy": str(surface.get("frontend_policy", "")),
        "schema_field_count": _int(schema.get("field_count")),
        "key_field_count": _int(surface.get("key_field_count")),
        "detailed_field_count": _int(surface.get("detailed_field_count")),
        "file_only_field_count": len(_values(surface.get("file_only_fields"))),
        "template_count": _int(templates.get("template_count")),
        "valid_template_count": _int(templates.get("valid_template_count")),
        "invalid_template_count": _int(templates.get("invalid_template_count")),
        "gate_count": len(gates),
        "passed_gate_count": len(gates) - len(failed_gates),
        "failed_gate_count": len(failed_gates),
        "gates": gates,
        "effective_config_hash": stable_hash_payload(effective_config),
        "generated_config_hash": (
            stable_hash_payload(generated) if generated else ""
        ),
        "operator_next_action": _operator_next_action(closure_status, failed_gates),
        "model_boundaries": {
            "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
            "packet_level_simulation": False,
            "external_simulators": False,
            "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
            "frontend_semantics_source": "BACKEND_USER_CONFIGURATION",
        },
        "model_assumptions": (
            "The control panel exposes key fields; full YAML/JSON config carries advanced fields.",
            "All accepted configuration mappings are validated through the backend config loader.",
            "Generated runtime config is evidence, not a source file to commit by default.",
        ),
    }
    payload["closure_hash"] = stable_hash_payload(payload)
    return payload


def _gate(
    gate_id: str,
    passed: bool,
    expectation: str,
    detail: Mapping[str, Any],
) -> dict[str, object]:
    row: dict[str, object] = {
        "gate_id": gate_id,
        "status": "PASS" if passed else "FAIL",
        "expectation": expectation,
        "detail": dict(detail),
    }
    row["gate_hash"] = stable_hash_payload(row)
    return row


def _generated_config_binding_ok(generated: Mapping[str, Any]) -> bool:
    backend_summary = _mapping(generated.get("backend_summary"))
    if not backend_summary:
        return False
    surface = _mapping(backend_summary.get("configuration_surface_summary"))
    fidelity = _mapping(backend_summary.get("fidelity_summary"))
    return (
        surface.get("schema_id") == USER_CONFIGURATION_SCHEMA_V2_ID
        and str(surface.get("frontend_policy", "")) == "CONTROL_PANEL_KEY_FIELDS_ONLY"
        and bool(fidelity)
    )


def _generated_config_binding_detail(
    generated: Mapping[str, Any],
) -> dict[str, object]:
    backend_summary = _mapping(generated.get("backend_summary"))
    surface = _mapping(backend_summary.get("configuration_surface_summary"))
    fidelity = _mapping(backend_summary.get("fidelity_summary"))
    return {
        "generated_config_present": bool(generated),
        "backend_summary_present": bool(backend_summary),
        "configuration_surface_summary_present": bool(surface),
        "configuration_surface_schema_id": str(surface.get("schema_id", "")),
        "fidelity_summary_present": bool(fidelity),
    }


def _operator_next_action(
    closure_status: str,
    failed_gates: Sequence[Mapping[str, object]],
) -> str:
    if closure_status == "READY":
        return "USE_KEY_CONTROLS_OR_EDIT_DETAILED_CONFIG"
    failed_ids = {str(gate.get("gate_id", "")) for gate in failed_gates}
    if "effective_config_validation" in failed_ids:
        return "FIX_CURRENT_CONFIG_AND_REVALIDATE"
    if "template_validation" in failed_ids:
        return "FIX_APPROVED_CONFIGURATION_TEMPLATES"
    if "generated_config_binding" in failed_ids:
        return "REGENERATE_RUNTIME_CONFIG_BINDING"
    return "CHECK_CONFIGURATION_CONTRACT_EVIDENCE"


def _values(value: object) -> tuple[object, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(value)


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return max(0, int(value))


__all__ = [
    "USER_CONFIGURATION_CLOSURE_V2_ID",
    "UserConfigurationClosureV2",
    "build_user_configuration_closure_v2",
]
