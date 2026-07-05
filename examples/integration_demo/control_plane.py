"""Control-plane integration for the full-system demo backend."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
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
from leo_twin.schema.config_loader import write_config
from leo_twin.models.orbit import KeplerianOrbitEngine
from leo_twin.schema import SatelliteState
from leo_twin.schema.config import SEESConfig
from leo_twin.services.configuration_view import (
    build_user_configuration_view,
    load_user_configuration_template,
)
from leo_twin.services.network_kpi_provenance import build_network_kpi_provenance_v2
from leo_twin.services.control import (
    RuntimeController,
    ScaleSafetyChecker,
)
from leo_twin.services.runtime_observability import (
    build_runtime_lifecycle_summaries,
    build_runtime_node_detail_page,
    build_runtime_satellite_service_summary,
    build_runtime_user_request_summary,
)
from leo_twin.services.runtime_reproducibility import (
    build_runtime_reproducibility_manifest,
    stable_hash_payload,
    stable_json_payload,
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

    def runtime_user_details(self, cursor: int = 0, limit: int = 100) -> dict[str, Any]:
        summary = build_runtime_user_request_summary(
            self.visible_snapshot(),
            service_latency_history=self._service_latency_history_json(),
            cursor=cursor,
            limit=limit,
        )
        return {
            "type": "RUNTIME_DETAIL_PAGE",
            "kind": "users",
            "summary": summary,
        }

    def runtime_satellite_details(
        self,
        cursor: int = 0,
        limit: int = 120,
    ) -> dict[str, Any]:
        summary = build_runtime_satellite_service_summary(
            self.visible_snapshot(),
            service_latency_history=self._service_latency_history_json(),
            satellite_kpi_slices=self._satellite_kpi_slices_json(),
            cursor=cursor,
            limit=limit,
        )
        return {
            "type": "RUNTIME_DETAIL_PAGE",
            "kind": "satellites",
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
        config_snapshot = {
            "type": "RUNTIME_CONFIG_SNAPSHOT",
            "status": _runtime_export_status_snapshot(status),
            "config": self._controller.config_json(),
            "generated_config": generated_config,
        }
        config_snapshot_path = package_dir / "config_snapshot.json"
        manifest_path = package_dir / "manifest.json"
        config_snapshot_path.write_text(
            stable_json_pretty(config_snapshot), encoding="utf-8"
        )
        manifest = dict(status["reproducibility_manifest_v1"])
        manifest_path.write_text(stable_json_pretty(manifest), encoding="utf-8")
        written_files["config_snapshot"] = config_snapshot_path
        written_files["manifest"] = manifest_path

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
        status["network_kpi_provenance_v2"] = build_network_kpi_provenance_v2(
            metrics_summary
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

    def _ack(self, command: ControlCommand) -> dict[str, Any]:
        generated_config = self._generated_config_json()
        return {
            "type": "CONTROL_ACK",
            "ok": True,
            "command": command.command.value,
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
    if filename.endswith(".zip"):
        return "application/zip"
    return "application/octet-stream"


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
