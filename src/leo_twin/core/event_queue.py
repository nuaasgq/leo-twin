"""Deterministic priority queue for simulation events."""

import heapq

from leo_twin.schema import SimEvent


EventIdKey = tuple[int, int | str]
QueueKey = tuple[float, int, EventIdKey]
QueueEntry = tuple[QueueKey, SimEvent]


def _event_id_key(event_id: int | str) -> EventIdKey:
    if isinstance(event_id, int):
        return (0, event_id)
    return (1, event_id)


class EventQueue:
    """Order events by time, descending priority, and event identifier.

    Integer identifiers sort before string identifiers. Identifiers within
    the same type sort in ascending order.
    """

    def __init__(self) -> None:
        self._heap: list[QueueEntry] = []
        self._seen_event_ids: set[int | str] = set()

    def push(self, event: SimEvent) -> None:
        if event.event_id in self._seen_event_ids:
            raise ValueError(f"duplicate event_id: {event.event_id!r}")

        key = (event.sim_time, -event.priority, _event_id_key(event.event_id))
        heapq.heappush(self._heap, (key, event))
        self._seen_event_ids.add(event.event_id)

    def pop(self) -> SimEvent:
        _, event = heapq.heappop(self._heap)
        return event

    def peek(self) -> SimEvent:
        return self._heap[0][1]

    def is_empty(self) -> bool:
        return not self._heap
