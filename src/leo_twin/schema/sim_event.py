"""Discrete-event data definitions."""

from dataclasses import dataclass
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class SimEvent:
    """An immutable event scheduled on simulation time."""

    event_id: int | str
    sim_time: float
    priority: int
    source: str
    target: str
    event_type: str
    payload: Any

    def __post_init__(self) -> None:
        if isinstance(self.event_id, bool) or not isinstance(
            self.event_id,
            (int, str),
        ):
            raise TypeError("event_id must be an int or str")
        if isinstance(self.sim_time, bool) or not isinstance(
            self.sim_time,
            (int, float),
        ):
            raise TypeError("sim_time must be an int or float")
        if not isfinite(self.sim_time):
            raise ValueError("sim_time must be finite")
        if isinstance(self.priority, bool) or not isinstance(self.priority, int):
            raise TypeError("priority must be an int")
        for field_name in ("source", "target", "event_type"):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be a str")
