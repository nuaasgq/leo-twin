from __future__ import annotations

from pathlib import Path


def test_full_system_docs_track_current_runtime_capabilities() -> None:
    architecture = Path("docs/full_system_architecture.md").read_text(encoding="utf-8")
    roadmap = Path("docs/full_system_roadmap.md").read_text(encoding="utf-8")

    for term in (
        "J2SecularDriftProfile",
        "ApplicationRuntime",
        "DataLinkRuntime",
        "CSMA/CA",
    ):
        assert term in architecture

    for term in (
        "J2 secular drift",
        "orbit_propagation_model",
        "application.py",
        "datalink.py",
    ):
        assert term in roadmap
