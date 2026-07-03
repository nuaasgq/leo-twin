"""Frozen event contract definitions for parallel domain modules."""

from dataclasses import dataclass
from enum import StrEnum


class EventType(StrEnum):
    """Canonical event type names exchanged through SimEvent."""

    ORBIT_TRIGGER = "ORBIT_TRIGGER"
    ORBIT_UPDATE = "ORBIT_UPDATE"
    ACCESS_START = "ACCESS_START"
    ACCESS_END = "ACCESS_END"
    LINK_UPDATE = "LINK_UPDATE"
    FLOW_ARRIVAL = "FLOW_ARRIVAL"
    FLOW_COMPLETE = "FLOW_COMPLETE"
    ROUTE_UPDATE = "ROUTE_UPDATE"
    TASK_ARRIVAL = "TASK_ARRIVAL"
    TASK_START = "TASK_START"
    TASK_FINISH = "TASK_FINISH"
    METRIC_SAMPLE = "METRIC_SAMPLE"


@dataclass(frozen=True)
class EventContract:
    """Static contract for one event type."""

    event_type: EventType
    producer: str
    consumers: tuple[str, ...]
    payload_schema: str
    description: str


EVENT_CONTRACTS: tuple[EventContract, ...] = (
    EventContract(
        event_type=EventType.ORBIT_TRIGGER,
        producer="scenario",
        consumers=("orbit",),
        payload_schema="None",
        description="Trigger for orbit module state publication.",
    ),
    EventContract(
        event_type=EventType.ORBIT_UPDATE,
        producer="orbit",
        consumers=("network", "metrics"),
        payload_schema="SatelliteState",
        description="Published satellite state update.",
    ),
    EventContract(
        event_type=EventType.ACCESS_START,
        producer="network",
        consumers=("metrics",),
        payload_schema="LinkState",
        description="Start of satellite-ground access.",
    ),
    EventContract(
        event_type=EventType.ACCESS_END,
        producer="network",
        consumers=("metrics",),
        payload_schema="LinkState",
        description="End of satellite-ground access.",
    ),
    EventContract(
        event_type=EventType.LINK_UPDATE,
        producer="network",
        consumers=("metrics",),
        payload_schema="LinkState",
        description="Flow-level link state update.",
    ),
    EventContract(
        event_type=EventType.FLOW_ARRIVAL,
        producer="scenario",
        consumers=("network",),
        payload_schema="FlowRequest",
        description="Flow-level route request.",
    ),
    EventContract(
        event_type=EventType.FLOW_COMPLETE,
        producer="network",
        consumers=("compute", "metrics"),
        payload_schema="FlowState",
        description="Flow state completion update.",
    ),
    EventContract(
        event_type=EventType.ROUTE_UPDATE,
        producer="network",
        consumers=("compute", "metrics"),
        payload_schema="Route",
        description="Route output for a flow request.",
    ),
    EventContract(
        event_type=EventType.TASK_ARRIVAL,
        producer="scenario",
        consumers=("compute",),
        payload_schema="TaskRequest",
        description="Compute task request.",
    ),
    EventContract(
        event_type=EventType.TASK_START,
        producer="compute",
        consumers=("metrics",),
        payload_schema="TaskState",
        description="Task execution start update.",
    ),
    EventContract(
        event_type=EventType.TASK_FINISH,
        producer="compute",
        consumers=("metrics",),
        payload_schema="TaskState",
        description="Task execution finish update.",
    ),
    EventContract(
        event_type=EventType.METRIC_SAMPLE,
        producer="metrics",
        consumers=("adapters",),
        payload_schema="MetricRecord",
        description="Metric sample generated from read-only event observation.",
    ),
)


MODULE_DEPENDENCIES: tuple[tuple[str, str], ...] = (
    ("orbit", "schema"),
    ("network", "schema"),
    ("compute", "schema"),
    ("metrics", "schema"),
)
