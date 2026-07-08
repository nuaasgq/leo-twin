from __future__ import annotations

from leo_twin.services.result_package_contract import (
    build_runtime_export_compute_resource_pool_summary_v1,
)


def test_runtime_compute_resource_pool_summary_export_preserves_status_contract() -> None:
    status_summary = {
        "summary_id": "leo_twin.compute_resource_pool_summary.v1",
        "summary_hash": "sha256:pool",
        "node_count": 2,
        "dimension_count": 7,
        "active_dimension_count": 7,
        "consumed_dimension_count": 3,
        "saturated_dimension_count": 1,
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "dimensions": (
            {
                "resource": "cpu_gflops_fp32",
                "label": "CPU FP32 GFLOPS",
                "unit": "GFLOPS",
                "used": 10.0,
                "total": 20.0,
            },
        ),
    }

    export = build_runtime_export_compute_resource_pool_summary_v1(
        package_id="package-1",
        package_dir="exports/package-1",
        config_snapshot={
            "status": {"compute_resource_pool_summary_v1": status_summary},
        },
    )

    assert export["type"] == "RUNTIME_EXPORT_COMPUTE_RESOURCE_POOL_SUMMARY_V1"
    assert export["artifact_id"] == (
        "leo_twin.runtime_export_compute_resource_pool_summary.v1"
    )
    assert export["source"] == "BACKEND_RUNTIME_STATUS"
    assert export["compute_resource_pool_summary"] == status_summary
    assert export["evidence"]["source"] == (
        "runtime_status.compute_resource_pool_summary_v1"
    )
    assert export["evidence"]["summary_hash"] == "sha256:pool"
    assert export["evidence"]["node_count"] == 2
    assert export["evidence"]["dimension_count"] == 7
    assert export["evidence"]["packet_level_simulation"] is False
    assert export["evidence"]["frontend_inference_required"] is False
    assert export["evidence"]["evidence_hash"].startswith("sha256:")
    assert "cross-unit pie aggregation is not performed" in export["review_notes"]
    assert export["artifact_hash"].startswith("sha256:")
