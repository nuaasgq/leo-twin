import csv
import io
import json

from leo_twin.schema import (
    EventType,
    FlowState,
    LinkState,
    MetricRecord,
    Route,
    SatelliteState,
    SimEvent,
    TaskState,
)
from leo_twin.services.metrics import MetricsCollector


class _ScheduledEventSink:
    def __init__(self) -> None:
        self.events: list[SimEvent] = []

    def schedule_event(self, event: SimEvent) -> None:
        self.events.append(event)


def _event(
    event_id: str,
    sim_time: float,
    event_type: str,
    payload: object,
    source: str,
) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=sim_time,
        priority=0,
        source=source,
        target="metrics",
        event_type=event_type,
        payload=payload,
    )


def _sample_events() -> tuple[SimEvent, ...]:
    return (
        _event(
            "orbit-1",
            0.0,
            EventType.ORBIT_UPDATE,
            SatelliteState(
                satellite_id="sat-a",
                sim_time=0.0,
                position=(1.0, 2.0, 3.0),
                velocity=(0.0, 0.1, 0.2),
                status="online",
            ),
            "orbit",
        ),
        _event(
            "access-start-1",
            1.0,
            EventType.ACCESS_START,
            LinkState(
                source_id="sat-a",
                target_id="user-1",
                latency=10.0,
                capacity=50.0,
                availability=True,
            ),
            "network",
        ),
        _event(
            "link-update-1",
            1.5,
            EventType.LINK_UPDATE,
            LinkState(
                source_id="sat-a",
                target_id="user-1",
                latency=8.0,
                capacity=60.0,
                availability=True,
            ),
            "network",
        ),
        _event(
            "route-1",
            2.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route:flow-1",
                flow_id="flow-1",
                path=("user-1", "sat-a", "user-2"),
                latency=16.0,
                capacity=60.0,
                available=True,
            ),
            "network",
        ),
        _event(
            "flow-1",
            3.0,
            EventType.FLOW_COMPLETE,
            FlowState(
                flow_id="flow-1",
                route_id="route:flow-1",
                source_id="user-1",
                target_id="user-2",
                status="complete",
            ),
            "network",
        ),
        _event(
            "task-start-1",
            4.0,
            EventType.TASK_START,
            TaskState(
                task_id="task-1",
                node_id="sat-a",
                sim_time=4.0,
                progress=0.0,
                status="running",
            ),
            "compute",
        ),
        _event(
            "task-finish-1",
            5.0,
            EventType.TASK_FINISH,
            TaskState(
                task_id="task-1",
                node_id="sat-a",
                sim_time=5.0,
                progress=1.0,
                status="finished",
            ),
            "compute",
        ),
        _event(
            "access-end-1",
            6.0,
            EventType.ACCESS_END,
            LinkState(
                source_id="sat-a",
                target_id="user-1",
                latency=8.0,
                capacity=60.0,
                availability=False,
            ),
            "network",
        ),
    )


def test_metrics_collector_kpis_are_consistent_with_observations() -> None:
    collector = MetricsCollector()

    for event in _sample_events():
        collector.observe(event)

    summary = collector.summary()
    records = collector.records()

    assert summary["event_count"] == 8
    assert summary["unique_satellites"] == 1
    assert summary["observed_links"] == 1
    assert summary["active_link_capacity_avg"] == 0.0
    assert summary["active_link_capacity_max"] == 0.0
    assert summary["active_link_capacity_min"] == 0.0
    assert summary["active_link_latency_avg"] == 0.0
    assert summary["active_links"] == 0
    assert summary["available_link_capacity"] == 0.0
    assert summary["routes_total"] == 1
    assert summary["routes_available"] == 1
    assert summary["route_capacity_max"] == 60.0
    assert summary["route_capacity_min"] == 60.0
    assert summary["route_latency_avg"] == 16.0
    assert summary["route_latency_min"] == 16.0
    assert summary["completed_flows"] == 1
    assert summary["running_tasks"] == 0
    assert summary["finished_tasks"] == 1
    assert summary["last_sim_time"] == 6.0
    assert summary["events.ACCESS_START.count"] == 1
    assert summary["events.LINK_UPDATE.count"] == 1
    assert summary["events.TASK_FINISH.count"] == 1

    assert _last_record(records, "events.observed.count").value == float(summary["event_count"])
    assert _last_record(records, "links.active.count").value == float(summary["active_links"])
    assert _last_record(records, "links.available_capacity.total").value == summary[
        "available_link_capacity"
    ]
    assert _last_record(records, "routes.total.count").value == float(summary["routes_total"])
    assert _last_record(records, "routes.available.count").value == float(
        summary["routes_available"]
    )
    assert _last_record(records, "flows.completed.count").value == float(
        summary["completed_flows"]
    )
    assert _last_record(records, "tasks.running.count").value == float(summary["running_tasks"])
    assert _last_record(records, "tasks.finished.count").value == float(
        summary["finished_tasks"]
    )


