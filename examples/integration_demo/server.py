"""HTTP and WebSocket server for the integration demo."""

from __future__ import annotations

import argparse
import base64
import hashlib
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

from examples.integration_demo.config import DEFAULT_CONFIG_PATH, DemoConfig, load_demo_config
from examples.integration_demo.runtime import DemoRunResult, run_integration_demo
from examples.integration_demo.serialization import (
    JsonValue,
    event_to_json,
    events_jsonl,
    stable_json,
    stable_json_pretty,
)


_WEBSOCKET_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
_FRONTEND_EVENT_TYPES = frozenset(
    {
        "ORBIT_UPDATE",
        "LINK_UPDATE",
        "ACCESS_START",
        "ACCESS_END",
        "ROUTE_UPDATE",
        "TASK_START",
        "TASK_FINISH",
        "METRIC_SAMPLE",
    }
)


def serve_demo(result: DemoRunResult, host: str, port: int) -> None:
    handler = _handler_for(result)
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


def _handler_for(result: DemoRunResult) -> type[BaseHTTPRequestHandler]:
    class DemoRequestHandler(BaseHTTPRequestHandler):
        server_version = "LEOTwinDemo/0.1"

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self._cors_headers()
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if self.headers.get("Upgrade", "").lower() == "websocket":
                self._handle_websocket(path)
                return
            if path == result.config.scenario_config:
                self._send_json(result.scenario.frontend_config)
                return
            if path == result.config.metrics_snapshot:
                self._send_json(result.final_snapshot)
                return
            if path == "/health":
                self._send_json({"status": "ok", "events": len(result.processed_events)})
                return
            self.send_error(404, "not found")

        def log_message(self, format: str, *args: object) -> None:
            return

        def _handle_websocket(self, path: str) -> None:
            if path == result.config.websocket_events:
                self._accept_websocket()
                for event in result.processed_events:
                    if str(event.event_type) in _FRONTEND_EVENT_TYPES:
                        self._send_ws_json(event_to_json(event))
                self._close_websocket()
                return
            if path == result.config.websocket_state:
                self._accept_websocket()
                for snapshot in result.state_timeline:
                    self._send_ws_json(snapshot)
                self._close_websocket()
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

        def _cors_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
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

        def _close_websocket(self) -> None:
            self._send_ws_close()
            self.close_connection = True
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    return DemoRequestHandler


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


if __name__ == "__main__":
    raise SystemExit(main())
