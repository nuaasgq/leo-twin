"""Configuration loader for the full-system pipeline demo."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "full_system_pipeline_demo.json"


@dataclass(frozen=True)
class FullSystemPipelineConfig:
    """Typed configuration for the full-system pipeline demo."""

    orbit: Mapping[str, Any]
    ground_endpoint: Mapping[str, Any]
    network: Mapping[str, Any]
    flow: Mapping[str, Any]
    task: Mapping[str, Any]
    compute: Mapping[str, Any]
    channel: Mapping[str, Any]
    link_budget: Mapping[str, Any]
    transmit_terminal: Mapping[str, Any]
    receive_terminal: Mapping[str, Any]
    transport: Mapping[str, Any]


def load_full_system_pipeline_config(
    path: str | Path = DEFAULT_CONFIG_PATH,
) -> FullSystemPipelineConfig:
    """Load and validate the deterministic full-system pipeline demo config."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, Mapping):
        raise ValueError("full-system pipeline config must be a mapping")
    return FullSystemPipelineConfig(
        orbit=_mapping(data, "orbit"),
        ground_endpoint=_mapping(data, "ground_endpoint"),
        network=_mapping(data, "network"),
        flow=_mapping(data, "flow"),
        task=_mapping(data, "task"),
        compute=_mapping(data, "compute"),
        channel=_mapping(data, "channel"),
        link_budget=_mapping(data, "link_budget"),
        transmit_terminal=_mapping(data, "transmit_terminal"),
        receive_terminal=_mapping(data, "receive_terminal"),
        transport=_mapping(data, "transport"),
    )


def _mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"{key} must be a mapping")
    return dict(value)
