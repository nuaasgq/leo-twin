from __future__ import annotations

import json

import pytest

from leo_twin.services.runtime_dashboard_kpi import (
    RUNTIME_DASHBOARD_KPI_V1_ID,
    build_runtime_dashboard_kpi_v1,
)
from leo_twin.services.runtime_kpi_movement import (
    build_runtime_kpi_movement_summary_v1,
)


def test_runtime_dashboard_kpi_prefers_tail_samples_for_current_values() -> None:
    series = {
        "samples": (
            _sample(0.0, throughput=120.0, loss=0.0, jitter=0.0, cpu_fp32=0.0),
            _sample(60.0, throughput=90.0, loss=0.0, jitter=0.0, cpu_fp32=35.0),
        )
    }
    metrics = _metrics(
        throughput=999.0,
        latency=0.07,
        loss=0.0,
        jitter=0.0,
        cpu_fp32=35.0,
    )
    movement = build_runtime_kpi_movement_summary_v1(series, metrics)
    dynamic = {
        "dynamic_status": "PARTIALLY_DYNAMIC",
        "items": (
            {
                "metric": "NETWORK_EFFECTIVE_LOSS_PROXY",
                "variation_status": "FLAT_ZERO",
                "visibility": "SHOW_ZERO_VALUE_REASON",
                "zero_value_note": "Backend loss proxy is zero in this window.",
            },
        ),
    }

    first = build_runtime_dashboard_kpi_v1(series, metrics, movement, dynamic)
    second = build_runtime_dashboard_kpi_v1(series, metrics, movement, dynamic)

    assert first == second
    assert first["summary_id"] == RUNTIME_DASHBOARD_KPI_V1_ID
    assert first["source"] == "KPI_TIME_SERIES_TAIL_AND_METRICS_SUMMARY"
    assert first["sample_count"] == 2
    assert first["tail_sample_time_s"] == 60.0
    assert first["metrics_summary_observation_time_s"] == 60.0
    assert first["metrics_summary_time_source"] == "RUNTIME_ADVANCE_TARGET"
    assert first["metric_count"] == 11
    assert first["observed_metric_count"] == 11
    assert first["packet_level_simulation"] is False
    assert first["frontend_inference_required"] is False
    assert str(first["summary_hash"]).startswith("sha256:")
    items = _items(first)
    throughput = items["NETWORK_EFFECTIVE_THROUGHPUT"]
    assert throughput["current_value"] == 90.0
    assert throughput["tail_sample_value"] == 90.0
    assert throughput["runtime_summary_value"] == 999.0
    assert throughput["value_source"] == "KPI_TAIL_SAMPLE"
    assert throughput["source_detail"] == {
        "source": "ACTIVE_FLOW_WINDOW",
        "source_label": "active flow window estimate",
    }
    loss = items["NETWORK_EFFECTIVE_LOSS_PROXY"]
    assert loss["current_value"] == 0.0
    assert loss["zero_value_note"] == "Backend loss proxy is zero in this window."
    assert json.loads(json.dumps(first, sort_keys=True))["summary_id"] == (
        RUNTIME_DASHBOARD_KPI_V1_ID
    )


def test_runtime_dashboard_kpi_falls_back_to_metrics_summary_without_tail_sample() -> None:
    metrics = _metrics(
        throughput=80.0,
        latency=0.04,
        loss=0.01,
        jitter=0.002,
        cpu_fp32=10.0,
    )

    summary = build_runtime_dashboard_kpi_v1(
        {"samples": ()},
        metrics,
        {"items": ()},
        {"items": ()},
    )

    assert summary["sample_count"] == 0
    assert summary["tail_sample_time_s"] is None
    assert summary["observed_metric_count"] == 11
    items = _items(summary)
    assert items["NETWORK_EFFECTIVE_THROUGHPUT"]["current_value"] == 80.0
    assert items["NETWORK_EFFECTIVE_THROUGHPUT"]["tail_sample_value"] is None
    assert items["NETWORK_EFFECTIVE_THROUGHPUT"]["value_source"] == "METRICS_SUMMARY"
    assert items["NETWORK_EFFECTIVE_LOSS_PROXY"]["current_value"] == 0.01
    assert items["COMPUTE_CPU_FP32_USED"]["current_value"] == 10.0


