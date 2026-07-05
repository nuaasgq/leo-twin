from __future__ import annotations

import json

from leo_twin.models.orbit import AutoPlaneAllocator
from leo_twin.services.dashboard_information_architecture import (
    DASHBOARD_INFORMATION_ARCHITECTURE_V3_ID,
    dashboard_information_architecture_v3_to_dict,
)
from leo_twin.services.derived_summary import build_backend_derived_summary


def test_dashboard_information_architecture_v3_is_deterministic() -> None:
    first = dashboard_information_architecture_v3_to_dict()
    second = dashboard_information_architecture_v3_to_dict()

    assert first == second
    assert json.loads(json.dumps(first, sort_keys=True))["architecture_id"] == (
        DASHBOARD_INFORMATION_ARCHITECTURE_V3_ID
    )


def test_dashboard_information_architecture_v3_sections_are_complete() -> None:
    architecture = dashboard_information_architecture_v3_to_dict()
    sections = architecture["sections"]
    assert isinstance(sections, tuple)

    expected_order = (
        "OVERVIEW",
        "NETWORK",
        "BUSINESS",
        "COMPUTE",
        "NODE_DETAIL",
        "MODEL_ASSUMPTIONS",
        "DIAGNOSTICS",
    )
    assert tuple(section["section"] for section in sections) == expected_order
    assert architecture["layout_policy"]["primary_order"] == expected_order
    assert architecture["backend_source_of_truth"] is True
    assert architecture["frontend_policy"] == (
        "RENDER_BACKEND_SECTIONS_WITH_LOCAL_FORMATTING_ONLY"
    )
    assert "must not invent" in architecture["frontend_inference_policy"]

    priorities = [section["priority"] for section in sections]
    assert priorities == sorted(priorities)
    for section in sections:
        assert section["owner"] == "BACKEND_SUMMARY_CONTRACT"
        assert section["title_zh"]
        assert section["title_en"]
        assert section["purpose"]
        assert section["primary_data_sources"]
        assert section["runtime_status_fields"]
        assert section["detail_surfaces"]
        assert section["empty_state"]
        assert section["scale_behavior"]


def test_backend_summary_exposes_dashboard_information_architecture_v3() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=72, plane_count=12)

    summary = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=72,
        user_count=100,
        compute_node_count=72,
        compute_capacity=40.0,
        flow_count=24,
        demand_capacity=80.0,
        task_compute_demand=30.0,
        task_data_size=12.0,
        application_protocol="TASK_OFFLOAD_FLOW",
    )

    architecture = summary["dashboard_information_architecture_v3"]
    assert architecture == dashboard_information_architecture_v3_to_dict()
    assert architecture["architecture_id"] == DASHBOARD_INFORMATION_ARCHITECTURE_V3_ID
