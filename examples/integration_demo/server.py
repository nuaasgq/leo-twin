"""HTTP and WebSocket server for the integration demo."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs, unquote, urlsplit

from examples.integration_demo.config import DEFAULT_CONFIG_PATH, DemoConfig, load_demo_config
from examples.integration_demo.control_plane import (
    DemoControlPlane,
    RuntimeExportArtifactError,
)
from examples.integration_demo.runtime import DemoRunResult, run_integration_demo
from examples.integration_demo.serialization import (
    JsonValue,
    events_jsonl,
    stable_json,
    stable_json_pretty,
)
from leo_twin.runtime import RuntimeLifecycleState


_WEBSOCKET_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
_WEBSOCKET_STREAM_INTERVAL_SECONDS = 0.05
_WEBSOCKET_STREAM_BATCH_LIMIT = 500
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


def serve_demo(result: DemoRunResult, host: str, port: int) -> None:
    handler = _handler_for(DemoControlPlane.from_result(result))
    ThreadingHTTPServer((host, port), handler).serve_forever()


def write_replay_artifacts(result: DemoRunResult, output_dir: str | Path) -> dict[str, Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    files = {
        "events": root / "integration-demo-events.jsonl",
        "state": root / "integration-demo-final-state.json",
        "scenario": root / "integration-demo-scenario.json",
    }
    files["events"].write_text(events_jsonl(result.processed_events), encoding="utf-8")
    files["state"].write_text(stable_json_pretty(result.final_snapshot), encoding="utf-8")
    files["scenario"].write_text(
        stable_json_pretty(result.scenario.frontend_config), encoding="utf-8"
    )
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="run_demo.py")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--write-replay", default=None)
    parser.add_argument("--no-server", action="store_true")
    args = parser.parse_args(argv)

    config = load_demo_config(args.config)
    result = run_integration_demo(config)
    if args.write_replay:
        write_replay_artifacts(result, args.write_replay)
    if args.no_server:
        print(_summary_text(result))
        return 0

    host = args.host or config.backend_host
    port = args.port or config.backend_port
    print(_summary_text(result))
    print(f"Serving demo backend at http://{host}:{port}")
    serve_demo(result, host, port)
    return 0


def _summary_text(result: DemoRunResult) -> str:
    return "\n".join(
        (
            "LEO-Twin integration demo ready",
            f"events={len(result.processed_events)}",
            f"frontend_events={len(result.frontend_events)}",
            f"satellites={len(result.scenario.orbit_satellites)}",
            f"ground_users={result.config.ground_user_count}",
            f"ground_stations={result.config.ground_station_count}",
            f"compute_nodes={len(result.scenario.compute_nodes)}",
        )
    )


def _handler_for(control_plane: DemoControlPlane) -> type[BaseHTTPRequestHandler]:
    class DemoRequestHandler(BaseHTTPRequestHandler):
        server_version = "LEOTwinDemo/0.1"

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self._cors_headers()
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            result = control_plane.result
            parsed_url = urlsplit(self.path)
            path = parsed_url.path
            query = parse_qs(parsed_url.query)
            if self.headers.get("Upgrade", "").lower() == "websocket":
                self._handle_websocket(path)
                return
            if path == result.config.scenario_config:
                self._send_json(result.scenario.frontend_config)
                return
            if path == "/scenario/user-config/schema":
                self._send_json(control_plane.user_configuration_schema())
                return
            if path == "/scenario/user-config/templates":
                self._send_json(control_plane.user_configuration_templates())
                return
            if path == "/scenario/user-config/export":
                self._send_json(control_plane.user_configuration_export())
                return
            if path == result.config.metrics_snapshot:
                self._send_json(control_plane.visible_snapshot())
                return
            if path == result.config.websocket_events:
                try:
                    cursor, limit = _stream_query(query)
                except ValueError as exc:
                    self.send_error(400, str(exc))
                    return
                self._send_json(control_plane.stream_event_batch(cursor, limit))
                return
            if path == result.config.websocket_state:
                try:
                    cursor, limit = _stream_query(query)
                except ValueError as exc:
                    self.send_error(400, str(exc))
                    return
                self._send_json(control_plane.stream_snapshot_batch(cursor, limit))
                return
            if path == "/health":
                self._send_json({"status": "ok", "events": len(result.processed_events)})
                return
            if path == "/runtime/status":
                self._send_json(control_plane.runtime_status())
                return
            if path == "/runtime/export":
                try:
                    self._send_json(control_plane.export_runtime_package())
                except RuntimeError as exc:
                    self.send_error(409, str(exc))
                return
            if path == "/runtime/export/history":
                self._send_json(control_plane.runtime_export_history())
                return
            if path == "/runtime/export/catalog":
                self._send_json(control_plane.runtime_export_catalog())
                return
            export_artifact_route = _runtime_export_package_route(path)
            if export_artifact_route is not None:
                package_id, artifact_kind, filename = export_artifact_route
                try:
                    if artifact_kind == "record":
                        self._send_json(
                            control_plane.runtime_export_package_record(package_id)
                        )
                        return
                    if artifact_kind == "compare":
                        self._send_json(
                            control_plane.runtime_export_package_compare(package_id)
                        )
                        return
                    if artifact_kind == "restore-preflight":
                        self._send_json(
                            control_plane.runtime_export_package_restore_preflight(
                                package_id
                            )
                        )
                        return
                    if artifact_kind == "manifest":
                        artifact = control_plane.runtime_export_package_artifact(
                            package_id,
                            "manifest.json",
                        )
                    elif artifact_kind == "archive":
                        artifact = control_plane.runtime_export_package_archive_artifact(
                            package_id,
                        )
                    elif artifact_kind == "file" and filename is not None:
                        artifact = control_plane.runtime_export_package_artifact(
                            package_id,
                            filename,
                        )
                    else:
                        self.send_error(404, "runtime export artifact not found")
                        return
                except RuntimeExportArtifactError as exc:
                    self.send_error(404, str(exc))
                    return
                self._send_file(
                    Path(artifact["path"]),
                    content_type=str(artifact["content_type"]),
                    download_name=str(artifact["filename"]),
                )
                return
            if path == "/runtime/export/archive":
                try:
                    exported_archive = control_plane.export_runtime_archive()
                except RuntimeError as exc:
                    self.send_error(409, str(exc))
                    return
                archive = exported_archive["archive"]
                self._send_file(
                    Path(str(archive["path"])),
                    content_type="application/zip",
                    download_name=str(archive["filename"]),
                )
                return
            if path == "/runtime/details/users":
                try:
                    cursor, limit = _detail_query(query, default_limit=100)
                except ValueError as exc:
                    self.send_error(400, str(exc))
                    return
                self._send_json(control_plane.runtime_user_details(cursor, limit))
                return
            if path == "/runtime/details/satellites":
                try:
                    cursor, limit = _detail_query(query, default_limit=120)
                except ValueError as exc:
                    self.send_error(400, str(exc))
                    return
                self._send_json(control_plane.runtime_satellite_details(cursor, limit))
                return
            if path == "/runtime/details/nodes":
                try:
                    cursor, limit = _detail_query(query, default_limit=100)
                except ValueError as exc:
                    self.send_error(400, str(exc))
                    return
                self._send_json(control_plane.runtime_node_details(cursor, limit))
                return
            self.send_error(404, "not found")

        def do_POST(self) -> None:  # noqa: N802
            parsed_url = urlsplit(self.path)
            path = parsed_url.path
            if path == "/scenario/user-config/validate":
                try:
                    payload = self._read_json_body()
                except ValueError as exc:
                    self.send_error(400, str(exc))
                    return
                self._send_json(control_plane.user_configuration_validate(payload))
                return
            self.send_error(404, "not found")

        def log_message(self, format: str, *args: object) -> None:
            return

        def _handle_websocket(self, path: str) -> None:
            result = control_plane.result
            if path == result.config.websocket_events:
                self._accept_websocket()
                self._stream_event_batches()
                self._close_websocket()
                return
            if path == result.config.websocket_state:
                self._accept_websocket()
                self._stream_snapshot_batches()
                self._close_websocket()
                return
            if path == "/control":
                self._handle_control_websocket()
                return
            self.send_error(404, "websocket endpoint not found")

        def _send_json(self, payload: JsonValue) -> None:
            data = stable_json(payload).encode("utf-8")
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_file(
            self,
            path: Path,
            *,
            content_type: str,
            download_name: str,
        ) -> None:
            data = path.read_bytes()
            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", content_type)
            self.send_header(
                "Content-Disposition",
                f'attachment; filename="{download_name}"',
            )
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _read_json_body(self) -> object:
            content_length = self.headers.get("Content-Length")
            if content_length is None:
                raise ValueError("missing Content-Length")
            try:
                length = int(content_length)
            except ValueError as exc:
                raise ValueError("invalid Content-Length") from exc
            if length < 0:
                raise ValueError("invalid Content-Length")
            raw = self.rfile.read(length)
            try:
                return json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("request body must be valid UTF-8 JSON") from exc

        def _cors_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def _accept_websocket(self) -> None:
            key = self.headers.get("Sec-WebSocket-Key")
            if not key:
                raise ValueError("missing Sec-WebSocket-Key")
            accept = base64.b64encode(
                hashlib.sha1((key + _WEBSOCKET_GUID).encode("ascii")).digest()
            ).decode("ascii")
            self.send_response(101)
            self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade")
            self.send_header("Sec-WebSocket-Accept", accept)
            self.end_headers()

        def _send_ws_json(self, payload: JsonValue) -> None:
            _write_ws_frame(self.wfile.write, stable_json(payload).encode("utf-8"))

        def _send_ws_close(self) -> None:
            _write_ws_frame(self.wfile.write, b"", opcode=0x8)

        def _handle_control_websocket(self) -> None:
            self._accept_websocket()
            self._send_ws_json(control_plane.runtime_status())
            while True:
                try:
                    opcode, payload = _read_ws_frame(self.rfile.read)
                except OSError:
                    break
                if opcode == 0x8:
                    break
                if opcode == 0x9:
                    _write_ws_frame(self.wfile.write, payload, opcode=0xA)
                    continue
                if opcode != 0x1:
                    self._send_ws_json(
                        {
                            "type": "CONTROL_ACK",
                            "ok": False,
                            "error": f"unsupported websocket opcode: {opcode}",
                        }
                    )
                    continue
                self._send_ws_json(control_plane.handle_raw_message(payload))
            self._close_websocket()

        def _stream_event_batches(self) -> None:
            cursor = 0
            while True:
                batch = control_plane.stream_event_batch(
                    cursor,
                    limit=_WEBSOCKET_STREAM_BATCH_LIMIT,
                )
                cursor = int(batch["next_cursor"])
                items = batch["items"]
                if items:
                    self._send_ws_json(batch)  # type: ignore[arg-type]
                if _live_stream_finished(control_plane.runtime_lifecycle_state(), bool(items)):
                    return
                time.sleep(_WEBSOCKET_STREAM_INTERVAL_SECONDS)

        def _stream_snapshot_batches(self) -> None:
            cursor = 0
            while True:
                batch = control_plane.stream_snapshot_batch(
                    cursor,
                    limit=_WEBSOCKET_STREAM_BATCH_LIMIT,
                )
                cursor = int(batch["next_cursor"])
                items = batch["items"]
                if items:
                    self._send_ws_json(batch)  # type: ignore[arg-type]
                if _live_stream_finished(control_plane.runtime_lifecycle_state(), bool(items)):
                    return
                time.sleep(_WEBSOCKET_STREAM_INTERVAL_SECONDS)

        def _close_websocket(self) -> None:
            self._send_ws_close()
            self.close_connection = True
            try:
                self.connection.close()
            except OSError:
                pass

    return DemoRequestHandler


def _live_stream_finished(state: RuntimeLifecycleState, sent_items: bool) -> bool:
    if sent_items:
        return False
    return state != RuntimeLifecycleState.RUNNING


def _write_ws_frame(
    write: Callable[[bytes], object],
    payload: bytes,
    opcode: int = 0x1,
) -> None:
    first = bytes([0x80 | opcode])
    length = len(payload)
    if length <= 125:
        header = first + bytes([length])
    elif length <= 65_535:
        header = first + bytes([126]) + length.to_bytes(2, "big")
    else:
        header = first + bytes([127]) + length.to_bytes(8, "big")
    write(header + payload)


def _read_ws_frame(read: Callable[[int], bytes]) -> tuple[int, bytes]:
    header = _read_exact(read, 2)
    first, second = header
    opcode = first & 0x0F
    masked = (second & 0x80) != 0
    length = second & 0x7F
    if length == 126:
        length = int.from_bytes(_read_exact(read, 2), "big")
    elif length == 127:
        length = int.from_bytes(_read_exact(read, 8), "big")
    mask_key = _read_exact(read, 4) if masked else b""
    payload = _read_exact(read, length) if length else b""
    if masked:
        payload = bytes(byte ^ mask_key[index % 4] for index, byte in enumerate(payload))
    return opcode, payload


def _read_exact(read: Callable[[int], bytes], size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining > 0:
        chunk = read(remaining)
        if not chunk:
            raise OSError("websocket connection closed")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _stream_query(query: dict[str, list[str]]) -> tuple[int, int | None]:
    cursor = _optional_query_int(query, "cursor", 0)
    limit = _optional_query_int(query, "limit", None)
    if cursor < 0:
        raise ValueError("cursor must be non-negative")
    if limit is not None and limit <= 0:
        raise ValueError("limit must be positive")
    return cursor, limit


def _detail_query(query: dict[str, list[str]], *, default_limit: int) -> tuple[int, int]:
    cursor = _optional_query_int(query, "cursor", 0)
    limit = _optional_query_int(query, "limit", default_limit)
    if cursor < 0:
        raise ValueError("cursor must be non-negative")
    if limit is None or limit <= 0:
        raise ValueError("limit must be positive")
    return cursor, min(limit, 5_000)


def _runtime_export_package_route(
    path: str,
) -> tuple[str, str, str | None] | None:
    prefix = "/runtime/export/packages/"
    if not path.startswith(prefix):
        return None
    suffix = path[len(prefix) :].strip("/")
    parts = [unquote(part) for part in suffix.split("/") if part]
    if len(parts) == 1:
        return parts[0], "record", None
    if len(parts) == 2 and parts[1] == "manifest":
        return parts[0], "manifest", None
    if len(parts) == 2 and parts[1] == "compare":
        return parts[0], "compare", None
    if len(parts) == 2 and parts[1] == "restore-preflight":
        return parts[0], "restore-preflight", None
    if len(parts) == 2 and parts[1] == "archive":
        return parts[0], "archive", None
    if len(parts) == 3 and parts[1] == "files":
        return parts[0], "file", parts[2]
    return "", "missing", None


def _optional_query_int(
    query: dict[str, list[str]],
    key: str,
    default: int | None,
) -> int | None:
    values = query.get(key)
    if not values:
        return default
    return int(values[-1])


if __name__ == "__main__":
    raise SystemExit(main())