def test_runtime_dashboard_kpi_rejects_non_mapping_inputs() -> None:
    with pytest.raises(TypeError, match="kpi_time_series"):
        build_runtime_dashboard_kpi_v1(  # type: ignore[arg-type]
            object(),
            {},
            {},
            {},
        )
    with pytest.raises(TypeError, match="metrics_summary"):
        build_runtime_dashboard_kpi_v1(  # type: ignore[arg-type]
            {},
            object(),
            {},
            {},
        )


def _sample(
    sim_time: float,
    *,
    throughput: float,
    loss: float,
    jitter: float,
    cpu_fp32: float,
) -> dict[str, float | str]:
    return {
        "sim_time": sim_time,
        "network_effective_throughput_mbps": throughput,
        "network_effective_throughput_source": "ACTIVE_FLOW_WINDOW",
        "network_effective_throughput_source_label": "active flow window estimate",
        "network_effective_latency_s": 0.05,
        "network_effective_loss_proxy_rate": loss,
        "network_recent_loss_zero_reason": "NO_RECENT_FLOW_FAILURE",
        "network_recent_loss_zero_reason_label": "no recent failed flow",
        "network_effective_delay_variation_s": jitter,
        "network_recent_delay_variation_zero_reason": "NO_LATENCY_VARIATION",
        "network_recent_delay_variation_zero_reason_label": "latencies did not vary",
        "network_requested_route_demand_mbps": 120.0,
        "network_offered_route_capacity_mbps": 140.0,
        "compute_resource_used_gflops_fp32": cpu_fp32,
        "compute_resource_used_gflops_fp64": 0.0,
        "compute_resource_used_gpu_tflops_fp32": 0.0,
        "compute_resource_used_gpu_tflops_fp16": 0.0,
        "compute_resource_used_npu_tops_int8": 0.0,
        "compute_resource_used_memory_gb": 0.0,
        "compute_resource_used_storage_gb": 0.0,
    }


def _metrics(
    *,
    throughput: float,
    latency: float,
    loss: float,
    jitter: float,
    cpu_fp32: float,
) -> dict[str, float | str]:
    return {
        "network_quality_metric_model": "FLOW_LEVEL_PROXY",
        "network_quality_effective_throughput_mbps": throughput,
        "network_quality_effective_latency_avg_s": latency,
        "network_quality_effective_loss_proxy_rate": loss,
        "network_quality_effective_delay_variation_proxy_s": jitter,
        "network_quality_requested_route_demand_mbps": 120.0,
        "network_quality_offered_route_capacity_mbps": 140.0,
        "metrics_summary_event_time_s": 30.0,
        "metrics_summary_observation_time_s": 60.0,
        "metrics_summary_time_source": "RUNTIME_ADVANCE_TARGET",
        "compute_resource_used_gflops_fp32": cpu_fp32,
        "compute_resource_used_gflops_fp64": 0.0,
        "compute_resource_used_gpu_tflops_fp32": 0.0,
        "compute_resource_used_gpu_tflops_fp16": 0.0,
        "compute_resource_used_npu_tops_int8": 0.0,
        "compute_resource_used_memory_gb": 0.0,
        "compute_resource_used_storage_gb": 0.0,
    }


def _items(summary: dict[str, object]) -> dict[str, dict[str, object]]:
    items = summary["items"]
    assert isinstance(items, tuple)
    result: dict[str, dict[str, object]] = {}
    for item in items:
        assert isinstance(item, dict)
        result[str(item["metric"])] = item
    return result
