"""Performance mode policies for external event-flow control."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from leo_twin.schema import EventType


class PerformanceMode(StrEnum):
    """Named runtime modes used by stabilization controls."""

    NORMAL = "NORMAL"
    FULL = "FULL"
    OPTIMIZED = "OPTIMIZED"
    SCALE = "SCALE"


@dataclass(frozen=True)
class EventFlowPolicy:
    """Configuration for deterministic event flow control.

    The policy is consumed by an external controller. It does not modify the
    event schema or the simulation kernel.
    """

    mode: PerformanceMode = PerformanceMode.FULL
    batching_enabled: bool = False
    time_window: float = 0.0
    deduplicate: bool = False
    priority_floor: int | None = None
    suppressed_event_types: tuple[str, ...] = ()
    max_events_per_window: int | None = None
    window_history_limit: int = 1024
    partitioning_enabled: bool = False
    compression_enabled: bool = False
    frontend_batch_size: int = 200
    snapshot_interval_events: int = 1000

    def __post_init__(self) -> None:
        if not isinstance(self.mode, PerformanceMode):
            object.__setattr__(self, "mode", PerformanceMode(self.mode))
        _require_non_negative_finite(self.time_window, "time_window")
        if self.priority_floor is not None and (
            isinstance(self.priority_floor, bool)
            or not isinstance(self.priority_floor, int)
        ):
            raise TypeError("priority_floor must be an int or None")
        _require_optional_positive_int(
            self.max_events_per_window,
            "max_events_per_window",
        )
        _require_positive_int(self.window_history_limit, "window_history_limit")
        _require_positive_int(self.frontend_batch_size, "frontend_batch_size")
        _require_positive_int(
            self.snapshot_interval_events,
            "snapshot_interval_events",
        )
        object.__setattr__(
            self,
            "suppressed_event_types",
            tuple(sorted(str(event_type) for event_type in self.suppressed_event_types)),
        )

    @classmethod
    def for_mode(cls, mode: PerformanceMode | str) -> "EventFlowPolicy":
        selected_mode = PerformanceMode(mode)
        if selected_mode in {PerformanceMode.NORMAL, PerformanceMode.FULL}:
            return cls(mode=selected_mode)
        if selected_mode == PerformanceMode.OPTIMIZED:
            return cls(
                mode=selected_mode,
                batching_enabled=True,
                time_window=1.0,
                deduplicate=True,
                suppressed_event_types=(EventType.METRIC_SAMPLE.value,),
                partitioning_enabled=True,
                compression_enabled=True,
                frontend_batch_size=500,
                snapshot_interval_events=1000,
            )
        return cls(
            mode=selected_mode,
            batching_enabled=True,
            time_window=5.0,
            deduplicate=True,
            priority_floor=0,
            suppressed_event_types=(EventType.METRIC_SAMPLE.value,),
            max_events_per_window=10000,
            window_history_limit=4096,
            partitioning_enabled=True,
            compression_enabled=True,
            frontend_batch_size=2000,
            snapshot_interval_events=10000,
        )


def _require_non_negative_finite(value: float, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value) or value < 0:
        raise ValueError(f"{field_name} must be finite and non-negative")


def _require_optional_positive_int(value: int | None, field_name: str) -> None:
    if value is None:
        return
    _require_positive_int(value, field_name)


def _require_positive_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")