def test_metrics_outputs_are_deterministic_and_have_expected_format(tmp_path) -> None:
    first = MetricsCollector()
    second = MetricsCollector()

    for event in _sample_events():
        first.observe(event)
        second.observe(event)

    assert first.records() == second.records()
    assert first.event_log() == second.event_log()
    assert first.metrics_csv() == second.metrics_csv()
    assert first.summary_json() == second.summary_json()
    assert first.events_jsonl() == second.events_jsonl()

    rows = list(csv.DictReader(io.StringIO(first.metrics_csv())))
    assert rows
    assert tuple(rows[0]) == ("sim_time", "metric_name", "entity_id", "value", "tags")
    assert rows[0] == {
        "sim_time": "0.0",
        "metric_name": "events.observed.count",
        "entity_id": "system",
        "value": "1.0",
        "tags": '{"event_type":"ORBIT_UPDATE","source":"orbit","target":"metrics"}',
    }
    assert json.loads(rows[0]["value"]) == 1.0
    assert json.loads(rows[0]["tags"]) == {
        "event_type": "ORBIT_UPDATE",
        "source": "orbit",
        "target": "metrics",
    }

    summary = json.loads(first.summary_json())
    assert summary == first.summary()
    assert first.summary_json().endswith("\n")

    replay_lines = first.events_jsonl().splitlines()
    first_replay_event = json.loads(replay_lines[0])
    assert first_replay_event == {
        "event_id": "orbit-1",
        "event_type": "ORBIT_UPDATE",
        "payload": {
            "position": [1.0, 2.0, 3.0],
            "satellite_id": "sat-a",
            "sim_time": 0.0,
            "status": "online",
            "velocity": [0.0, 0.1, 0.2],
        },
        "payload_type": "SatelliteState",
        "priority": 0,
        "sim_time": 0.0,
        "source": "orbit",
        "target": "metrics",
    }

    output_files = first.write_outputs(tmp_path)
    assert output_files["events"].read_text(encoding="utf-8") == first.events_jsonl()
    assert output_files["metrics"].read_text(encoding="utf-8") == first.metrics_csv()
    assert output_files["summary"].read_text(encoding="utf-8") == first.summary_json()


def test_metrics_on_event_emits_only_metric_sample_events() -> None:
    collector = MetricsCollector(emit_metric_events=True, metric_target="metrics-sink")
    sink = _ScheduledEventSink()
    observed = _sample_events()[1]

    collector.on_event(observed, sink)

    assert len(sink.events) == len(collector.records())
    assert {event.event_type for event in sink.events} == {EventType.METRIC_SAMPLE}
    assert {event.target for event in sink.events} == {"metrics-sink"}
    assert {event.source for event in sink.events} == {"metrics"}
    assert all(isinstance(event.payload, MetricRecord) for event in sink.events)
    assert not any(
        event.event_type
        in {
            EventType.ORBIT_UPDATE,
            EventType.ACCESS_START,
            EventType.ACCESS_END,
            EventType.LINK_UPDATE,
            EventType.ROUTE_UPDATE,
            EventType.FLOW_COMPLETE,
            EventType.TASK_START,
            EventType.TASK_FINISH,
        }
        for event in sink.events
    )


def _last_record(records: tuple[MetricRecord, ...], metric_name: str) -> MetricRecord:
    for record in reversed(records):
        if record.metric_name == metric_name:
            return record
    raise AssertionError(f"missing metric record: {metric_name}")
