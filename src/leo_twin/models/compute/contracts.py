"""Local compute module runtime contracts."""

from dataclasses import dataclass
from math import isfinite


COMPUTE_NODE_UPDATE = "COMPUTE_NODE_UPDATE"


@dataclass(frozen=True)
class ComputeNode:
    """Configuration for one deterministic simulated compute node."""

    node_id: str
    capacity: float
    cpu_gflops_fp64: float = 0.0
    gpu_tflops_fp32: float = 0.0
    gpu_tflops_fp16: float = 0.0
    npu_tops_int8: float = 0.0
    memory_gb: float = 0.0
    storage_gb: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, str) or not self.node_id:
            raise TypeError("node_id must be a non-empty str")
        _require_number(self.capacity, "capacity")
        if self.capacity <= 0:
            raise ValueError("capacity must be finite and positive")
        for field_name in (
            "cpu_gflops_fp64",
            "gpu_tflops_fp32",
            "gpu_tflops_fp16",
            "npu_tops_int8",
            "memory_gb",
            "storage_gb",
        ):
            value = getattr(self, field_name)
            _require_number(value, field_name)
            if value < 0:
                raise ValueError(f"{field_name} must be non-negative")
            object.__setattr__(self, field_name, float(value))
        object.__setattr__(self, "capacity", float(self.capacity))


def _require_number(value: float, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite")
