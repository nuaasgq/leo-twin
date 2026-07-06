"""Control-plane integration for the full-system demo backend."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from leo_twin.runtime import (
    ControlCommand,
    RuntimeCommand,
    RuntimeKernelSpec,
    RuntimeLifecycleState,
    SessionAdvanceLoop,
    SimulationController,
    SimulationSession,
    StreamBackpressurePolicy,
    StreamBuffer,
    parse_control_command,
)
from leo_twin.schema.config_loader import (
    ConfigValidationError,
    config_from_mapping,
    parse_simple_yaml,
    write_config,
)
from leo_twin.models.orbit import KeplerianOrbitEngine
from leo_twin.schema import SatelliteState
from leo_twin.schema.config import SEESConfig, config_to_dict
from leo_twin.services.configuration_schema import (
    USER_CONFIGURATION_SCHEMA_V2_ID,
    build_user_configuration_schema_v2,
    validate_user_configuration_mapping_v2,
)
from leo_twin.services.configuration_view import (
    build_user_configuration_view,
    configuration_template_profiles,
    load_user_configuration_template,
)
from leo_twin.services.detail_pagination_contract import DETAIL_ENDPOINT_MAX_LIMIT
from leo_twin.services.network_kpi_provenance import (
    build_network_kpi_credibility_v1,
    build_network_kpi_provenance_v2,
)
from leo_twin.services.control import (
    RuntimeController,
    ScaleSafetyChecker,
)
from leo_twin.services.runtime_observability import (
    build_runtime_compute_node_detail_item,
    build_runtime_compute_node_detail_page,
    build_runtime_lifecycle_summaries,
    build_runtime_node_detail_page,
    build_runtime_route_detail_item,
    build_runtime_route_explanation_summary,
    build_runtime_route_provenance_trust_summary,
    build_runtime_satellite_detail_card,
    build_runtime_satellite_service_summary,
    build_runtime_service_detail_item,
    build_runtime_service_detail_page,
    build_runtime_service_lifecycle_trace_v2,
    build_runtime_service_trace_detail_item,
    build_runtime_user_detail_card,
    build_runtime_user_request_summary,
)
from leo_twin.services.runtime_reproducibility import (
    build_runtime_reproducibility_manifest,
    stable_hash_payload,
    stable_json_payload,
)
from leo_twin.services.result_package_contract import (
    build_runtime_export_diagnostics_bundle_v1,
    build_runtime_export_package_audit_index_v1,
    build_runtime_export_package_handoff_report_v1,
    build_runtime_export_reproducibility_boundary_v1,
    build_runtime_export_route_comparison_review_report_v1,
    build_runtime_export_route_detail_item_v1,
    build_runtime_export_route_detail_index_v1,
    build_runtime_export_route_detail_page_v1,
    build_runtime_export_review_summary_v1,
    build_runtime_export_scenario_review_bundle_v1,
    build_runtime_export_scenario_review_checklist_v1,
    build_runtime_export_service_trace_page_v1,
)
from leo_twin.services.scenario_builder import (
    scenario_builder_backend_summary,
    scenario_builder_config_from_sees_config,
    scenario_builder_config_to_mapping,
    write_full_system_scenario_builder_config,
)
from leo_twin.services.scale_fidelity import (
    ScaleFidelityConfig,
    build_scale_fidelity_summary,
)
from leo_twin.services.build_info import build_version_info_v1

from examples.integration_demo.config import (
    DemoConfig,
    demo_config_from_sees_config,
    demo_config_to_sees_config,
)
from examples.integration_demo.replay import DemoStateProjector
from examples.integration_demo.runtime import (
    DemoRunResult,
    DemoRuntimeContext,
    build_integration_demo_runtime,
    finalize_integration_demo_run,
    run_integration_demo,
)
from examples.integration_demo.serialization import JsonValue, event_to_json, stable_json_pretty


_FRONTEND_EVENT_TYPES = frozenset(
    {
        "ORBIT_UPDATE",
        "LINK_UPDATE",
        "ACCESS_START",
        "ACCESS_END",
        "ROUTE_UPDATE",
        "TASK_START",
        "TASK_FINISH",
        "COMPUTE_NODE_UPDATE",
        "METRIC_SAMPLE",
    }
)
_RUNTIME_EXPORT_CATALOG_FILENAME = "runtime_export_catalog_v1.json"
_RUNTIME_EXPORT_RESTORE_COMMAND = "RESTORE_EXPORT_PACKAGE"
_SERVICE_LIFECYCLE_TRACE_EXPORT_FILENAME = "service_lifecycle_trace_v2.json"
_RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_FILENAME = "route_detail_index_v1.json"
_RUNTIME_EXPORT_ROUTE_DETAIL_LIMIT = DETAIL_ENDPOINT_MAX_LIMIT
_RUNTIME_EXPORT_SERVICE_TRACE_LIMIT = DETAIL_ENDPOINT_MAX_LIMIT
_RUNTIME_EXPORT_REVIEW_SUMMARY_FILENAME = "review_summary_v1.json"
_RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_FILENAME = "diagnostics_bundle_v1.json"
_RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_FILENAME = "scenario_review_bundle_v1.json"
_RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_FILENAME = "scenario_review_checklist_v1.json"
_RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_FILENAME = (
    "route_comparison_review_report_v1.json"
)
_RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_FILENAME = "export_package_audit_index_v1.json"
_RUNTIME_EXPORT_PACKAGE_HANDOFF_REPORT_FILENAME = "package_handoff_report_v1.md"


class RuntimeExportArtifactError(LookupError):
    """Raised when a persisted runtime export artifact cannot be served safely."""


@dataclass
class DemoControlPlane:
    """Own the mutable control-plane state for a demo server instance."""

    _base_config: DemoConfig
    _result: DemoRunResult
    _controller: RuntimeController
    _config_output_path: Path
    _generated_config_output_path: Path
    _session: SimulationSession | None = None
    _runtime_adapter: SimulationController | None = None
    _runtime_context: DemoRuntimeContext | None = None
    _advance_loop: SessionAdvanceLoop | None = None
    _initialized: bool = False
    _user_request_history: dict[str, list[dict[str, object]]] = field(
        default_factory=dict
    )
    _user_request_history_limit: int = 32
    _export_history: list[dict[str, Any]] = field(default_factory=list)
    _export_history_limit: int = 8
    _export_sequence: int = 0

    @classmethod
    def from_result(
        cls,
        result: DemoRunResult,
        config_output_path: str | Path = "configs/sees_control.yaml",
        generated_config_output_path: str | Path = "configs/generated_full_system_demo.json",
    ) -> "DemoControlPlane":
        controller = RuntimeController(
            demo_config_to_sees_config(result.config),
            scale_safety_checker=ScaleSafetyChecker(),
        )
        control_plane = cls(
            _base_config=result.config,
            _result=result,
            _controller=controller,
            _config_output_path=Path(config_output_path),
            _generated_config_output_path=Path(generated_config_output_path),
        )
        control_plane._install_runtime_session(result.config)
        return control_plane

    @property
    def result(self) -> DemoRunResult:
        return self._result

    @property
    def controller(self) -> RuntimeController:
        return self._controller

    def runtime_status(self) -> dict[str, Any]:
        generated_config = self._generated_config_json()
        return {
            "type": "RUNTIME_STATUS",
            "status": self._status_json(generated_config),
            "config": self._controller.config_json(),
            "generated_config": generated_config,
        }

    def user_configuration_schema(self) -> dict[str, Any]:
        return {
            "type": "USER_CONFIGURATION_SCHEMA_V2",
            "summary": build_user_configuration_schema_v2(self._controller.config),
        }

    def user_configuration_templates(self) -> dict[str, Any]:
        templates = configuration_template_profiles()
        return {
            "type": "USER_CONFIGURATION_TEMPLATE_CATALOG",
            "summary": {
                "version": "v1",
                "source": "BACKEND_USER_CONFIGURATION",
                "schema_id": USER_CONFIGURATION_SCHEMA_V2_ID,
                "catalog_scope": "APPROVED_EXECUTABLE_TEMPLATES",
                "mutation_policy": "READ_ONLY_CATALOG",
                "template_count": len(templates),
                "templates": templates,
                "load_command": {
                    "type": "RUNTIME_CONTROL",
                    "action": "LOAD_TEMPLATE",
                    "payload_key": "template_id",
                    "requires_uninitialized_runtime": True,
                },
            },
        }

    def user_configuration_export(self) -> dict[str, Any]:
        config = self._controller.config_json()
        validation = validate_user_configuration_mapping_v2(config)
        return {
            "type": "USER_CONFIGURATION_EXPORT",
            "summary": {
                "version": "v1",
                "source": "BACKEND_USER_CONFIGURATION",
                "schema_id": USER_CONFIGURATION_SCHEMA_V2_ID,
                "export_scope": "CURRENT_EFFECTIVE_SEES_CONFIG",
                "format": "JSON_MAPPING",
                "yaml_config_file": str(self._config_output_path),
                "generated_config_file": str(self._generated_config_output_path),
                "unknown_key_policy": "REJECT",
                "defaulting_policy": "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
                "import_paths": (
                    "CONFIG_UPDATE control message for partial updates",
                    "LOAD_TEMPLATE control message for approved templates",
                    "RESTORE_EXPORT_PACKAGE control message for exported runtime packages",
                ),
                "config_hash": stable_hash_payload(config),
                "validation_ok": bool(validation["ok"]),
                "validation_error_count": int(validation["error_count"]),
                "validation_errors": tuple(validation["errors"]),
                "config": config,
            },
        }

    def user_configuration_validate(self, raw_config: Any) -> dict[str, Any]:
        validation = validate_user_configuration_mapping_v2(raw_config)
        return self._user_configuration_validation_response(
            validation,
            validation_scope="USER_PROVIDED_CONFIG_MAPPING",
            format_label="JSON_MAPPING",
        )

    def user_configuration_validate_text(
        self,
        text: str,
        *,
        format_hint: str = "auto",
    ) -> dict[str, Any]:
        try:
            raw_config, detected_format = _parse_user_configuration_text(
                text,
                format_hint=format_hint,
            )
        except ValueError as exc:
            return self._user_configuration_validation_response(
                {
                    "ok": False,
                    "error_count": 1,
                    "errors": (
                        {
                            "source": "config_text_parser",
                            "message": str(exc),
                        },
                    ),
                    "normalized_config": None,
                },
                validation_scope="USER_PROVIDED_CONFIG_TEXT",
                format_label="YAML_OR_JSON_TEXT",
                text_parse={
                    "version": "v1",
                    "source": "BACKEND_USER_CONFIGURATION",
                    "requested_format": format_hint,
                    "detected_format": None,
                    "ok": False,
                },
            )
        validation = validate_user_configuration_mapping_v2(raw_config)
        return self._user_configuration_validation_response(
            validation,
            validation_scope="USER_PROVIDED_CONFIG_TEXT",
            format_label=f"{detected_format.upper()}_TEXT",
            text_parse={
                "version": "v1",
                "source": "BACKEND_USER_CONFIGURATION",
                "requested_format": format_hint,
                "detected_format": detected_format,
                "ok": True,
            },
        )

    def _user_configuration_validation_response(
        self,
        validation: Mapping[str, Any],
        *,
        validation_scope: str,
        format_label: str,
        text_parse: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_config = validation.get("normalized_config")
        normalized_hash = (
            stable_hash_payload(normalized_config)
            if isinstance(normalized_config, dict)
            else None
        )
        change_summary = (
            _user_configuration_change_summary(
                self._controller.config_json(),
                normalized_config,
            )
            if isinstance(normalized_config, dict)
            else None
        )
        apply_readiness = (
            _user_configuration_apply_readiness(
                initialized=self._initialized,
                controller_status=self._controller.snapshot().status.value,
                lifecycle_state=self._require_session().lifecycle_state.value,
            )
            if isinstance(normalized_config, dict)
            else None
        )
        response = {
            "type": "USER_CONFIGURATION_VALIDATION_REPORT",
            "summary": {
                "version": "v1",
                "source": "BACKEND_USER_CONFIGURATION",
                "schema_id": USER_CONFIGURATION_SCHEMA_V2_ID,
                "validation_scope": validation_scope,
                "format": format_label,
                "mutation_policy": "VALIDATE_ONLY_NO_APPLY",
                "unknown_key_policy": "REJECT",
                "defaulting_policy": "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
                "ok": bool(validation["ok"]),
                "error_count": int(validation["error_count"]),
                "errors": tuple(validation["errors"]),
                "normalized_config_hash": normalized_hash,
                "normalized_config": normalized_config,
                "change_summary": change_summary,
                "apply_readiness": apply_readiness,
                "apply_command": _user_configuration_apply_command(),
            },
        }
        if text_parse is not None:
            response["summary"]["text_parse"] = text_parse
        return response

    def runtime_user_details(
        self,
        cursor: int = 0,
        limit: int = 100,
        *,
        query: str = "",
    ) -> dict[str, Any]:
        summary = build_runtime_user_request_summary(
            self.visible_snapshot(),
            service_latency_history=self._service_latency_history_json(),
            cursor=cursor,
            limit=limit,
            query=query,
        )
        return {
            "type": "RUNTIME_DETAIL_PAGE",
            "kind": "users",
            "summary": summary,
        }

    def runtime_user_detail(self, user_id: str) -> dict[str, Any]:
        summary = build_runtime_user_detail_card(
            self.visible_snapshot(),
            user_id,
            service_latency_history=self._service_latency_history_json(),
        )
        if summary is None:
            raise KeyError(f"runtime user detail not found: {user_id}")
        return {
            "type": "RUNTIME_ENTITY_DETAIL",
            "kind": "user",
            "entity_id": str(summary["entity_id"]),
            "summary": summary,
        }

    def runtime_satellite_details(
        self,
        cursor: int = 0,
        limit: int = 120,
        *,
        query: str = "",
    ) -> dict[str, Any]:
        summary = build_runtime_satellite_service_summary(
            self.visible_snapshot(),
            service_latency_history=self._service_latency_history_json(),
            satellite_kpi_slices=self._satellite_kpi_slices_json(),
            cursor=cursor,
            limit=limit,
            query=query,
        )
        return {
            "type": "RUNTIME_DETAIL_PAGE",
            "kind": "satellites",
            "summary": summary,
        }

    def runtime_satellite_detail(self, satellite_id: str) -> dict[str, Any]:
        summary = build_runtime_satellite_detail_card(
            self.visible_snapshot(),
            satellite_id,
            service_latency_history=self._service_latency_history_json(),
            satellite_kpi_slices=self._satellite_kpi_slices_json(),
        )
        if summary is None:
            raise KeyError(f"runtime satellite detail not found: {satellite_id}")
        return {
            "type": "RUNTIME_ENTITY_DETAIL",
            "kind": "satellite",
            "entity_id": str(summary["entity_id"]),
            "summary": summary,
        }

    def runtime_node_details(self, cursor: int = 0, limit: int = 100) -> dict[str, Any]:
        summary = build_runtime_node_detail_page(
            self.visible_snapshot(),
            service_latency_history=self._service_latency_history_json(),
            satellite_kpi_slices=self._satellite_kpi_slices_json(),
            cursor=cursor,
            limit=limit,
        )
        return {
            "type": "RUNTIME_DETAIL_PAGE",
            "kind": "nodes",
            "summary": summary,
        }

    def runtime_route_details(
        self,
        cursor: int = 0,
        limit: int = 100,
        *,
        query: str = "",
        availability: str = "ALL",
        business_type: str = "ALL",
        bottleneck_component: str = "ALL",
    ) -> dict[str, Any]:
        summary = build_runtime_route_explanation_summary(
            self.visible_snapshot(),
            service_latency_history=self._service_latency_history_json(),
            cursor=cursor,
            limit=limit,
            query=query,
            availability=availability,
            business_type=business_type,
            bottleneck_component=bottleneck_component,
        )
        return {
            "type": "RUNTIME_DETAIL_PAGE",
            "kind": "routes",
            "summary": summary,
        }

    def runtime_route_detail(self, route_id: str) -> dict[str, Any]:
        summary = build_runtime_route_detail_item(
            self.visible_snapshot(),
            route_id,
            service_latency_history=self._service_latency_history_json(),
        )
        if summary is None:
            raise KeyError(f"runtime route detail not found: {route_id}")
        return {
            "type": "RUNTIME_ENTITY_DETAIL",
            "kind": "route",
            "entity_id": str(summary["route_id"]),
            "summary": summary,
        }

    def runtime_service_details(
        self,
        cursor: int = 0,
        limit: int = 100,
        *,
        query: str = "",
    ) -> dict[str, Any]:
        summary = build_runtime_service_detail_page(
            self._service_latency_history_json(),
            cursor=cursor,
            limit=limit,
            query=query,
        )
        return {
            "type": "RUNTIME_DETAIL_PAGE",
            "kind": "services",
            "summary": summary,
        }

    def runtime_service_detail(self, service_id: str) -> dict[str, Any]:
        summary = build_runtime_service_detail_item(
            self._service_latency_history_json(),
            service_id,
        )
        if summary is None:
            raise KeyError(f"runtime service detail not found: {service_id}")
        return {
            "type": "RUNTIME_ENTITY_DETAIL",
            "kind": "service",
            "entity_id": str(summary["service_id"]),
            "summary": summary,
        }

    def runtime_service_trace_details(
        self,
        cursor: int = 0,
        limit: int = 100,
        *,
        query: str = "",
        terminal_state: str = "ALL",
        compute_node_id: str = "",
        stage_kind: str = "ALL",
        terminal_reason: str = "ALL",
    ) -> dict[str, Any]:
        summary = build_runtime_service_lifecycle_trace_v2(
            self._service_latency_history_json(),
            cursor=cursor,
            limit=limit,
            query=query,
            terminal_state=terminal_state,
            compute_node_id=compute_node_id,
            stage_kind=stage_kind,
            terminal_reason=terminal_reason,
        )
        return {
            "type": "RUNTIME_DETAIL_PAGE",
            "kind": "service_traces",
            "summary": summary,
        }

    def runtime_service_trace_detail(self, trace_id: str) -> dict[str, Any]:
        summary = build_runtime_service_trace_detail_item(
            self.visible_snapshot(),
            self._service_latency_history_json(),
            trace_id,
            satellite_kpi_slices=self._satellite_kpi_slices_json(),
        )
        if summary is None:
            raise KeyError(f"runtime service trace detail not found: {trace_id}")
        trace = summary["trace"]
        if not isinstance(trace, dict):
            raise KeyError(f"runtime service trace detail not found: {trace_id}")
        return {
            "type": "RUNTIME_ENTITY_DETAIL",
            "kind": "service_trace",
            "entity_id": str(trace["trace_id"]),
            "summary": summary,
        }

    def runtime_compute_node_details(
        self,
        cursor: int = 0,
        limit: int = 100,
        *,
        query: str = "",
    ) -> dict[str, Any]:
        summary = build_runtime_compute_node_detail_page(
            self.visible_snapshot(),
            satellite_kpi_slices=self._satellite_kpi_slices_json(),
            cursor=cursor,
            limit=limit,
            query=query,
        )
        return {
            "type": "RUNTIME_DETAIL_PAGE",
            "kind": "compute_nodes",
            "summary": summary,
        }

    def runtime_compute_node_detail(self, node_id: str) -> dict[str, Any]:
        summary = build_runtime_compute_node_detail_item(
            self.visible_snapshot(),
            node_id,
            satellite_kpi_slices=self._satellite_kpi_slices_json(),
        )
        if summary is None:
            raise KeyError(f"runtime compute node detail not found: {node_id}")
        return {
            "type": "RUNTIME_ENTITY_DETAIL",
            "kind": "compute_node",
            "entity_id": str(summary["node_id"]),
            "summary": summary,
        }

    def version_info(self) -> dict[str, Any]:
        return {
            "type": "VERSION_INFO",
            "summary": build_version_info_v1(),
        }

    def export_runtime_package(
        self,
        output_root: str | Path = "artifacts/runtime_exports",
        *,
        record_history: bool = True,
    ) -> dict[str, Any]:
        if self._runtime_context is None:
            raise RuntimeError("runtime metrics are unavailable for export")
        generated_config = self._generated_config_json()
        status = self._status_json(generated_config)
        package_id = _runtime_export_package_id(
            self._require_session().session_id,
            status,
        )
        package_dir = Path(output_root) / package_id
        package_dir.mkdir(parents=True, exist_ok=True)

        written_files = dict(self._runtime_context.metrics.write_outputs(package_dir))
        export_status = self._runtime_export_status_json(status)
        config_snapshot = {
            "type": "RUNTIME_CONFIG_SNAPSHOT",
            "status": export_status,
            "config": self._controller.config_json(),
            "generated_config": generated_config,
        }
        config_snapshot_path = package_dir / "config_snapshot.json"
        manifest_path = package_dir / "manifest.json"
        config_snapshot_path.write_text(
            stable_json_pretty(config_snapshot), encoding="utf-8"
        )
        manifest = dict(export_status["reproducibility_manifest_v1"])
        manifest_path.write_text(stable_json_pretty(manifest), encoding="utf-8")
        service_lifecycle_trace_path = (
            package_dir / _SERVICE_LIFECYCLE_TRACE_EXPORT_FILENAME
        )
        service_lifecycle_trace_path.write_text(
            stable_json_pretty(_runtime_service_lifecycle_trace_export(export_status)),
            encoding="utf-8",
        )
        route_detail_index_path = (
            package_dir / _RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_FILENAME
        )
        route_detail_index = build_runtime_export_route_detail_index_v1(
            package_id=package_id,
            package_dir=str(package_dir),
            config_snapshot=config_snapshot,
        )
        route_detail_index_path.write_text(
            stable_json_pretty(route_detail_index),
            encoding="utf-8",
        )
        written_files["config_snapshot"] = config_snapshot_path
        written_files["manifest"] = manifest_path
        written_files["service_lifecycle_trace_v2"] = service_lifecycle_trace_path
        written_files["route_detail_index_v1"] = route_detail_index_path
        review_summary_path = package_dir / _RUNTIME_EXPORT_REVIEW_SUMMARY_FILENAME
        diagnostics_bundle_path = (
            package_dir / _RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_FILENAME
        )
        scenario_review_bundle_path = (
            package_dir / _RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_FILENAME
        )
        audit_index_path = package_dir / _RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_FILENAME
        handoff_report_path = (
            package_dir / _RUNTIME_EXPORT_PACKAGE_HANDOFF_REPORT_FILENAME
        )
        artifact_filenames = tuple(
            sorted(
                path.name
                for path in (
                    *written_files.values(),
                    review_summary_path,
                    diagnostics_bundle_path,
                    scenario_review_bundle_path,
                    audit_index_path,
                    handoff_report_path,
                )
            )
        )
        review_summary = build_runtime_export_review_summary_v1(
            package_id=package_id,
            package_dir=str(package_dir),
            config_snapshot=config_snapshot,
            manifest=manifest,
            artifact_filenames=artifact_filenames,
        )
        review_summary_path.write_text(
            stable_json_pretty(review_summary),
            encoding="utf-8",
        )
        written_files["review_summary_v1"] = review_summary_path
        diagnostics_bundle = build_runtime_export_diagnostics_bundle_v1(
            package_id=package_id,
            package_dir=str(package_dir),
            config_snapshot=config_snapshot,
            manifest=manifest,
            review_summary=review_summary,
            artifact_filenames=artifact_filenames,
        )
        diagnostics_bundle_path.write_text(
            stable_json_pretty(diagnostics_bundle),
            encoding="utf-8",
        )
        written_files["diagnostics_bundle_v1"] = diagnostics_bundle_path
        user_configuration_export = self.user_configuration_export()["summary"]
        scenario_review_bundle = build_runtime_export_scenario_review_bundle_v1(
            package_id=package_id,
            package_dir=str(package_dir),
            config_snapshot=config_snapshot,
            manifest=manifest,
            review_summary=review_summary,
            diagnostics_bundle=diagnostics_bundle,
            user_configuration_export=user_configuration_export,
            artifact_filenames=artifact_filenames,
        )
        scenario_review_bundle_path.write_text(
            stable_json_pretty(scenario_review_bundle),
            encoding="utf-8",
        )
        written_files["scenario_review_bundle_v1"] = scenario_review_bundle_path
        audit_compare = _runtime_export_package_compare_summary(
            package_id,
            config_snapshot,
            config_snapshot,
            diff_limit=0,
        )
        raw_alignment = audit_compare.get("runtime_export_boundary_alignment_v1")
        runtime_export_boundary_alignment: Mapping[str, Any] = (
            raw_alignment if isinstance(raw_alignment, Mapping) else {}
        )
        audit_index, audit_artifact = self._write_runtime_export_package_audit_index(
            package_id,
            package_dir,
            config_snapshot=config_snapshot,
            manifest=manifest,
            review_summary=review_summary,
            diagnostics_bundle=diagnostics_bundle,
            runtime_export_boundary_alignment=runtime_export_boundary_alignment,
        )
        _, handoff_artifact = self._write_runtime_export_package_handoff_report(
            package_id,
            package_dir,
            audit_index=audit_index,
        )
        written_files["export_package_audit_index_v1"] = audit_index_path
        written_files["package_handoff_report_v1"] = handoff_report_path

        files = tuple(
            _runtime_export_file_record(name, path)
            for name, path in sorted(written_files.items())
        )
        package = {
            "type": "RUNTIME_EXPORT",
            "ok": True,
            "package_id": package_id,
            "package_dir": str(package_dir),
            "file_count": len(files),
            "files": files,
            "manifest": manifest,
        }
        if record_history:
            package["export_history_record"] = self._record_runtime_export(
                "PACKAGE",
                package,
            )
        package["export_catalog_record"] = _write_runtime_export_catalog(
            output_root,
            "PACKAGE",
            package,
        )["latest_export"]
        return package

    def export_runtime_archive(
        self,
        output_root: str | Path = "artifacts/runtime_exports",
    ) -> dict[str, Any]:
        package = self.export_runtime_package(output_root, record_history=False)
        package_dir = Path(str(package["package_dir"]))
        archive_path = package_dir / f"{package['package_id']}.zip"
        _write_runtime_export_archive(package_dir, archive_path)
        archive_record = _runtime_export_file_record("archive", archive_path)
        archive_package = dict(package)
        archive_package["archive"] = archive_record
        archive_package["export_history_record"] = self._record_runtime_export(
            "ARCHIVE",
            archive_package,
        )
        archive_package["export_catalog_record"] = _write_runtime_export_catalog(
            output_root,
            "ARCHIVE",
            archive_package,
        )["latest_export"]
        return archive_package

    def runtime_export_history(self) -> dict[str, Any]:
        return {
            "type": "RUNTIME_EXPORT_HISTORY",
            "summary": self._runtime_export_history_json(),
        }

    def runtime_export_catalog(
        self,
        output_root: str | Path = "artifacts/runtime_exports",
    ) -> dict[str, Any]:
        return {
            "type": "RUNTIME_EXPORT_CATALOG",
            "summary": _read_runtime_export_catalog(output_root),
        }

    def runtime_export_package_record(
        self,
        package_id: str,
        output_root: str | Path = "artifacts/runtime_exports",
    ) -> dict[str, Any]:
        catalog = _read_runtime_export_catalog(output_root)
        record = _runtime_export_catalog_package_record(catalog, package_id)
        return {
            "type": "RUNTIME_EXPORT_PACKAGE_RECORD",
            "summary": record,
        }

    def runtime_export_package_artifact(
        self,
        package_id: str,
        filename: str,
        output_root: str | Path = "artifacts/runtime_exports",
    ) -> dict[str, Any]:
        catalog = _read_runtime_export_catalog(output_root)
        record = _runtime_export_catalog_package_record(catalog, package_id)
        file_record = _runtime_export_catalog_file(record, filename)
        path = _runtime_export_catalog_file_path(output_root, record, file_record)
        return {
            "path": path,
            "filename": file_record["filename"],
            "content_type": _runtime_export_content_type(file_record["filename"]),
            "sha256": file_record["sha256"],
            "bytes": file_record["bytes"],
        }

    def runtime_export_package_route_details(
        self,
        package_id: str,
        output_root: str | Path = "artifacts/runtime_exports",
        *,
        cursor: int = 0,
        limit: int = 100,
        query: str = "",
        availability: str = "ALL",
        business_type: str = "ALL",
        bottleneck_component: str = "ALL",
    ) -> dict[str, Any]:
        route_detail_index = self._runtime_export_package_route_detail_index(
            package_id,
            output_root,
        )
        return build_runtime_export_route_detail_page_v1(
            route_detail_index,
            cursor=cursor,
            limit=limit,
            query=query,
            availability=availability,
            business_type=business_type,
            bottleneck_component=bottleneck_component,
        )

    def runtime_export_package_service_traces(
        self,
        package_id: str,
        output_root: str | Path = "artifacts/runtime_exports",
        *,
        cursor: int = 0,
        limit: int = 100,
        query: str = "",
        terminal_state: str = "ALL",
        compute_node_id: str = "",
        stage_kind: str = "ALL",
        terminal_reason: str = "ALL",
    ) -> dict[str, Any]:
        service_trace_export = self._runtime_export_package_service_trace_export(
            package_id,
            output_root,
        )
        return build_runtime_export_service_trace_page_v1(
            service_trace_export,
            package_id=package_id,
            cursor=cursor,
            limit=limit,
            query=query,
            terminal_state=terminal_state,
            compute_node_id=compute_node_id,
            stage_kind=stage_kind,
            terminal_reason=terminal_reason,
        )

    def runtime_export_package_review_completion(
        self,
        package_id: str,
        output_root: str | Path = "artifacts/runtime_exports",
    ) -> dict[str, Any]:
        audit_artifact = self.runtime_export_package_artifact(
            package_id,
            _RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_FILENAME,
            output_root,
        )
        audit_index = json.loads(
            Path(str(audit_artifact["path"])).read_text(encoding="utf-8")
        )
        if not isinstance(audit_index, Mapping):
            raise RuntimeExportArtifactError(
                f"runtime export package {package_id!r} has invalid audit index"
            )
        completion = audit_index.get("package_review_completion_v1")
        if not isinstance(completion, Mapping):
            raise RuntimeExportArtifactError(
                f"runtime export package {package_id!r} has no package review completion evidence"
            )
        return {
            "type": "RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION",
            "summary": dict(completion),
            "source_artifact": _runtime_export_catalog_file_record(audit_artifact),
        }

    def runtime_export_package_route_detail(
        self,
        package_id: str,
        route_id: str,
        output_root: str | Path = "artifacts/runtime_exports",
    ) -> dict[str, Any]:
        route_detail_index = self._runtime_export_package_route_detail_index(
            package_id,
            output_root,
        )
        detail = build_runtime_export_route_detail_item_v1(
            route_detail_index,
            route_id,
        )
        if detail is None:
            raise RuntimeExportArtifactError(
                f"runtime export package {package_id!r} route {route_id!r} not found"
            )
        return detail

    def runtime_export_package_route_comparison_review_report(
        self,
        package_id: str,
        payload: Mapping[str, Any],
        output_root: str | Path = "artifacts/runtime_exports",
    ) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise RuntimeError("route comparison review report payload must be an object")
        route_detail_index = self._runtime_export_package_route_detail_index(
            package_id,
            output_root,
        )
        route_comparison_review = route_detail_index.get("route_comparison_review")
        if not isinstance(route_comparison_review, Mapping):
            raise RuntimeExportArtifactError(
                f"runtime export package {package_id!r} has no route comparison review metadata"
            )
        raw_records = payload.get("records", ())
        if raw_records is None:
            raw_records = ()
        if not isinstance(raw_records, (list, tuple)):
            raise RuntimeError("route comparison review report records must be a list")
        records: list[Mapping[str, Any]] = []
        for record in raw_records:
            if not isinstance(record, Mapping):
                raise RuntimeError(
                    "route comparison review report records must be objects"
                )
            records.append(record)
        catalog = _read_runtime_export_catalog(output_root)
        catalog_record = _runtime_export_catalog_package_record(catalog, package_id)
        package_dir = _runtime_export_catalog_package_dir(output_root, catalog_record)
        preflight = self.runtime_export_package_restore_preflight(
            package_id,
            output_root,
        )
        preflight_summary = preflight.get("summary")
        runtime_export_boundary_alignment: Mapping[str, Any] = {}
        if isinstance(preflight_summary, Mapping):
            raw_alignment = preflight_summary.get(
                "runtime_export_boundary_alignment_v1"
            )
            if isinstance(raw_alignment, Mapping):
                runtime_export_boundary_alignment = raw_alignment
        report = build_runtime_export_route_comparison_review_report_v1(
            package_id=package_id,
            package_dir=str(package_dir),
            route_comparison_review=route_comparison_review,
            runtime_export_boundary_alignment=runtime_export_boundary_alignment,
            records=tuple(records),
        )
        report_path = package_dir / _RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_FILENAME
        report_path.write_text(stable_json_pretty(report), encoding="utf-8")
        artifact = _runtime_export_file_record(
            "route_comparison_review_report_v1",
            report_path,
        )
        catalog_record = _upsert_runtime_export_catalog_file(
            output_root,
            package_id,
            artifact,
        )
        audit_index, audit_artifact = self._write_runtime_export_package_audit_index(
            package_id,
            package_dir,
            runtime_export_boundary_alignment=runtime_export_boundary_alignment,
        )
        catalog_record = _upsert_runtime_export_catalog_file(
            output_root,
            package_id,
            audit_artifact,
        )
        _, handoff_artifact = self._write_runtime_export_package_handoff_report(
            package_id,
            package_dir,
            audit_index=audit_index,
        )
        catalog_record = _upsert_runtime_export_catalog_file(
            output_root,
            package_id,
            handoff_artifact,
        )
        return {
            "type": "RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT",
            "summary": report,
            "artifact": _runtime_export_catalog_file_record(artifact),
            "audit_index": audit_index,
            "audit_artifact": _runtime_export_catalog_file_record(audit_artifact),
            "handoff_report_artifact": _runtime_export_catalog_file_record(
                handoff_artifact
            ),
            "catalog_record": catalog_record,
        }

    def runtime_export_package_scenario_review_checklist(
        self,
        package_id: str,
        payload: Mapping[str, Any],
        output_root: str | Path = "artifacts/runtime_exports",
    ) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise RuntimeError("scenario review checklist payload must be an object")
        raw_records = payload.get("records", ())
        if raw_records is None:
            raw_records = ()
        if not isinstance(raw_records, (list, tuple)):
            raise RuntimeError("scenario review checklist records must be a list")
        records: list[Mapping[str, Any]] = []
        for record in raw_records:
            if not isinstance(record, Mapping):
                raise RuntimeError("scenario review checklist records must be objects")
            records.append(record)
        catalog = _read_runtime_export_catalog(output_root)
        catalog_record = _runtime_export_catalog_package_record(catalog, package_id)
        package_dir = _runtime_export_catalog_package_dir(output_root, catalog_record)
        scenario_review_artifact = self.runtime_export_package_artifact(
            package_id,
            _RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_FILENAME,
            output_root,
        )
        scenario_review_bundle = json.loads(
            Path(str(scenario_review_artifact["path"])).read_text(encoding="utf-8")
        )
        if not isinstance(scenario_review_bundle, Mapping):
            raise RuntimeExportArtifactError(
                f"runtime export package {package_id!r} has invalid scenario review bundle"
            )
        checklist = build_runtime_export_scenario_review_checklist_v1(
            package_id=package_id,
            package_dir=str(package_dir),
            scenario_review_bundle=scenario_review_bundle,
            records=tuple(records),
        )
        checklist_path = package_dir / _RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_FILENAME
        checklist_path.write_text(stable_json_pretty(checklist), encoding="utf-8")
        artifact = _runtime_export_file_record(
            "scenario_review_checklist_v1",
            checklist_path,
        )
        catalog_record = _upsert_runtime_export_catalog_file(
            output_root,
            package_id,
            artifact,
        )
        audit_index, audit_artifact = self._write_runtime_export_package_audit_index(
            package_id,
            package_dir,
        )
        catalog_record = _upsert_runtime_export_catalog_file(
            output_root,
            package_id,
            audit_artifact,
        )
        _, handoff_artifact = self._write_runtime_export_package_handoff_report(
            package_id,
            package_dir,
            audit_index=audit_index,
        )
        catalog_record = _upsert_runtime_export_catalog_file(
            output_root,
            package_id,
            handoff_artifact,
        )
        return {
            "type": "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST",
            "summary": checklist,
            "artifact": _runtime_export_catalog_file_record(artifact),
            "audit_index": audit_index,
            "audit_artifact": _runtime_export_catalog_file_record(audit_artifact),
            "handoff_report_artifact": _runtime_export_catalog_file_record(
                handoff_artifact
            ),
            "catalog_record": catalog_record,
        }

    def _write_runtime_export_package_audit_index(
        self,
        package_id: str,
        package_dir: Path,
        *,
        config_snapshot: Mapping[str, Any] | None = None,
        manifest: Mapping[str, Any] | None = None,
        review_summary: Mapping[str, Any] | None = None,
        diagnostics_bundle: Mapping[str, Any] | None = None,
        runtime_export_boundary_alignment: Mapping[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if config_snapshot is None:
            config_snapshot = self._runtime_export_package_config_snapshot(
                package_id,
                package_dir.parent,
            )
        if manifest is None:
            manifest_artifact = self.runtime_export_package_artifact(
                package_id,
                "manifest.json",
                package_dir.parent,
            )
            manifest = json.loads(
                Path(str(manifest_artifact["path"])).read_text(encoding="utf-8")
            )
        if review_summary is None:
            review_artifact = self.runtime_export_package_artifact(
                package_id,
                _RUNTIME_EXPORT_REVIEW_SUMMARY_FILENAME,
                package_dir.parent,
            )
            review_summary = json.loads(
                Path(str(review_artifact["path"])).read_text(encoding="utf-8")
            )
        if diagnostics_bundle is None:
            diagnostics_artifact = self.runtime_export_package_artifact(
                package_id,
                _RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_FILENAME,
                package_dir.parent,
            )
            diagnostics_bundle = json.loads(
                Path(str(diagnostics_artifact["path"])).read_text(encoding="utf-8")
            )
        route_report: Mapping[str, Any] | None = None
        route_report_path = (
            package_dir / _RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_FILENAME
        )
        if route_report_path.is_file():
            raw_route_report = json.loads(route_report_path.read_text(encoding="utf-8"))
            if isinstance(raw_route_report, Mapping):
                route_report = raw_route_report
        scenario_checklist: Mapping[str, Any] | None = None
        scenario_checklist_path = (
            package_dir / _RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_FILENAME
        )
        if scenario_checklist_path.is_file():
            raw_scenario_checklist = json.loads(
                scenario_checklist_path.read_text(encoding="utf-8")
            )
            if isinstance(raw_scenario_checklist, Mapping):
                scenario_checklist = raw_scenario_checklist
        artifact_records = tuple(
            _runtime_export_file_record(path.stem, path)
            for path in sorted(package_dir.iterdir(), key=lambda item: item.name)
            if path.is_file()
            and path.name not in {
                _RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_FILENAME,
                _RUNTIME_EXPORT_PACKAGE_HANDOFF_REPORT_FILENAME,
            }
            and path.suffix.lower() != ".zip"
        )
        audit_index = build_runtime_export_package_audit_index_v1(
            package_id=package_id,
            package_dir=str(package_dir),
            config_snapshot=config_snapshot,
            manifest=manifest,
            review_summary=review_summary,
            diagnostics_bundle=diagnostics_bundle,
            artifact_records=artifact_records,
            route_comparison_review_report=route_report,
            scenario_review_checklist=scenario_checklist,
            runtime_export_boundary_alignment=runtime_export_boundary_alignment,
            user_configuration_export=self.user_configuration_export()["summary"],
        )
        audit_path = package_dir / _RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_FILENAME
        audit_path.write_text(stable_json_pretty(audit_index), encoding="utf-8")
        audit_artifact = _runtime_export_file_record(
            "export_package_audit_index_v1",
            audit_path,
        )
        return audit_index, audit_artifact

    def _write_runtime_export_package_handoff_report(
        self,
        package_id: str,
        package_dir: Path,
        *,
        audit_index: Mapping[str, Any] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        if audit_index is None:
            audit_artifact = self.runtime_export_package_artifact(
                package_id,
                _RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_FILENAME,
                package_dir.parent,
            )
            raw_audit_index = json.loads(
                Path(str(audit_artifact["path"])).read_text(encoding="utf-8")
            )
            if not isinstance(raw_audit_index, Mapping):
                raise RuntimeExportArtifactError(
                    f"runtime export package {package_id!r} has invalid audit index"
                )
            audit_index = raw_audit_index
        report = build_runtime_export_package_handoff_report_v1(
            audit_index=audit_index,
        )
        report_path = package_dir / _RUNTIME_EXPORT_PACKAGE_HANDOFF_REPORT_FILENAME
        report_path.write_text(report, encoding="utf-8")
        artifact = _runtime_export_file_record(
            "package_handoff_report_v1",
            report_path,
        )
        return report, artifact

    def runtime_export_package_archive_artifact(
        self,
        package_id: str,
        output_root: str | Path = "artifacts/runtime_exports",
    ) -> dict[str, Any]:
        catalog = _read_runtime_export_catalog(output_root)
        record = _runtime_export_catalog_package_record(catalog, package_id)
        archive_filename = str(record.get("archive_filename", ""))
        if not archive_filename:
            raise RuntimeExportArtifactError(
                f"runtime export package {package_id!r} has no archive"
            )
        package_dir = _runtime_export_catalog_package_dir(output_root, record)
        path = _runtime_export_safe_child_file(package_dir, archive_filename)
        return {
            "path": path,
            "filename": archive_filename,
            "content_type": "application/zip",
            "sha256": str(record.get("archive_sha256", "")),
            "bytes": _control_int(record.get("archive_bytes")),
        }

    def runtime_export_package_compare(
        self,
        package_id: str,
        output_root: str | Path = "artifacts/runtime_exports",
        *,
        diff_limit: int = 32,
    ) -> dict[str, Any]:
        artifact = self.runtime_export_package_artifact(
            package_id,
            "config_snapshot.json",
            output_root,
        )
        package_snapshot = json.loads(
            Path(str(artifact["path"])).read_text(encoding="utf-8")
        )
        if not isinstance(package_snapshot, dict):
            raise RuntimeExportArtifactError(
                f"runtime export package {package_id!r} has invalid config snapshot"
            )
        generated_config = self._generated_config_json()
        current_snapshot = {
            "type": "RUNTIME_CONFIG_SNAPSHOT",
            "status": _runtime_export_status_snapshot(
                self._status_json(generated_config)
            ),
            "config": self._controller.config_json(),
            "generated_config": generated_config,
        }
        summary = _runtime_export_package_compare_summary(
            package_id,
            package_snapshot,
            current_snapshot,
            diff_limit=diff_limit,
        )
        return {
            "type": "RUNTIME_EXPORT_PACKAGE_COMPARE",
            "summary": summary,
        }

    def runtime_export_package_restore_preflight(
        self,
        package_id: str,
        output_root: str | Path = "artifacts/runtime_exports",
        *,
        diff_limit: int = 32,
    ) -> dict[str, Any]:
        artifact = self.runtime_export_package_artifact(
            package_id,
            "config_snapshot.json",
            output_root,
        )
        package_snapshot = json.loads(
            Path(str(artifact["path"])).read_text(encoding="utf-8")
        )
        if not isinstance(package_snapshot, dict):
            raise RuntimeExportArtifactError(
                f"runtime export package {package_id!r} has invalid config snapshot"
            )
        generated_config = self._generated_config_json()
        current_snapshot = {
            "type": "RUNTIME_CONFIG_SNAPSHOT",
            "status": _runtime_export_status_snapshot(
                self._status_json(generated_config)
            ),
            "config": self._controller.config_json(),
            "generated_config": generated_config,
        }
        compare = _runtime_export_package_compare_summary(
            package_id,
            package_snapshot,
            current_snapshot,
            diff_limit=diff_limit,
        )
        summary = _runtime_export_package_restore_preflight_summary(
            package_id,
            package_snapshot,
            current_snapshot,
            compare,
            lifecycle_state=self.runtime_lifecycle_state().value,
        )
        return {
            "type": "RUNTIME_EXPORT_RESTORE_PREFLIGHT",
            "summary": summary,
        }

    def restore_runtime_export_package(
        self,
        package_id: str,
        output_root: str | Path = "artifacts/runtime_exports",
        *,
        confirm_restore: bool = False,
        diff_limit: int = 32,
    ) -> dict[str, Any]:
        if not confirm_restore:
            raise RuntimeError("restore requires confirm_restore=true")
        preflight = self.runtime_export_package_restore_preflight(
            package_id,
            output_root,
            diff_limit=diff_limit,
        )
        preflight_summary = preflight["summary"]
        readiness = str(preflight_summary.get("readiness", ""))
        if readiness == "BLOCKED" or not bool(preflight_summary.get("can_restore")):
            blocked_reasons = tuple(preflight_summary.get("blocked_reasons", ()))
            detail = "; ".join(str(item) for item in blocked_reasons) or readiness
            raise RuntimeError(f"runtime export restore is blocked: {detail}")

        restore_result = _runtime_export_restore_result(
            package_id,
            preflight_summary,
            restored=False,
            rollback_package=None,
        )
        if readiness == "READY":
            loop = self._advance_loop
            self._stop_advance_loop()
            if loop is not None:
                loop.publish_pending()
            rollback_package = self.export_runtime_package(output_root)
            package_snapshot = self._runtime_export_package_config_snapshot(
                package_id,
                output_root,
            )
            package_config = package_snapshot.get("config")
            if not isinstance(package_config, dict):
                raise RuntimeExportArtifactError(
                    f"runtime export package {package_id!r} has invalid config"
                )
            restored_config = config_from_mapping(package_config)
            self._controller.initialize(config_to_dict(restored_config))
            write_config(self._config_output_path, self._controller.config)
            write_full_system_scenario_builder_config(
                self._generated_config_output_path,
                scenario_builder_config_from_sees_config(self._controller.config),
            )
            updated_demo_config = demo_config_from_sees_config(
                self._controller.config,
                self._base_config,
            )
            self._install_runtime_session(updated_demo_config)
            if self._runtime_context is not None:
                self._result = finalize_integration_demo_run(self._runtime_context, ())
            self._initialized = True
            restore_result = _runtime_export_restore_result(
                package_id,
                preflight_summary,
                restored=True,
                rollback_package=rollback_package,
            )

        response = self._ack_for_command_name(_RUNTIME_EXPORT_RESTORE_COMMAND)
        response["restore_preflight"] = preflight_summary
        response["restore_result"] = restore_result
        return response

    def visible_snapshot(self) -> dict[str, JsonValue]:
        session = self._require_session()
        if self._initialized and session.lifecycle_state in {
            RuntimeLifecycleState.INITIALIZED,
            RuntimeLifecycleState.RUNNING,
            RuntimeLifecycleState.PAUSED,
            RuntimeLifecycleState.COMPLETED,
        }:
            return session.get_snapshot()  # type: ignore[return-value]
        return _initial_snapshot(self._result)

    def stream_events(self) -> tuple[dict[str, JsonValue], ...]:
        if not self._live_stream_active():
            return ()
        self._require_advance_loop().publish_pending()
        batch = self._require_advance_loop().event_stream.read_after(0)
        return tuple(
            event_to_json(event)
            for event in batch.items
            if str(event.event_type) in _FRONTEND_EVENT_TYPES
        )

    def stream_snapshots(self) -> tuple[dict[str, JsonValue], ...]:
        if not self._live_stream_active():
            return ()
        loop = self._require_advance_loop()
        loop.publish_pending()
        snapshots = loop.snapshot_stream.read_after(0).items
        if not snapshots:
            snapshots = (self._require_runtime_adapter().snapshot(),)
        return snapshots  # type: ignore[return-value]

    def stream_event_batch(
        self,
        cursor: int = 0,
        limit: int | None = None,
    ) -> dict[str, Any]:
        self._require_advance_loop().publish_pending()
        return _frontend_event_batch(
            self._require_advance_loop().event_stream,
            cursor,
            limit,
        )

    def stream_snapshot_batch(
        self,
        cursor: int = 0,
        limit: int | None = None,
    ) -> dict[str, Any]:
        self._require_advance_loop().publish_pending()
        return self._require_advance_loop().snapshot_stream.read_after(
            cursor,
            limit=limit,
        ).to_dict()

    def handle_raw_message(self, raw: str | bytes) -> dict[str, Any]:
        command_name = "UNKNOWN"
        try:
            restore_payload = _runtime_export_restore_control_payload(raw)
            if restore_payload is not None:
                command_name = _RUNTIME_EXPORT_RESTORE_COMMAND
                return self._restore_runtime_export_package(restore_payload)
            command = parse_control_command(raw)
            command_name = command.command.value
            if command.command == RuntimeCommand.INITIALIZE:
                return self._initialize(command.payload)
            if command.command == RuntimeCommand.START and not self._initialized:
                raise RuntimeError("simulation must be initialized before start")
            if command.command == RuntimeCommand.REQUEST_STATUS:
                return self._ack(command)
            if command.command == RuntimeCommand.REQUEST_SNAPSHOT:
                response = self._ack(command)
                response["snapshot"] = self.visible_snapshot()
                return response
            if command.command == RuntimeCommand.LOAD_TEMPLATE:
                return self._load_template(command.payload)
            if command.command == RuntimeCommand.RESET:
                return self._reset(command.payload)

            self._controller.handle_action(command.command.value, command.payload)
            if command.command == RuntimeCommand.START:
                self._require_session().start_live()
                runtime_ack = {"ok": True}
            elif command.command == RuntimeCommand.RESUME:
                self._require_session().resume_live()
                runtime_ack = {"ok": True}
            else:
                runtime_ack = self._require_runtime_adapter().handle_raw_message(
                    {"command": command.command.value, "payload": command.payload}
                )
            if not runtime_ack["ok"]:
                return self._nack(command_name, str(runtime_ack["error"]))
            if command.command == RuntimeCommand.START:
                self._require_advance_loop().publish_pending()
                response = self._ack(command)
                self._require_advance_loop().start()
                return response
            if command.command == RuntimeCommand.RESUME:
                self._require_advance_loop().publish_pending()
                response = self._ack(command)
                self._require_advance_loop().start()
                return response
            if command.command == RuntimeCommand.PAUSE:
                self._require_advance_loop().publish_pending()
            if command.command == RuntimeCommand.STOP:
                loop = self._require_advance_loop()
                loop.stop()
                loop.publish_pending()
            return self._ack(command)
        except Exception as exc:  # noqa: BLE001 - returned as protocol error
            return self._nack(command_name, str(exc))

    def _initialize(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._stop_advance_loop()
        self._controller.initialize(payload)
        write_config(self._config_output_path, self._controller.config)
        write_full_system_scenario_builder_config(
            self._generated_config_output_path,
            scenario_builder_config_from_sees_config(self._controller.config),
        )
        updated_demo_config = demo_config_from_sees_config(
            self._controller.config,
            self._base_config,
        )
        self._install_runtime_session(updated_demo_config)
        if self._runtime_context is not None:
            self._result = finalize_integration_demo_run(self._runtime_context, ())
        self._initialized = True
        return self._ack(ControlCommand(RuntimeCommand.INITIALIZE, payload))

    def _load_template(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._initialized:
            raise RuntimeError(
                "configuration templates can be loaded only before initialization; reset first"
            )
        template_id = payload.get("template_id")
        if not isinstance(template_id, str) or not template_id:
            raise RuntimeError("template_id is required")

        self._stop_advance_loop()
        if self._advance_loop is not None:
            self._advance_loop.reset_streams()
        next_config = load_user_configuration_template(template_id)
        self._controller.apply_config(next_config)
        write_config(self._config_output_path, self._controller.config)
        write_full_system_scenario_builder_config(
            self._generated_config_output_path,
            scenario_builder_config_from_sees_config(self._controller.config),
        )
        updated_demo_config = demo_config_from_sees_config(
            self._controller.config,
            self._base_config,
        )
        self._install_runtime_session(updated_demo_config)
        if self._runtime_context is not None:
            self._result = finalize_integration_demo_run(self._runtime_context, ())
        response = self._ack(
            ControlCommand(RuntimeCommand.LOAD_TEMPLATE, {"template_id": template_id})
        )
        response["loaded_template_id"] = template_id
        return response

    def _reset(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._stop_advance_loop()
        if self._advance_loop is not None:
            self._advance_loop.reset_streams()
        self._controller.handle_action(RuntimeCommand.RESET.value, payload)
        reset_demo_config = demo_config_from_sees_config(
            self._controller.config,
            self._base_config,
        )
        self._install_runtime_session(reset_demo_config)
        if self._runtime_context is not None:
            self._result = finalize_integration_demo_run(self._runtime_context, ())
        self._initialized = False
        return self._ack(ControlCommand(RuntimeCommand.RESET, payload))

    def _restore_runtime_export_package(self, payload: dict[str, Any]) -> dict[str, Any]:
        package_id = payload.get("package_id")
        if not isinstance(package_id, str) or not package_id.strip():
            raise RuntimeError("package_id is required")
        output_root = payload.get("output_root", "artifacts/runtime_exports")
        if not isinstance(output_root, str):
            raise RuntimeError("output_root must be a string")
        confirm_restore = payload.get("confirm_restore") is True
        raw_diff_limit = payload.get("diff_limit", 32)
        if isinstance(raw_diff_limit, bool) or not isinstance(raw_diff_limit, int):
            raise RuntimeError("diff_limit must be an integer")
        return self.restore_runtime_export_package(
            package_id.strip(),
            output_root,
            confirm_restore=confirm_restore,
            diff_limit=raw_diff_limit,
        )

    def _install_runtime_session(self, config: DemoConfig) -> None:
        self._stop_advance_loop()
        self._user_request_history.clear()
        self._export_history.clear()
        self._export_sequence = 0
        sees_config = demo_config_to_sees_config(config)
        fidelity_summary = _fidelity_summary_from_demo_config(config)

        def kernel_factory(
            _scenario_config: object,
            _runtime_config: object,
        ) -> RuntimeKernelSpec:
            context = build_integration_demo_runtime(config)
            self._runtime_context = context
            initial_satellites = _initial_satellite_states(config, context)
            return RuntimeKernelSpec(
                kernel=context.kernel,
                initial_events=context.scenario.initial_events,
                snapshot_projector=DemoStateProjector(
                    context.scenario.ground_user_render_states,
                    config.state_snapshot_interval_events,
                    initial_satellites=initial_satellites,
                    fidelity_summary=fidelity_summary,
                ),
                initial_snapshot=_initial_snapshot_from_ground_users(
                    context.scenario.ground_user_render_states,
                    initial_satellites,
                    fidelity_summary,
                ),
                tick_observer=context.profiler,
            )

        session = SimulationSession(
            session_id=f"integration-demo-{config.seed}",
            runtime_config=sees_config.runtime,
            scenario_config=sees_config.scenario,
            kernel_factory=kernel_factory,  # type: ignore[arg-type]
            snapshot_interval_events=config.state_snapshot_interval_events,
            deterministic_replay=False,
            control_step_seconds=1.0,
        )
        session.initialize()
        self._session = session
        self._runtime_adapter = SimulationController(session)
        self._advance_loop = SessionAdvanceLoop(
            session,
            stream_policy=StreamBackpressurePolicy(
                max_items=100_000,
                max_batch_size=100_000,
            ),
            tick_interval_seconds=0.01,
            max_sim_delta_per_tick=1.0,
        )

    def advance_loop_snapshot(self) -> dict[str, Any]:
        return self._require_advance_loop().snapshot().to_dict()

    def runtime_lifecycle_state(self) -> RuntimeLifecycleState:
        return self._require_session().lifecycle_state

    def _live_stream_active(self) -> bool:
        return (
            self._initialized
            and self._require_session().lifecycle_state == RuntimeLifecycleState.RUNNING
        )

    def _stop_advance_loop(self) -> None:
        if self._advance_loop is not None:
            self._advance_loop.stop()

    def _generated_config_json(self) -> dict[str, Any]:
        builder_config = scenario_builder_config_from_sees_config(self._controller.config)
        generated = scenario_builder_config_to_mapping(builder_config)
        backend_summary = scenario_builder_backend_summary(builder_config)
        backend_summary["fidelity_summary"] = _fidelity_summary_from_sees_config(
            self._controller.config
        )
        backend_summary["configuration_surface_summary"] = build_user_configuration_view(
            self._controller.config
        )
        generated["backend_summary"] = backend_summary
        return generated

    def _status_json(
        self,
        generated_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        runtime_status = self._require_session().get_status().to_dict()
        status = dict(runtime_status)
        status.update(self._controller.snapshot().to_json())
        status["lifecycle_state"] = runtime_status["lifecycle_state"]
        status["current_sim_time"] = runtime_status["current_sim_time"]
        status["wall_clock_start_time"] = runtime_status["wall_clock_start_time"]
        status["processed_event_count"] = runtime_status["processed_event_count"]
        status["queued_event_count"] = runtime_status["queued_event_count"]
        status["last_error"] = runtime_status["last_error"]
        status["deterministic_replay"] = runtime_status["deterministic_replay"]
        if runtime_status["lifecycle_state"] in {"COMPLETED", "ERROR"}:
            status["status"] = runtime_status["status"]
        status["initialized"] = self._initialized
        status["fidelity_summary"] = _fidelity_summary_from_sees_config(
            self._controller.config
        )
        status["configuration_surface_summary"] = build_user_configuration_view(
            self._controller.config
        )
        metrics_summary = self._metrics_summary_json()
        status["metrics_summary"] = metrics_summary
        status["network_quality_provenance_v1"] = _network_quality_provenance_from_metrics(
            metrics_summary
        )
        network_kpi_provenance_v2 = build_network_kpi_provenance_v2(metrics_summary)
        status["network_kpi_provenance_v2"] = network_kpi_provenance_v2
        status["network_kpi_credibility_v1"] = build_network_kpi_credibility_v1(
            network_kpi_provenance_v2
        )
        status["kpi_time_series_v1"] = self._kpi_time_series_json()
        status["satellite_kpi_slices_v1"] = self._satellite_kpi_slices_json()
        status["satellite_kpi_history_v1"] = self._satellite_kpi_history_json()
        status["service_latency_history_v1"] = self._service_latency_history_json()
        lifecycle_summaries = build_runtime_lifecycle_summaries(
            self.visible_snapshot(),
            service_latency_history=status["service_latency_history_v1"],
            satellite_kpi_slices=status["satellite_kpi_slices_v1"],
        )
        status.update(lifecycle_summaries)
        status["user_request_history_v1"] = self._user_request_history_json(
            lifecycle_summaries["user_request_summary_v1"],
            float(status["current_sim_time"]),
        )
        status["stream_diagnostics_v1"] = self._stream_diagnostics_json()
        status["reproducibility_manifest_v1"] = (
            build_runtime_reproducibility_manifest(
                session_id=self._require_session().session_id,
                runtime_status=status,
                control_config=self._controller.config_json(),
                generated_config=(
                    generated_config
                    if generated_config is not None
                    else self._generated_config_json()
                ),
                metrics_summary=metrics_summary,
            )
        )
        status["runtime_export_history_v1"] = self._runtime_export_history_json()
        return status

    def _runtime_export_status_json(self, status: dict[str, Any]) -> dict[str, Any]:
        export_status = _runtime_export_status_snapshot(status)
        route_summary = self._runtime_export_route_explanation_summary()
        export_status["route_explanation_summary_v1"] = route_summary
        export_status["route_provenance_trust_summary_v1"] = (
            build_runtime_route_provenance_trust_summary(route_summary)
        )
        export_status["runtime_export_route_detail_policy_v1"] = {
            "version": "v1",
            "source": "BACKEND_RUNTIME_EXPORT",
            "policy": "EXPORT_ROUTE_DETAIL_INDEX_WINDOW",
            "route_summary_source": "visible_snapshot.routes",
            "route_detail_limit": _RUNTIME_EXPORT_ROUTE_DETAIL_LIMIT,
            "route_count": route_summary["route_count"],
            "indexed_route_count": route_summary["item_count"],
            "hidden_route_count": max(
                0,
                int(route_summary["route_count"]) - int(route_summary["item_count"]),
            ),
            "packet_level_simulation": False,
            "all_pairs_computation": False,
        }
        service_trace_summary = self._runtime_export_service_lifecycle_trace_summary()
        export_status["service_lifecycle_trace_v2"] = service_trace_summary
        export_status["runtime_export_service_trace_policy_v1"] = {
            "version": "v1",
            "source": "BACKEND_RUNTIME_EXPORT",
            "policy": "EXPORT_SERVICE_TRACE_WINDOW",
            "service_trace_source": "service_latency_history_v1",
            "service_trace_limit": _RUNTIME_EXPORT_SERVICE_TRACE_LIMIT,
            "service_count": service_trace_summary["service_count"],
            "exported_trace_count": service_trace_summary["trace_count"],
            "hidden_trace_count": service_trace_summary["hidden_trace_count"],
            "artifact_window_only": True,
            "event_replay": False,
            "service_recomputation": False,
            "packet_level_simulation": False,
        }
        manifest = _runtime_export_manifest_with_boundary(export_status)
        export_status["reproducibility_manifest_v1"] = manifest
        export_status["runtime_export_reproducibility_boundary_v1"] = manifest[
            "runtime_export_reproducibility_boundary_v1"
        ]
        return export_status

    def _runtime_export_route_explanation_summary(self) -> dict[str, Any]:
        return build_runtime_route_explanation_summary(
            self.visible_snapshot(),
            service_latency_history=self._service_latency_history_json(),
            cursor=0,
            limit=_RUNTIME_EXPORT_ROUTE_DETAIL_LIMIT,
        )

    def _runtime_export_service_lifecycle_trace_summary(self) -> dict[str, Any]:
        return build_runtime_service_lifecycle_trace_v2(
            self._service_latency_history_json(),
            cursor=0,
            limit=_RUNTIME_EXPORT_SERVICE_TRACE_LIMIT,
        )

    def _ack(self, command: ControlCommand) -> dict[str, Any]:
        return self._ack_for_command_name(command.command.value)

    def _ack_for_command_name(self, command_name: str) -> dict[str, Any]:
        generated_config = self._generated_config_json()
        return {
            "type": "CONTROL_ACK",
            "ok": True,
            "command": command_name,
            "status": self._status_json(generated_config),
            "config": self._controller.config_json(),
            "generated_config": generated_config,
        }

    def _metrics_summary_json(self) -> dict[str, Any]:
        if self._runtime_context is not None:
            return dict(self._runtime_context.metrics.summary())
        return dict(self._result.metrics_summary)

    def _kpi_time_series_json(self) -> dict[str, Any]:
        if self._runtime_context is None:
            return {
                "version": "v1",
                "sample_count": 0,
                "tail_sample_source": "NO_RUNTIME_SESSION",
                "tail_sample_source_label": "等待运行时指标",
                "samples": (),
            }
        current_sim_time = self._require_session().get_status().current_sim_time
        return dict(self._runtime_context.metrics.kpi_time_series(sim_time=current_sim_time))

    def _satellite_kpi_slices_json(self) -> dict[str, Any]:
        if self._runtime_context is None:
            return {
                "version": "v1",
                "mode": "TOP_ACTIVITY_LIMITED",
                "slice_limit": 64,
                "satellite_count": 0,
                "slice_count": 0,
                "slices": (),
            }
        return dict(self._runtime_context.metrics.satellite_kpi_slices())

    def _satellite_kpi_history_json(self) -> dict[str, Any]:
        if self._runtime_context is None:
            return {
                "version": "v1",
                "mode": "RECENT_COMPUTE_LIMITED",
                "slice_limit": 64,
                "sample_limit": 32,
                "satellite_count": 0,
                "series_count": 0,
                "series": (),
            }
        return dict(self._runtime_context.metrics.satellite_kpi_history())

    def _service_latency_history_json(self) -> dict[str, Any]:
        if self._runtime_context is None:
            return {
                "version": "v1",
                "mode": "RECENT_SERVICE_LIMITED",
                "service_count": 0,
                "service_limit": 32,
                "item_count": 0,
                "items": (),
            }
        return dict(self._runtime_context.metrics.service_latency_history())

    def _user_request_history_json(
        self,
        user_summary: object,
        sim_time: float,
    ) -> dict[str, Any]:
        if isinstance(user_summary, dict):
            self._append_user_request_history(user_summary, sim_time)
        user_ids = sorted(self._user_request_history, key=_control_entity_sort_key)
        series_items: list[dict[str, object]] = []
        for user_id in user_ids:
            samples = tuple(
                self._user_request_history[user_id][-self._user_request_history_limit :]
            )
            series_items.append(
                {
                    "user_id": user_id,
                    "sample_count": len(samples),
                    "samples": samples,
                }
            )
        series = tuple(series_items)
        summary_user_count = 0
        summary_item_count = 0
        hidden_user_count = 0
        if isinstance(user_summary, dict):
            summary_user_count = _control_int(user_summary.get("user_count"))
            summary_item_count = _control_int(user_summary.get("item_count"))
            hidden_user_count = _control_int(user_summary.get("hidden_user_count"))
        return {
            "version": "v1",
            "mode": "RECENT_USER_REQUEST_LIMITED",
            "source": "BACKEND_RUNTIME_STATUS",
            "history_scope": "STATUS_POLL_SAMPLED_VISIBLE_USERS",
            "sample_policy": "ONE_SAMPLE_PER_RUNTIME_STATUS_PER_VISIBLE_USER",
            "sample_limit": self._user_request_history_limit,
            "user_count": summary_user_count or len(self._user_request_history),
            "summary_item_count": summary_item_count,
            "hidden_user_count": hidden_user_count,
            "history_user_count": len(self._user_request_history),
            "series_count": len(series),
            "series": series,
        }

    def _append_user_request_history(
        self,
        user_summary: dict[str, Any],
        sim_time: float,
    ) -> None:
        for item in _control_records(user_summary.get("items")):
            user_id = _control_string(item.get("user_id"))
            if not user_id:
                continue
            sample = {
                "sim_time": sim_time,
                "communication_route_count": _control_int(
                    item.get("communication_route_count")
                ),
                "available_route_count": _control_int(item.get("available_route_count")),
                "compute_service_count": _control_int(item.get("compute_service_count")),
                "network_queue_count": _control_int(item.get("network_queue_count")),
                "selected_satellite_id": _control_string(
                    item.get("selected_satellite_id")
                ),
                "destination_id": _control_string(item.get("destination_id")),
                "status": _control_string(item.get("status")),
                "primary_route_id": _control_string(item.get("primary_route_id")),
                "primary_flow_id": _control_string(item.get("primary_flow_id")),
                "latency_s": _control_optional_float(item.get("latency_s")),
                "capacity_mbps": _control_optional_float(item.get("capacity_mbps")),
                "loss_proxy_rate": _control_optional_float(item.get("loss_proxy_rate")),
                "service_state": _control_string(item.get("service_state")),
                "active_business_type": _control_string(
                    item.get("active_business_type")
                ),
                "active_business_label": _control_string(
                    item.get("active_business_label")
                ),
                "request_state": _control_string(item.get("request_state")),
            }
            history = self._user_request_history.setdefault(user_id, [])
            if history and history[-1]["sim_time"] == sim_time:
                history[-1] = sample
            else:
                history.append(sample)
            del history[: max(0, len(history) - self._user_request_history_limit)]

    def _stream_diagnostics_json(self) -> dict[str, Any]:
        loop = self._require_advance_loop()
        snapshot = loop.snapshot()
        return {
            "version": "v1",
            "advance_loop_state": snapshot.state.value,
            "tick_count": snapshot.tick_count,
            "event_stream": _stream_buffer_diagnostics(
                name="events",
                stream=loop.event_stream,
            ),
            "state_stream": _stream_buffer_diagnostics(
                name="state",
                stream=loop.snapshot_stream,
            ),
        }

    def _record_runtime_export(
        self,
        export_type: str,
        package: dict[str, Any],
    ) -> dict[str, Any]:
        self._export_sequence += 1
        status = self._require_session().get_status().to_dict()
        manifest = package.get("manifest", {})
        archive = package.get("archive")
        record: dict[str, Any] = {
            "sequence": self._export_sequence,
            "export_type": export_type,
            "package_id": str(package.get("package_id", "")),
            "package_dir": str(package.get("package_dir", "")),
            "file_count": _control_int(package.get("file_count")),
            "manifest_hash": (
                str(manifest.get("manifest_hash", ""))
                if isinstance(manifest, dict)
                else ""
            ),
            "current_sim_time": _control_optional_float(
                status.get("current_sim_time"),
            )
            or 0.0,
            "processed_event_count": _control_int(
                status.get("processed_event_count"),
            ),
        }
        if isinstance(archive, dict):
            record.update(
                {
                    "archive_filename": str(archive.get("filename", "")),
                    "archive_sha256": str(archive.get("sha256", "")),
                    "archive_bytes": _control_int(archive.get("bytes")),
                }
            )
        self._export_history.append(record)
        del self._export_history[: max(0, len(self._export_history) - self._export_history_limit)]
        return dict(record)

    def _runtime_export_history_json(self) -> dict[str, Any]:
        items = tuple(dict(item) for item in self._export_history)
        latest = dict(items[-1]) if items else None
        return {
            "version": "v1",
            "source": "BACKEND_RUNTIME_STATUS",
            "history_scope": "CURRENT_SESSION_RECENT_EXPORTS",
            "history_limit": self._export_history_limit,
            "export_count": self._export_sequence,
            "retained_count": len(items),
            "latest_export": latest,
            "items": items,
        }

    def _nack(self, command: str, error: str) -> dict[str, Any]:
        return {
            "type": "CONTROL_ACK",
            "ok": False,
            "command": command,
            "status": self._status_json(),
            "error": error,
        }

    def _require_session(self) -> SimulationSession:
        if self._session is None:
            raise RuntimeError("runtime session is not installed")
        return self._session

    def _require_runtime_adapter(self) -> SimulationController:
        if self._runtime_adapter is None:
            raise RuntimeError("runtime adapter is not installed")
        return self._runtime_adapter

    def _require_advance_loop(self) -> SessionAdvanceLoop:
        if self._advance_loop is None:
            raise RuntimeError("runtime advance loop is not installed")
        return self._advance_loop

    def _runtime_export_package_config_snapshot(
        self,
        package_id: str,
        output_root: str | Path,
    ) -> dict[str, Any]:
        artifact = self.runtime_export_package_artifact(
            package_id,
            "config_snapshot.json",
            output_root,
        )
        package_snapshot = json.loads(
            Path(str(artifact["path"])).read_text(encoding="utf-8")
        )
        if not isinstance(package_snapshot, dict):
            raise RuntimeExportArtifactError(
                f"runtime export package {package_id!r} has invalid config snapshot"
            )
        return package_snapshot

    def _runtime_export_package_route_detail_index(
        self,
        package_id: str,
        output_root: str | Path,
    ) -> dict[str, Any]:
        artifact = self.runtime_export_package_artifact(
            package_id,
            _RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_FILENAME,
            output_root,
        )
        route_detail_index = json.loads(
            Path(str(artifact["path"])).read_text(encoding="utf-8")
        )
        if not isinstance(route_detail_index, dict):
            raise RuntimeExportArtifactError(
                f"runtime export package {package_id!r} has invalid route detail index"
            )
        return route_detail_index

    def _runtime_export_package_service_trace_export(
        self,
        package_id: str,
        output_root: str | Path,
    ) -> dict[str, Any]:
        artifact = self.runtime_export_package_artifact(
            package_id,
            _SERVICE_LIFECYCLE_TRACE_EXPORT_FILENAME,
            output_root,
        )
        service_trace_export = json.loads(
            Path(str(artifact["path"])).read_text(encoding="utf-8")
        )
        if not isinstance(service_trace_export, dict):
            raise RuntimeExportArtifactError(
                f"runtime export package {package_id!r} has invalid service trace export"
            )
        return service_trace_export


def _runtime_export_restore_control_payload(raw: str | bytes) -> dict[str, Any] | None:
    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    data = json.loads(text)
    if not isinstance(data, dict):
        return None
    raw_command = data.get("command", data.get("action"))
    if (
        data.get("type") != "RUNTIME_CONTROL"
        or str(raw_command) != _RUNTIME_EXPORT_RESTORE_COMMAND
    ):
        return None
    payload = data.get("payload", {})
    if not isinstance(payload, dict):
        raise RuntimeError("restore payload must be a mapping")
    return dict(payload)


def _parse_user_configuration_text(
    text: str,
    *,
    format_hint: str,
) -> tuple[Mapping[str, Any], str]:
    if not isinstance(text, str):
        raise ValueError("config text must be a UTF-8 string")
    normalized_hint = str(format_hint or "auto").strip().lower()
    if normalized_hint not in {"auto", "json", "yaml", "yml"}:
        raise ValueError("format must be one of: auto, json, yaml")
    if not text.strip():
        raise ValueError("config text must not be empty")
    if normalized_hint == "json":
        return _parse_user_configuration_json_text(text), "json"
    if normalized_hint in {"yaml", "yml"}:
        return _parse_user_configuration_yaml_text(text), "yaml"
    try:
        return _parse_user_configuration_json_text(text), "json"
    except ValueError as json_error:
        try:
            return _parse_user_configuration_yaml_text(text), "yaml"
        except ValueError as yaml_error:
            raise ValueError(
                f"config text is neither valid JSON nor supported YAML: "
                f"json={json_error}; yaml={yaml_error}"
            ) from yaml_error


def _parse_user_configuration_json_text(text: str) -> Mapping[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(str(exc)) from exc
    if not isinstance(value, Mapping):
        raise ValueError("JSON config root must be a mapping")
    return value


def _parse_user_configuration_yaml_text(text: str) -> Mapping[str, Any]:
    try:
        value = parse_simple_yaml(text)
    except ConfigValidationError as exc:
        raise ValueError(str(exc)) from exc
    if not isinstance(value, Mapping):
        raise ValueError("YAML config root must be a mapping")
    return value


def _user_configuration_apply_command() -> dict[str, Any]:
    return {
        "type": "CONFIG_UPDATE",
        "action": "CONFIG_UPDATE",
        "payload_source": "normalized_config",
        "payload_format": "SEES_CONFIG_MAPPING",
        "requires_preflight_ok": True,
        "requires_explicit_user_action": True,
        "runtime_effect": "REINITIALIZES_SESSION_AND_STREAMS",
        "runtime_status_policy": (
            "SAFE_WHEN_STOPPED_OR_UNINITIALIZED; "
            "RUNNING_SESSION_IS_STOPPED_AND_REINITIALIZED_BY_BACKEND"
        ),
    }


def _user_configuration_change_summary(
    current_config: Mapping[str, Any],
    candidate_config: Mapping[str, Any],
    *,
    preview_limit: int = 24,
) -> dict[str, Any]:
    current = _flatten_config_paths(current_config)
    candidate = _flatten_config_paths(candidate_config)
    all_paths = sorted(set(current) | set(candidate))
    changes: list[dict[str, Any]] = []
    section_counts: dict[str, int] = {}
    sentinel = object()
    for path in all_paths:
        current_value = current.get(path, sentinel)
        candidate_value = candidate.get(path, sentinel)
        if current_value == candidate_value:
            continue
        section = path.split(".", 1)[0]
        section_counts[section] = section_counts.get(section, 0) + 1
        if len(changes) >= preview_limit:
            continue
        if current_value is sentinel:
            change_type = "ADDED"
            current_json: Any = None
        else:
            change_type = "CHANGED"
            current_json = current_value
        if candidate_value is sentinel:
            change_type = "REMOVED"
            candidate_json: Any = None
        else:
            candidate_json = candidate_value
        changes.append(
            {
                "path": path,
                "section": section,
                "change_type": change_type,
                "current_value": current_json,
                "candidate_value": candidate_json,
            }
        )
    changed_field_count = sum(section_counts.values())
    return {
        "version": "v1",
        "source": "BACKEND_USER_CONFIGURATION",
        "baseline": "CURRENT_EFFECTIVE_SEES_CONFIG",
        "candidate": "NORMALIZED_USER_CONFIG",
        "changed_field_count": changed_field_count,
        "section_counts": {
            section: section_counts[section] for section in sorted(section_counts)
        },
        "preview_limit": preview_limit,
        "change_count": len(changes),
        "hidden_change_count": max(0, changed_field_count - len(changes)),
        "changes": tuple(changes),
    }


def _flatten_config_paths(data: Mapping[str, Any]) -> dict[str, Any]:
    flattened: dict[str, Any] = {}

    def walk(prefix: str, value: Any) -> None:
        if isinstance(value, Mapping):
            for key in sorted(value):
                child_path = f"{prefix}.{key}" if prefix else str(key)
                walk(child_path, value[key])
            return
        flattened[prefix] = value

    walk("", data)
    return flattened


def _user_configuration_apply_readiness(
    *,
    initialized: bool,
    controller_status: str,
    lifecycle_state: str,
) -> dict[str, Any]:
    running = lifecycle_state == RuntimeLifecycleState.RUNNING.value
    completed = lifecycle_state == RuntimeLifecycleState.COMPLETED.value
    error = lifecycle_state == RuntimeLifecycleState.ERROR.value
    session_exists = lifecycle_state != RuntimeLifecycleState.UNINITIALIZED.value
    requires_confirmation = running or completed or error
    if running:
        readiness = "APPLY_ALLOWED_WITH_RUNNING_SESSION_REINIT"
        recommended_action = "PAUSE_OR_STOP_BEFORE_APPLY"
        reason = "runtime is running; applying config will stop and rebuild the live session"
    elif completed:
        readiness = "APPLY_ALLOWED_AFTER_COMPLETION_REINIT"
        recommended_action = "APPLY_TO_START_NEW_SESSION"
        reason = "runtime is completed; applying config will create a fresh initialized session"
    elif error:
        readiness = "APPLY_ALLOWED_AFTER_ERROR_REINIT"
        recommended_action = "APPLY_TO_RECOVER_SESSION"
        reason = "runtime is in error state; applying config rebuilds the session from validated config"
    elif initialized or session_exists:
        readiness = "APPLY_ALLOWED_REINITIALIZES_SESSION"
        recommended_action = "APPLY_WHEN_READY"
        reason = "runtime session exists; applying config will rebuild the initialized session"
    else:
        readiness = "APPLY_ALLOWED_UNINITIALIZED"
        recommended_action = "APPLY_THEN_INITIALIZE"
        reason = "runtime is not initialized; applying config prepares the next session"
    return {
        "version": "v1",
        "source": "BACKEND_RUNTIME_STATUS",
        "can_apply": True,
        "readiness": readiness,
        "requires_confirmation": requires_confirmation,
        "recommended_action": recommended_action,
        "reason": reason,
        "runtime_initialized": initialized,
        "controller_status": controller_status,
        "lifecycle_state": lifecycle_state,
        "session_effect": "REINITIALIZES_SESSION",
        "stream_effect": "STOPS_AND_RECREATES_STREAM_BUFFERS",
    }


def _runtime_export_restore_result(
    package_id: str,
    preflight_summary: dict[str, Any],
    *,
    restored: bool,
    rollback_package: dict[str, Any] | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "version": "v1",
        "source": "BACKEND_RUNTIME_EXPORT_RESTORE_COMMAND",
        "package_id": package_id,
        "readiness": str(preflight_summary.get("readiness", "")),
        "restored": restored,
        "wrote_config_files": restored,
        "reset_runtime_session": restored,
        "stopped_live_streams": restored,
        "preflight_hash": str(preflight_summary.get("preflight_hash", "")),
        "restored_config_hash": str(preflight_summary.get("package_config_hash", "")),
        "previous_config_hash": str(preflight_summary.get("current_config_hash", "")),
        "rollback_package_id": "",
        "rollback_package_dir": "",
        "rollback_catalog_key": "",
    }
    if rollback_package is not None:
        result["rollback_package_id"] = str(rollback_package.get("package_id", ""))
        result["rollback_package_dir"] = str(rollback_package.get("package_dir", ""))
        catalog_record = rollback_package.get("export_catalog_record")
        if isinstance(catalog_record, dict):
            result["rollback_catalog_key"] = str(catalog_record.get("catalog_key", ""))
    result["restore_result_hash"] = stable_hash_payload(result)
    return result


def _control_records(value: object) -> tuple[dict[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item for item in value if isinstance(item, dict))


def _control_string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _control_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return 0


def _control_optional_float(value: object) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _control_entity_sort_key(value: str) -> tuple[tuple[int, object], ...]:
    return tuple(
        (0, int(token)) if token.isdigit() else (1, token)
        for token in re.split(r"(\d+)", value)
        if token
    )


def _initial_snapshot(result: DemoRunResult) -> dict[str, JsonValue]:
    return _initial_snapshot_from_ground_users(
        result.scenario.ground_user_render_states,
        fidelity_summary=_fidelity_summary_from_demo_config(result.config),
    )


def _initial_snapshot_from_ground_users(
    ground_users: tuple[Any, ...],
    satellites: tuple[SatelliteState, ...] = (),
    fidelity_summary: dict[str, object] | None = None,
) -> dict[str, JsonValue]:
    snapshot: dict[str, JsonValue] = {
        "satellites": [
            {
                "satellite_id": satellite.satellite_id,
                "sim_time": satellite.sim_time,
                "position": list(satellite.position),
                "velocity": list(satellite.velocity),
                "status": satellite.status,
            }
            for satellite in sorted(satellites, key=lambda item: item.satellite_id)
        ],
        "ground_users": [
            {
                "user_id": user.user_id,
                "cell_id": user.cell_id,
                "position": list(user.position),
                "status": user.status,
            }
            for user in sorted(ground_users, key=lambda item: item.user_id)
        ],
        "links": [],
        "routes": [],
        "tasks": [],
        "compute_nodes": [],
        "metrics": [],
        "event_count": 0,
        "last_sim_time": 0.0,
    }
    if fidelity_summary is not None:
        snapshot["fidelity_summary"] = dict(fidelity_summary)
    return snapshot


def _initial_satellite_states(
    config: DemoConfig,
    context: DemoRuntimeContext,
) -> tuple[SatelliteState, ...]:
    return KeplerianOrbitEngine(
        elements=context.scenario.orbit_elements,
        update_targets=("metrics",),
        earth_rotation_rate_rad_s=0.000072921159,
        state_vector_scale=1000.0,
        update_mode=config.orbit_update_mode,
    ).states_at(0.0)


def _frontend_event_batch(
    stream: StreamBuffer[Any],
    cursor: int,
    limit: int | None,
) -> dict[str, Any]:
    selected_limit = stream.policy.max_batch_size if limit is None else min(
        limit,
        stream.policy.max_batch_size,
    )
    if selected_limit <= 0:
        raise ValueError("limit must be positive")
    items: list[dict[str, JsonValue]] = []
    next_cursor = cursor
    overflow = False
    dropped_count = 0
    first_read = True
    while len(items) < selected_limit:
        batch = stream.read_after(next_cursor, limit=selected_limit)
        if first_read:
            overflow = batch.overflow
            dropped_count = batch.dropped_count
            first_read = False
        if batch.next_cursor == next_cursor:
            break
        next_cursor = batch.next_cursor
        for event in batch.items:
            if str(event.event_type) in _FRONTEND_EVENT_TYPES:
                items.append(event_to_json(event))
                if len(items) >= selected_limit:
                    break
        if len(batch.items) < selected_limit:
            break
    return {
        "items": items,
        "cursor": cursor,
        "next_cursor": next_cursor,
        "overflow": overflow,
        "dropped_count": dropped_count,
    }


def _stream_buffer_diagnostics(name: str, stream: StreamBuffer[Any]) -> dict[str, Any]:
    snapshot = stream.snapshot()
    return {
        "name": name,
        "next_cursor": max(0, snapshot.next_sequence - 1),
        "oldest_cursor": max(0, snapshot.oldest_sequence - 1),
        "retained_count": snapshot.retained_count,
        "total_dropped_count": snapshot.total_dropped_count,
        "max_items": stream.policy.max_items,
        "max_batch_size": stream.policy.max_batch_size,
        "overflow_risk": snapshot.total_dropped_count > 0,
    }


def _runtime_export_package_id(session_id: str, status: dict[str, Any]) -> str:
    sim_time = _control_optional_float(status.get("current_sim_time")) or 0.0
    event_count = _control_int(status.get("processed_event_count"))
    sim_token = f"{sim_time:012.3f}".replace(".", "p")
    return (
        f"{_safe_runtime_export_token(session_id)}-"
        f"t{sim_token}-e{event_count:08d}"
    )


def _safe_runtime_export_token(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return safe.strip(".-") or "runtime-session"


def _runtime_export_file_record(name: str, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "name": name,
        "filename": path.name,
        "path": str(path),
        "bytes": len(data),
        "sha256": f"sha256:{hashlib.sha256(data).hexdigest()}",
    }


def _runtime_export_status_snapshot(status: dict[str, Any]) -> dict[str, Any]:
    snapshot = dict(status)
    for key in (
        "backpressure_summary",
        "profiling_summary",
        "runtime_export_history_v1",
        "stream_diagnostics_v1",
    ):
        snapshot.pop(key, None)
    snapshot["export_status_policy"] = "STABLE_RUNTIME_STATUS_WITHOUT_STREAM_DIAGNOSTICS"
    snapshot["excluded_export_status_fields"] = (
        "backpressure_summary",
        "profiling_summary",
        "runtime_export_history_v1",
        "stream_diagnostics_v1",
    )
    return snapshot


def _runtime_export_manifest_with_boundary(status: dict[str, Any]) -> dict[str, Any]:
    raw_manifest = status.get("reproducibility_manifest_v1")
    manifest = dict(raw_manifest) if isinstance(raw_manifest, dict) else {}
    manifest.pop("manifest_hash", None)
    boundary = build_runtime_export_reproducibility_boundary_v1(
        runtime_status=status,
        manifest=manifest,
    )
    manifest["runtime_export_reproducibility_boundary_v1"] = stable_json_payload(
        boundary
    )
    manifest["manifest_hash"] = stable_hash_payload(manifest)
    payload = stable_json_payload(manifest)
    return dict(payload) if isinstance(payload, dict) else {}


def _runtime_service_lifecycle_trace_export(status: dict[str, Any]) -> dict[str, Any]:
    trace = status.get("service_lifecycle_trace_v2")
    if not isinstance(trace, dict):
        trace = {
            "version": "v2",
            "source": "SERVICE_LATENCY_HISTORY",
            "summary_scope": "SERVICE_LIFECYCLE_TRACE_WINDOW",
            "service_count": 0,
            "trace_count": 0,
            "items": (),
        }
    policy = status.get("runtime_export_service_trace_policy_v1")
    if not isinstance(policy, dict):
        policy = {
            "version": "v1",
            "source": "BACKEND_RUNTIME_EXPORT",
            "policy": "EXPORT_SERVICE_TRACE_WINDOW",
            "service_trace_source": "service_latency_history_v1",
            "service_trace_limit": 0,
            "service_count": int(trace.get("service_count", 0)),
            "exported_trace_count": int(trace.get("trace_count", 0)),
            "hidden_trace_count": int(trace.get("hidden_trace_count", 0)),
            "artifact_window_only": True,
            "event_replay": False,
            "service_recomputation": False,
            "packet_level_simulation": False,
        }
    return {
        "type": "SERVICE_LIFECYCLE_TRACE_EXPORT_V2",
        "source": "BACKEND_RUNTIME_STATUS",
        "artifact_policy": "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
        "service_trace_export_policy": policy,
        "summary": trace,
    }


def _write_runtime_export_archive(package_dir: Path, archive_path: Path) -> None:
    entries = tuple(
        path
        for path in sorted(package_dir.iterdir(), key=lambda item: item.name)
        if path.is_file() and path != archive_path
    )
    with zipfile.ZipFile(
        archive_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in entries:
            info = zipfile.ZipInfo(path.name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())


def _write_runtime_export_catalog(
    output_root: str | Path,
    export_type: str,
    package: dict[str, Any],
) -> dict[str, Any]:
    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    catalog_path = root / _RUNTIME_EXPORT_CATALOG_FILENAME
    existing = _read_runtime_export_catalog(root)
    record = _runtime_export_catalog_record(root, export_type, package)
    records = {
        str(item.get("catalog_key", "")): dict(item)
        for item in _control_records(existing.get("records"))
        if item.get("catalog_key")
    }
    records[record["catalog_key"]] = record
    catalog = _runtime_export_catalog_document(
        root,
        catalog_path,
        tuple(records[key] for key in sorted(records)),
        record,
    )
    catalog_path.write_text(stable_json_pretty(catalog), encoding="utf-8")
    return catalog


def _read_runtime_export_catalog(output_root: str | Path) -> dict[str, Any]:
    root = Path(output_root)
    catalog_path = root / _RUNTIME_EXPORT_CATALOG_FILENAME
    if not catalog_path.exists():
        return _runtime_export_catalog_document(root, catalog_path, (), None)
    loaded = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return _runtime_export_catalog_document(root, catalog_path, (), None)
    records = tuple(
        dict(record)
        for record in _control_records(loaded.get("records"))
        if record.get("catalog_key")
    )
    latest = loaded.get("latest_export")
    latest_record = dict(latest) if isinstance(latest, dict) else None
    return _runtime_export_catalog_document(
        root,
        catalog_path,
        tuple(sorted(records, key=lambda item: str(item["catalog_key"]))),
        latest_record,
    )


def _upsert_runtime_export_catalog_file(
    output_root: str | Path,
    package_id: str,
    file_record: dict[str, Any],
) -> dict[str, Any]:
    root = Path(output_root)
    catalog_path = root / _RUNTIME_EXPORT_CATALOG_FILENAME
    existing = _read_runtime_export_catalog(root)
    records = tuple(
        _runtime_export_catalog_record_with_file(record, package_id, file_record)
        for record in _control_records(existing.get("records"))
        if record.get("catalog_key")
    )
    latest = existing.get("latest_export")
    latest_record = (
        _runtime_export_catalog_record_with_file(latest, package_id, file_record)
        if isinstance(latest, dict)
        else None
    )
    catalog = _runtime_export_catalog_document(
        root,
        catalog_path,
        tuple(sorted(records, key=lambda item: str(item["catalog_key"]))),
        latest_record,
    )
    catalog_path.write_text(stable_json_pretty(catalog), encoding="utf-8")
    return _runtime_export_catalog_package_record(catalog, package_id)


def _runtime_export_catalog_record_with_file(
    record: dict[str, Any],
    package_id: str,
    file_record: dict[str, Any],
) -> dict[str, Any]:
    updated = dict(record)
    if str(updated.get("package_id", "")) != str(package_id):
        return updated
    catalog_file = _runtime_export_catalog_file_record(file_record)
    files = {
        str(item.get("filename", "")): _runtime_export_catalog_file_record(item)
        for item in _control_records(updated.get("files"))
        if item.get("filename")
    }
    files[str(catalog_file["filename"])] = catalog_file
    updated["files"] = tuple(files[key] for key in sorted(files))
    updated["file_count"] = len(files)
    return updated


def _runtime_export_catalog_document(
    root: Path,
    catalog_path: Path,
    records: tuple[dict[str, Any], ...],
    latest_record: dict[str, Any] | None,
) -> dict[str, Any]:
    records_payload = stable_json_payload(records)
    latest_payload = (
        None if latest_record is None else stable_json_payload(latest_record)
    )
    document: dict[str, Any] = {
        "version": "v1",
        "source": "BACKEND_RUNTIME_EXPORT",
        "catalog_scope": "RUNTIME_EXPORT_ROOT",
        "catalog_file": str(catalog_path),
        "export_root": str(root),
        "record_count": len(records),
        "latest_export": latest_payload,
        "records": records_payload,
    }
    document["catalog_hash"] = stable_hash_payload(document)
    return document


def _runtime_export_catalog_record(
    root: Path,
    export_type: str,
    package: dict[str, Any],
) -> dict[str, Any]:
    package_id = str(package.get("package_id", ""))
    package_dir = Path(str(package.get("package_dir", "")))
    manifest = package.get("manifest", {})
    archive = package.get("archive")
    record: dict[str, Any] = {
        "catalog_key": f"{export_type}:{package_id}",
        "export_type": export_type,
        "package_id": package_id,
        "package_dir": str(package_dir),
        "relative_package_dir": _relative_runtime_export_path(root, package_dir),
        "file_count": _control_int(package.get("file_count")),
        "manifest_hash": (
            str(manifest.get("manifest_hash", ""))
            if isinstance(manifest, dict)
            else ""
        ),
        "current_sim_time": _control_optional_float(
            _runtime_export_manifest_state_value(manifest, "current_sim_time"),
        )
        or 0.0,
        "processed_event_count": _control_int(
            _runtime_export_manifest_state_value(manifest, "processed_event_count"),
        ),
        "files": tuple(
            _runtime_export_catalog_file_record(file_record)
            for file_record in _control_records(package.get("files"))
        ),
    }
    if isinstance(archive, dict):
        record.update(
            {
                "archive_filename": str(archive.get("filename", "")),
                "archive_sha256": str(archive.get("sha256", "")),
                "archive_bytes": _control_int(archive.get("bytes")),
            }
        )
    return record


def _runtime_export_catalog_file_record(file_record: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": str(file_record.get("name", "")),
        "filename": str(file_record.get("filename", "")),
        "bytes": _control_int(file_record.get("bytes")),
        "sha256": str(file_record.get("sha256", "")),
    }


def _runtime_export_catalog_package_record(
    catalog: dict[str, Any],
    package_id: str,
) -> dict[str, Any]:
    normalized_package_id = str(package_id)
    if not normalized_package_id:
        raise RuntimeExportArtifactError("runtime export package id is required")
    matches = tuple(
        dict(record)
        for record in _control_records(catalog.get("records"))
        if str(record.get("package_id", "")) == normalized_package_id
    )
    if not matches:
        raise RuntimeExportArtifactError(
            f"runtime export package {normalized_package_id!r} was not found"
        )
    return sorted(
        matches,
        key=lambda record: (
            0 if str(record.get("export_type", "")) == "ARCHIVE" else 1,
            str(record.get("catalog_key", "")),
        ),
    )[0]


def _runtime_export_catalog_file(
    record: dict[str, Any],
    filename: str,
) -> dict[str, Any]:
    normalized_filename = str(filename)
    if (
        not normalized_filename
        or "/" in normalized_filename
        or "\\" in normalized_filename
    ):
        raise RuntimeExportArtifactError(
            f"runtime export artifact filename {normalized_filename!r} is invalid"
        )
    for file_record in _control_records(record.get("files")):
        if str(file_record.get("filename", "")) == normalized_filename:
            return _runtime_export_catalog_file_record(file_record)
    raise RuntimeExportArtifactError(
        f"runtime export artifact {normalized_filename!r} was not found"
    )


def _runtime_export_catalog_file_path(
    output_root: str | Path,
    record: dict[str, Any],
    file_record: dict[str, Any],
) -> Path:
    package_dir = _runtime_export_catalog_package_dir(output_root, record)
    return _runtime_export_safe_child_file(package_dir, str(file_record["filename"]))


def _runtime_export_catalog_package_dir(
    output_root: str | Path,
    record: dict[str, Any],
) -> Path:
    root = Path(output_root).resolve()
    relative = str(record.get("relative_package_dir", ""))
    if not relative:
        raise RuntimeExportArtifactError("runtime export record has no package directory")
    package_dir = (root / relative).resolve()
    if package_dir != root and root not in package_dir.parents:
        raise RuntimeExportArtifactError("runtime export package path escapes export root")
    if not package_dir.is_dir():
        raise RuntimeExportArtifactError(
            f"runtime export package directory {package_dir} was not found"
        )
    return package_dir


def _runtime_export_safe_child_file(package_dir: Path, filename: str) -> Path:
    if not filename or "/" in filename or "\\" in filename:
        raise RuntimeExportArtifactError(
            f"runtime export artifact filename {filename!r} is invalid"
        )
    root = package_dir.resolve()
    path = (root / filename).resolve()
    if path.parent != root:
        raise RuntimeExportArtifactError("runtime export artifact path escapes package")
    if not path.is_file():
        raise RuntimeExportArtifactError(
            f"runtime export artifact {filename!r} was not found"
        )
    return path


def _runtime_export_content_type(filename: str) -> str:
    if filename.endswith(".json"):
        return "application/json; charset=utf-8"
    if filename.endswith(".jsonl"):
        return "application/x-ndjson; charset=utf-8"
    if filename.endswith(".csv"):
        return "text/csv; charset=utf-8"
    if filename.endswith(".md"):
        return "text/markdown; charset=utf-8"
    if filename.endswith(".zip"):
        return "application/zip"
    return "application/octet-stream"


_RUNTIME_EXPORT_BOUNDARY_ALIGNMENT_V1_ID = (
    "leo_twin.runtime_export_boundary_alignment.v1"
)
_RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID = (
    "leo_twin.runtime_export_reproducibility_boundary.v1"
)


def _runtime_export_snapshot_boundary(snapshot: dict[str, Any]) -> dict[str, Any]:
    status = snapshot.get("status")
    if not isinstance(status, dict):
        return {}
    direct_boundary = status.get("runtime_export_reproducibility_boundary_v1")
    if isinstance(direct_boundary, dict):
        return dict(direct_boundary)
    manifest = status.get("reproducibility_manifest_v1")
    if isinstance(manifest, dict):
        manifest_boundary = manifest.get("runtime_export_reproducibility_boundary_v1")
        if isinstance(manifest_boundary, dict):
            return dict(manifest_boundary)
    return {}


def _runtime_export_boundary_flag(value: object) -> bool:
    return value is True


def _runtime_export_boundary_alignment_summary(
    package_id: str,
    package_snapshot: dict[str, Any],
    current_snapshot: dict[str, Any],
    *,
    source: str,
    compare: dict[str, Any] | None = None,
    preflight: dict[str, Any] | None = None,
) -> dict[str, Any]:
    package_boundary = _runtime_export_snapshot_boundary(package_snapshot)
    current_boundary = _runtime_export_snapshot_boundary(current_snapshot)
    package_boundary_present = bool(package_boundary)
    current_boundary_present = bool(current_boundary)
    boundary_hash = str(package_boundary.get("boundary_hash", ""))
    current_boundary_hash = str(current_boundary.get("boundary_hash", ""))
    compare_scope = str(
        compare.get("comparison_scope", "") if compare is not None else ""
    )
    preflight_scope = str(
        preflight.get("preflight_scope", "") if preflight is not None else ""
    )
    restore_scope = str(package_boundary.get("restore_scope", ""))
    boundary_compare_scope = str(package_boundary.get("compare_scope", ""))
    read_scope = str(package_boundary.get("read_scope", ""))
    forbidden_flags = (
        "event_replay_restore",
        "live_event_replay_restore",
        "recompute_on_read",
        "route_recomputation",
        "service_recomputation",
        "package_mutation_on_read",
        "packet_capture",
        "packet_level_simulation",
        "external_simulators",
    )
    forbidden_behavior_inactive = not any(
        _runtime_export_boundary_flag(package_boundary.get(flag))
        for flag in forbidden_flags
    )
    warnings: list[str] = []
    if not package_boundary_present:
        warnings.append("PACKAGE_RUNTIME_EXPORT_BOUNDARY_MISSING")
    elif (
        str(package_boundary.get("boundary_id", ""))
        != _RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID
    ):
        warnings.append("PACKAGE_RUNTIME_EXPORT_BOUNDARY_ID_UNEXPECTED")
    if (
        current_boundary_present
        and boundary_hash
        and current_boundary_hash
        and boundary_hash != current_boundary_hash
    ):
        warnings.append("CURRENT_RUNTIME_EXPORT_BOUNDARY_HASH_DIFFERS")
    if restore_scope and restore_scope != "CONFIG_ONLY":
        warnings.append("RESTORE_SCOPE_NOT_CONFIG_ONLY")
    if (
        boundary_compare_scope
        and boundary_compare_scope != "CONFIG_AND_GENERATED_CONFIG"
    ):
        warnings.append("BOUNDARY_COMPARE_SCOPE_NOT_CONFIG_AND_GENERATED_CONFIG")
    if read_scope and read_scope != "PERSISTED_ARTIFACTS_ONLY":
        warnings.append("READ_SCOPE_NOT_PERSISTED_ARTIFACTS_ONLY")
    if compare is not None:
        if str(compare.get("package_id", "")) != package_id:
            warnings.append("COMPARE_PACKAGE_ID_MISMATCH")
        if compare_scope != boundary_compare_scope:
            warnings.append("COMPARE_SCOPE_DOES_NOT_MATCH_BOUNDARY")
    if preflight is not None:
        if str(preflight.get("package_id", "")) != package_id:
            warnings.append("PREFLIGHT_PACKAGE_ID_MISMATCH")
        if preflight_scope != "CONFIG_RESTORE_PREVIEW_ONLY":
            warnings.append("PREFLIGHT_SCOPE_NOT_CONFIG_RESTORE_PREVIEW_ONLY")
        if _runtime_export_boundary_flag(
            preflight.get("would_mutate_current_runtime")
        ):
            warnings.append("PREFLIGHT_PREVIEW_WOULD_MUTATE_CURRENT_RUNTIME")
    if not forbidden_behavior_inactive:
        warnings.append("FORBIDDEN_BOUNDARY_BEHAVIOR_ENABLED")

    alignment: dict[str, Any] = {
        "type": "RUNTIME_EXPORT_BOUNDARY_ALIGNMENT_V1",
        "version": "v1",
        "alignment_id": _RUNTIME_EXPORT_BOUNDARY_ALIGNMENT_V1_ID,
        "source": source,
        "alignment_scope": "PACKAGE_COMPARE_AND_RESTORE_BOUNDARY",
        "package_id": package_id,
        "package_boundary_present": package_boundary_present,
        "current_boundary_present": current_boundary_present,
        "boundary_hash": boundary_hash,
        "current_boundary_hash": current_boundary_hash,
        "boundary_hash_matches_current": (
            current_boundary_present
            and bool(boundary_hash)
            and boundary_hash == current_boundary_hash
        ),
        "boundary_id_aligned": (
            str(package_boundary.get("boundary_id", ""))
            == _RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID
        ),
        "restore_scope": restore_scope,
        "compare_scope": boundary_compare_scope,
        "read_scope": read_scope,
        "preflight_scope": preflight_scope,
        "compare_scope_aligned": (
            compare is None or compare_scope == boundary_compare_scope
        ),
        "restore_scope_aligned": restore_scope == "CONFIG_ONLY",
        "read_scope_aligned": read_scope == "PERSISTED_ARTIFACTS_ONLY",
        "preflight_scope_aligned": (
            preflight is None or preflight_scope == "CONFIG_RESTORE_PREVIEW_ONLY"
        ),
        "forbidden_behavior_inactive": forbidden_behavior_inactive,
        "event_replay_restore": _runtime_export_boundary_flag(
            package_boundary.get("event_replay_restore")
        ),
        "live_event_replay_restore": _runtime_export_boundary_flag(
            package_boundary.get("live_event_replay_restore")
        ),
        "recompute_on_read": _runtime_export_boundary_flag(
            package_boundary.get("recompute_on_read")
        ),
        "route_recomputation": _runtime_export_boundary_flag(
            package_boundary.get("route_recomputation")
        ),
        "service_recomputation": _runtime_export_boundary_flag(
            package_boundary.get("service_recomputation")
        ),
        "package_mutation_on_read": _runtime_export_boundary_flag(
            package_boundary.get("package_mutation_on_read")
        ),
        "packet_capture": _runtime_export_boundary_flag(
            package_boundary.get("packet_capture")
        ),
        "packet_level_simulation": _runtime_export_boundary_flag(
            package_boundary.get("packet_level_simulation")
        ),
        "external_simulators": _runtime_export_boundary_flag(
            package_boundary.get("external_simulators")
        ),
        "alignment_status": (
            "ALIGNED" if package_boundary_present and not warnings else "WARN"
        ),
        "warnings": tuple(warnings),
    }
    alignment["alignment_hash"] = stable_hash_payload(alignment)
    return alignment


def _runtime_export_package_compare_summary(
    package_id: str,
    package_snapshot: dict[str, Any],
    current_snapshot: dict[str, Any],
    *,
    diff_limit: int,
) -> dict[str, Any]:
    sections = ("config", "generated_config")
    section_summaries: list[dict[str, Any]] = []
    differences: list[dict[str, Any]] = []
    for section in sections:
        section_differences = _runtime_export_section_differences(
            section,
            package_snapshot.get(section),
            current_snapshot.get(section),
        )
        section_summaries.append(
            {
                "section": section,
                "diff_count": len(section_differences),
                "matches": len(section_differences) == 0,
            }
        )
        differences.extend(section_differences)
    differences = sorted(
        differences,
        key=lambda item: (str(item["section"]), str(item["path"])),
    )
    normalized_limit = max(0, diff_limit)
    limited_differences = tuple(differences[:normalized_limit])
    package_manifest_hash = _runtime_export_snapshot_manifest_hash(package_snapshot)
    current_manifest_hash = _runtime_export_snapshot_manifest_hash(current_snapshot)
    summary: dict[str, Any] = {
        "version": "v1",
        "source": "BACKEND_RUNTIME_EXPORT_COMPARE",
        "comparison_scope": "CONFIG_AND_GENERATED_CONFIG",
        "package_id": package_id,
        "compatibility": "MATCH" if not differences else "DIFFERENT",
        "same_config": section_summaries[0]["matches"],
        "same_generated_config": section_summaries[1]["matches"],
        "same_manifest_hash": (
            bool(package_manifest_hash)
            and package_manifest_hash == current_manifest_hash
        ),
        "package_manifest_hash": package_manifest_hash,
        "current_manifest_hash": current_manifest_hash,
        "diff_count": len(differences),
        "diff_limit": normalized_limit,
        "diff_truncated": len(differences) > normalized_limit,
        "sections": tuple(section_summaries),
        "differences": stable_json_payload(limited_differences),
    }
    summary["runtime_export_boundary_alignment_v1"] = (
        _runtime_export_boundary_alignment_summary(
            package_id,
            package_snapshot,
            current_snapshot,
            source="BACKEND_RUNTIME_EXPORT_COMPARE",
            compare=summary,
        )
    )
    summary["compare_hash"] = stable_hash_payload(summary)
    return summary


def _runtime_export_package_restore_preflight_summary(
    package_id: str,
    package_snapshot: dict[str, Any],
    current_snapshot: dict[str, Any],
    compare: dict[str, Any],
    *,
    lifecycle_state: str,
) -> dict[str, Any]:
    package_config = package_snapshot.get("config")
    current_config = current_snapshot.get("config")
    blocked_reasons: list[str] = []
    if not isinstance(package_config, dict):
        blocked_reasons.append("package config_snapshot.config is not an object")
    else:
        try:
            config_from_mapping(package_config)
        except ConfigValidationError as exc:
            blocked_reasons.append(f"package config is invalid: {exc}")
    if not isinstance(current_config, dict):
        blocked_reasons.append("current runtime config is not an object")
    package_config_hash = (
        stable_hash_payload(package_config) if isinstance(package_config, dict) else ""
    )
    current_config_hash = (
        stable_hash_payload(current_config) if isinstance(current_config, dict) else ""
    )
    config_diff_count = _runtime_export_section_diff_count(compare, "config")
    generated_config_diff_count = _runtime_export_section_diff_count(
        compare,
        "generated_config",
    )
    same_config = bool(compare.get("same_config"))
    if blocked_reasons:
        readiness = "BLOCKED"
    elif same_config:
        readiness = "NO_CHANGE"
    else:
        readiness = "READY"
    requires_runtime_reset = readiness == "READY"
    summary: dict[str, Any] = {
        "version": "v1",
        "source": "BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
        "preflight_scope": "CONFIG_RESTORE_PREVIEW_ONLY",
        "package_id": package_id,
        "readiness": readiness,
        "can_restore": readiness in {"READY", "NO_CHANGE"},
        "requires_user_confirmation": readiness == "READY",
        "would_mutate_current_runtime": False,
        "would_write_config_files": readiness == "READY",
        "would_reset_runtime_session": requires_runtime_reset,
        "would_stop_live_streams": requires_runtime_reset,
        "current_lifecycle_state": lifecycle_state,
        "package_config_hash": package_config_hash,
        "current_config_hash": current_config_hash,
        "same_config": same_config,
        "same_generated_config": bool(compare.get("same_generated_config")),
        "config_diff_count": config_diff_count,
        "generated_config_diff_count": generated_config_diff_count,
        "compare_hash": str(compare.get("compare_hash", "")),
        "blocked_reasons": tuple(blocked_reasons),
        "warnings": _runtime_export_restore_preflight_warnings(
            readiness,
            lifecycle_state,
            generated_config_diff_count,
        ),
        "next_action": _runtime_export_restore_preflight_next_action(readiness),
    }
    summary["runtime_export_boundary_alignment_v1"] = (
        _runtime_export_boundary_alignment_summary(
            package_id,
            package_snapshot,
            current_snapshot,
            source="BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
            compare=compare,
            preflight=summary,
        )
    )
    summary["preflight_hash"] = stable_hash_payload(summary)
    return summary


def _runtime_export_section_diff_count(compare: dict[str, Any], section: str) -> int:
    for item in _control_records(compare.get("sections")):
        if str(item.get("section", "")) == section:
            return _control_int(item.get("diff_count"))
    return 0


def _runtime_export_restore_preflight_warnings(
    readiness: str,
    lifecycle_state: str,
    generated_config_diff_count: int,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if readiness == "READY":
        warnings.append(
            "RESTORE_WOULD_REPLACE_RUNTIME_CONFIG_AND_REQUIRE_REINITIALIZATION"
        )
        if lifecycle_state == "RUNNING":
            warnings.append("RESTORE_WOULD_STOP_RUNNING_SESSION")
    if generated_config_diff_count > 0:
        warnings.append("GENERATED_CONFIG_WILL_BE_REDERIVED_AFTER_RESTORE")
    return tuple(warnings)


def _runtime_export_restore_preflight_next_action(readiness: str) -> str:
    if readiness == "BLOCKED":
        return "FIX_PACKAGE_OR_SELECT_ANOTHER_EXPORT"
    if readiness == "NO_CHANGE":
        return "NO_RESTORE_REQUIRED"
    return "USER_CONFIRMATION_REQUIRED_BEFORE_RESTORE"


def _runtime_export_section_differences(
    section: str,
    package_value: object,
    current_value: object,
) -> list[dict[str, Any]]:
    package_flat = _runtime_export_flatten_json(package_value)
    current_flat = _runtime_export_flatten_json(current_value)
    differences: list[dict[str, Any]] = []
    for path in sorted(set(package_flat) | set(current_flat)):
        package_missing = path not in package_flat
        current_missing = path not in current_flat
        if (
            not package_missing
            and not current_missing
            and package_flat[path] == current_flat[path]
        ):
            continue
        differences.append(
            {
                "section": section,
                "path": path,
                "package_missing": package_missing,
                "current_missing": current_missing,
                "package_value": None if package_missing else package_flat[path],
                "current_value": None if current_missing else current_flat[path],
            }
        )
    return differences


def _runtime_export_flatten_json(value: object, prefix: str = "$") -> dict[str, Any]:
    if isinstance(value, dict):
        if not value:
            return {prefix: {}}
        flattened: dict[str, Any] = {}
        for key in sorted(value):
            flattened.update(
                _runtime_export_flatten_json(value[key], f"{prefix}.{key}")
            )
        return flattened
    if isinstance(value, (list, tuple)):
        if not value:
            return {prefix: []}
        flattened = {}
        for index, item in enumerate(value):
            flattened.update(_runtime_export_flatten_json(item, f"{prefix}[{index}]"))
        return flattened
    return {prefix: stable_json_payload(value)}


def _runtime_export_snapshot_manifest_hash(snapshot: dict[str, Any]) -> str:
    status = snapshot.get("status")
    if not isinstance(status, dict):
        return ""
    manifest = status.get("reproducibility_manifest_v1")
    if not isinstance(manifest, dict):
        return ""
    return str(manifest.get("manifest_hash", ""))


def _runtime_export_manifest_state_value(
    manifest: object,
    key: str,
) -> object:
    if not isinstance(manifest, dict):
        return None
    runtime_state = manifest.get("runtime_state")
    if not isinstance(runtime_state, dict):
        return None
    return runtime_state.get(key)


def _relative_runtime_export_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _network_quality_provenance_from_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": "v1",
        "metric_model": _metric_string(metrics, "network_quality_metric_model"),
        "packet_level_simulation": False,
        "proxy_note": _metric_string(metrics, "network_quality_proxy_note"),
        "provenance_note": _metric_string(metrics, "network_quality_provenance_note"),
        "sources": {
            "throughput": _network_quality_source(
                metrics,
                "network_quality_throughput_source",
                "network_quality_throughput_source_label",
            ),
            "latency": _network_quality_source(
                metrics,
                "network_quality_latency_source",
                "network_quality_latency_source_label",
            ),
            "loss": _network_quality_source(
                metrics,
                "network_quality_loss_source",
                "network_quality_loss_source_label",
            ),
            "delay_variation": _network_quality_source(
                metrics,
                "network_quality_delay_variation_source",
                "network_quality_delay_variation_source_label",
            ),
        },
        "zero_reasons": {
            "loss": _network_quality_zero_reason(
                metrics,
                "network_quality_loss_zero_reason",
                "network_quality_loss_zero_reason_label",
            ),
            "delay_variation": _network_quality_zero_reason(
                metrics,
                "network_quality_delay_variation_zero_reason",
                "network_quality_delay_variation_zero_reason_label",
            ),
        },
    }


def _network_quality_source(
    metrics: dict[str, Any],
    source_key: str,
    label_key: str,
) -> dict[str, str]:
    return {
        "source": _metric_string(metrics, source_key),
        "label": _metric_string(metrics, label_key),
    }


def _network_quality_zero_reason(
    metrics: dict[str, Any],
    reason_key: str,
    label_key: str,
) -> dict[str, str]:
    return {
        "reason": _metric_string(metrics, reason_key),
        "label": _metric_string(metrics, label_key),
    }


def _metric_string(metrics: dict[str, Any], key: str) -> str:
    value = metrics.get(key)
    return value if isinstance(value, str) else ""


def _fidelity_summary_from_demo_config(config: DemoConfig) -> dict[str, object]:
    return build_scale_fidelity_summary(
        ScaleFidelityConfig(
            satellite_count=config.satellite_count,
            user_count=config.ground_user_count,
            forced_orbit_update_mode=config.orbit_update_mode,
            forced_space_link_mode=config.space_link_mode,
            space_link_enabled=True,
            max_space_link_candidates_per_satellite=(
                config.max_space_link_candidates_per_satellite
            ),
            batch_space_link_update_limit=config.batch_space_link_update_limit,
        )
    )


def _fidelity_summary_from_sees_config(config: SEESConfig) -> dict[str, object]:
    orbit_update_mode = config.scenario.orbit.orbit_update_mode
    return build_scale_fidelity_summary(
        ScaleFidelityConfig(
            satellite_count=config.scenario.satellite_count,
            user_count=config.scenario.user_count,
            forced_orbit_update_mode=(
                orbit_update_mode.value if orbit_update_mode is not None else None
            ),
            forced_space_link_mode=(
                config.network.space_link_mode.value
                if config.network.space_link_mode is not None
                else None
            ),
            space_link_enabled=True,
            max_space_link_candidates_per_satellite=(
                config.network.max_space_link_candidates_per_satellite
            ),
            batch_space_link_update_limit=config.network.batch_space_link_update_limit,
        )
    )
