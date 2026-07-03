from pathlib import Path

import pytest


@pytest.fixture
def valid_review_workspace(tmp_path: Path) -> Path:
    create_valid_review_workspace(tmp_path)
    return tmp_path


def create_valid_review_workspace(root: Path) -> None:
    files = {
        "pyproject.toml": "[project]\nname = \"sample\"\n",
        "src/leo_twin/core/kernel.py": (
            "from leo_twin.core.event_queue import EventQueue\n"
            "from leo_twin.schema.sim_event import SimEvent\n\n"
            "class SimulationKernel:\n"
            "    def __init__(self):\n"
            "        self._event_queue = EventQueue()\n"
            "        self._current_time = 0.0\n\n"
            "    def schedule_event(self, event: SimEvent):\n"
            "        self._event_queue.push(event)\n\n"
            "    def run(self):\n"
            "        while not self._event_queue.is_empty():\n"
            "            event = self._event_queue.pop()\n"
            "            self._current_time = event.sim_time\n\n"
            "    def get_current_time(self):\n"
            "        return self._current_time\n"
        ),
        "src/leo_twin/core/event_queue.py": (
            "import heapq\n\n"
            "class EventQueue:\n"
            "    def __init__(self):\n"
            "        self._heap = []\n\n"
            "    def push(self, event):\n"
            "        heapq.heappush(\n"
            "            self._heap,\n"
            "            ((event.sim_time, -event.priority, event.event_id), event),\n"
            "        )\n\n"
            "    def pop(self):\n"
            "        return heapq.heappop(self._heap)[1]\n\n"
            "    def peek(self):\n"
            "        return self._heap[0][1]\n\n"
            "    def is_empty(self):\n"
            "        return not self._heap\n"
        ),
        "src/leo_twin/core/simulation_module.py": (
            "class SimulationModule:\n"
            "    def name(self):\n"
            "        raise NotImplementedError\n\n"
            "    def on_event(self, event, kernel):\n"
            "        raise NotImplementedError\n"
        ),
        "src/leo_twin/schema/sim_event.py": (
            "from dataclasses import dataclass\n\n"
            "@dataclass(frozen=True)\n"
            "class SimEvent:\n"
            "    event_id: int\n"
            "    sim_time: float\n"
            "    priority: int\n"
            "    source: str\n"
            "    target: str\n"
            "    event_type: str\n"
            "    payload: dict\n"
        ),
        "tests/unit/test_kernel.py": (
            "def test_kernel_determinism_same_seed():\n"
            "    from leo_twin.core.kernel import SimulationKernel\n"
            "    from leo_twin.core.event_queue import EventQueue\n"
            "    assert SimulationKernel is SimulationKernel\n"
            "    assert EventQueue is EventQueue\n"
            "    assert ('same seed', 1) == ('same seed', 1)\n"
        ),
        "tests/integration/test_loop.py": (
            "def test_integration_placeholder():\n"
            "    assert True\n"
        ),
        "tests/scale/test_scale_placeholder.py": (
            "def test_scale_placeholder():\n"
            "    assert True\n"
        ),
    }
    for relative_path, content in files.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
