"""Configuration loading for the full-system integration demo."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DemoConfig:
    seed: int
    satellite_count: int
    ground_user_count: int
    ground_station_count: int
    compute_node_count: int
    duration_seconds: int
    orbit_tick_seconds: int
    network_slot_seconds: int
    flow_interval_seconds: int
    task_interval_seconds: int
    cell_count: int
    state_snapshot_interval_events: int
    metric_sample_interval: int
    websocket_events: str
    websocket_state: str
    metrics_snapshot: str
    scenario_config: str
    backend_host: str
    backend_port: int


DEFAULT_CONFIG_PATH = Path("configs/integration_demo.yaml")


def load_demo_config(path: str | Path = DEFAULT_CONFIG_PATH) -> DemoConfig:
    data = _parse_simple_yaml(Path(path).read_text(encoding="utf-8"))
    scenario = _section(data, "scenario")
    frontend = _section(data, "frontend")
    return DemoConfig(
        seed=_int(scenario, "seed"),
        satellite_count=_int(scenario, "satellite_count"),
        ground_user_count=_int(scenario, "ground_user_count"),
        ground_station_count=_int(scenario, "ground_station_count"),
        compute_node_count=_int(scenario, "compute_node_count"),
        duration_seconds=_int(scenario, "duration_seconds"),
        orbit_tick_seconds=_int(scenario, "orbit_tick_seconds"),
        network_slot_seconds=_int(scenario, "network_slot_seconds"),
        flow_interval_seconds=_int(scenario, "flow_interval_seconds"),
        task_interval_seconds=_int(scenario, "task_interval_seconds"),
        cell_count=_int(scenario, "cell_count"),
        state_snapshot_interval_events=_int(
            scenario,
            "state_snapshot_interval_events",
        ),
        metric_sample_interval=_int(scenario, "metric_sample_interval"),
        websocket_events=_str(frontend, "websocket_events"),
        websocket_state=_str(frontend, "websocket_state"),
        metrics_snapshot=_str(frontend, "metrics_snapshot"),
        scenario_config=_str(frontend, "scenario_config"),
        backend_host=_str(frontend, "backend_host"),
        backend_port=_int(frontend, "backend_port"),
    )


def _parse_simple_yaml(text: str) -> dict[str, dict[str, Any]]:
    root: dict[str, dict[str, Any]] = {}
    current_section: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" "):
            key, value = _split_key_value(line)
            if value:
                raise ValueError("top-level config entries must be sections")
            current_section = key
            root[current_section] = {}
            continue
        if current_section is None:
            raise ValueError("nested config entry appears before a section")
        key, value = _split_key_value(line.strip())
        root[current_section][key] = _scalar(value)
    return root


def _split_key_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"invalid config line: {line!r}")
    key, value = line.split(":", 1)
    key = key.strip()
    if not key:
        raise ValueError(f"empty config key: {line!r}")
    return key, value.strip()


def _scalar(value: str) -> Any:
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value.strip('"')


def _section(data: dict[str, dict[str, Any]], key: str) -> dict[str, Any]:
    try:
        return data[key]
    except KeyError as exc:
        raise KeyError(f"missing config section: {key}") from exc


def _int(section: dict[str, Any], key: str) -> int:
    value = section[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{key} must be an int")
    return value


def _str(section: dict[str, Any], key: str) -> str:
    value = section[key]
    if not isinstance(value, str) or not value:
        raise TypeError(f"{key} must be a non-empty string")
    return value
