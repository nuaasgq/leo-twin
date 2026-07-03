"""Local compute module runtime contracts."""

from dataclasses import dataclass
from math import isfinite


COMPUTE_NODE_UPDATE = "COMPUTE_NODE_UPDATE"


@dataclass(frozen=True)
class ComputeNode:
    """Configuration for one deterministic simulated compute node."""

    node_id: str
    capacity: float

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, str) or not self.node_id:
            raise TypeError("node_id must be a non-empty str")
        if isinstance(self.capacity, bool) or not isinstance(
            self.capacity,
            (int, float),
        ):
            raise TypeError("capacity must be an int or float")
        if not isfinite(self.capacity) or self.capacity <= 0:
            raise ValueError("capacity must be finite and positive")
