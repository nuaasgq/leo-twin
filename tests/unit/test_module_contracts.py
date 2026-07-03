from pathlib import Path

from leo_twin.models.contracts import (
    ComputeModuleContract,
    MetricsModuleContract,
    NetworkModuleContract,
    OrbitModuleContract,
)
from leo_twin.schema import (
    EVENT_CONTRACTS,
    MODULE_DEPENDENCIES,
    EventType,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_event_contracts_freeze_required_event_types_and_payloads() -> None:
    contracts = {contract.event_type: contract for contract in EVENT_CONTRACTS}

    assert tuple(contracts) == tuple(EventType)
    assert contracts[EventType.ORBIT_TRIGGER].payload_schema == "None"
    assert contracts[EventType.ORBIT_UPDATE].payload_schema == "SatelliteState"
    assert contracts[EventType.ACCESS_START].payload_schema == "LinkState"
    assert contracts[EventType.ACCESS_END].payload_schema == "LinkState"
    assert contracts[EventType.LINK_UPDATE].payload_schema == "LinkState"
    assert contracts[EventType.FLOW_ARRIVAL].payload_schema == "FlowRequest"
    assert contracts[EventType.ROUTE_UPDATE].payload_schema == "Route"
    assert contracts[EventType.TASK_ARRIVAL].payload_schema == "TaskRequest"
    assert contracts[EventType.TASK_START].payload_schema == "TaskState"
    assert contracts[EventType.TASK_FINISH].payload_schema == "TaskState"
    assert contracts[EventType.METRIC_SAMPLE].payload_schema == "MetricRecord"


def test_module_dependency_contract_is_dag_and_has_no_peer_imports() -> None:
    graph: dict[str, set[str]] = {}
    for source, target in MODULE_DEPENDENCIES:
        graph.setdefault(source, set()).add(target)
        graph.setdefault(target, set())

    order = _topological_sort(graph)

    assert order[0] == "schema"
    assert set(order) == {"compute", "metrics", "network", "orbit", "schema"}
    assert all(target == "schema" for _, target in MODULE_DEPENDENCIES)


def test_formal_module_interfaces_define_required_methods_only() -> None:
    assert _contract_methods(OrbitModuleContract) == {"name", "on_event"}
    assert _contract_methods(NetworkModuleContract) == {
        "compute_access",
        "name",
        "on_event",
        "update_topology",
    }
    assert _contract_methods(ComputeModuleContract) == {"name", "on_event"}
    assert _contract_methods(MetricsModuleContract) == {
        "name",
        "on_event",
        "records",
        "summary",
    }


def test_contract_freeze_files_do_not_add_runtime_module_implementations() -> None:
    contract_files = [
        PROJECT_ROOT / "src/leo_twin/models/contracts.py",
        PROJECT_ROOT / "src/leo_twin/schema/events.py",
        PROJECT_ROOT / "src/leo_twin/schema/domain.py",
    ]
    forbidden_runtime_classes = (
        "class OrbitEngine",
        "class ComputeEngine",
        "class MetricsEngine",
    )

    for path in contract_files:
        text = path.read_text(encoding="utf-8")
        assert all(name not in text for name in forbidden_runtime_classes)


def _contract_methods(contract: type) -> set[str]:
    return {
        name
        for name, value in contract.__dict__.items()
        if callable(value) and not name.startswith("_")
    }


def _topological_sort(graph: dict[str, set[str]]) -> tuple[str, ...]:
    remaining = {node: set(dependencies) for node, dependencies in graph.items()}
    order: list[str] = []
    while remaining:
        ready = sorted(node for node, dependencies in remaining.items() if not dependencies)
        if not ready:
            raise AssertionError("dependency graph contains a cycle")
        for node in ready:
            order.append(node)
            del remaining[node]
        for dependencies in remaining.values():
            dependencies.difference_update(ready)
    return tuple(order)
