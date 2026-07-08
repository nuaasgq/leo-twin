from __future__ import annotations

from leo_twin.services.runtime_kpi_movement import (
    RUNTIME_KPI_MOVEMENT_SUMMARY_V1_ID,
    build_runtime_kpi_movement_summary_v1,
)


def test_runtime_kpi_movement_summary_reports_network_and_compute_movement() -> None:
    series = {
        "version": "v1",
        "samples": (
            _sample(0.0, throughput=120.0, loss=0.0, jitter=0.0, cpu_fp32=0.0),
            _sample(60.0, throughput=90.0, loss=0.12, jitter=0.02, cpu_fp32=35.0),
        ),
    }
    metrics = {
        "network_quality_metric_model": "FLOW_LEVEL_PROXY",
        "network_quality_effective_throughput_mbps": 90.0,
        "network_quality_effective_latency_avg_s": 0.05,
        "network_quality_effective_loss_proxy_rate": 0.12,
        "network_quality_effective_delay_variation_proxy_s": 0.02,
        "network_quality_requested_route_demand_mbps": 160.0,
        "network_quality_offered_route_capacity_mbps": 180.0,
        "compute_resource_used_gflops_fp32": 35.0,
        "compute_resource_used_gflops_fp64": 0.0,
        "compute_resource_used_gpu_tflops_fp32": 0.0,
        "compute_resource_used_gpu_tflops_fp16": 0.0,
        "compute_resource_used_npu_tops_int8": 0.0,
        "compute_resource_used_memory_gb": 0.0,
        "compute_resource_used_storage_gb": 0.0,
    }

    summary = build_runtime_kpi_movement_summary_v1(series, metrics)

    assert summary["version"] == "v1"
    assert summary["summary_id"] == RUNTIME_KPI_MOVEMENT_SUMMARY_V1_ID
    assert summary["source"] == "KPI_TIME_SERIES_V1_AND_METRICS_SUMMARY"
    assert summary["packet_level_simulation"] is False
    assert summary["frontend_inference_required"] is False
    assert summary["sample_count"] == 2
    assert summary["sim_time_span_s"] == 60.0
    assert summary["movement_status"] == "TIME_VARYING_OBSERVED"
    assert summary["metric_count"] == 11
    assert summary["observed_metric_count"] == 11
    assert summary["moving_metric_count"] == 4
    assert summary["network_moving_metric_count"] == 3
    assert summary["compute_moving_metric_count"] == 1
    assert summary["activity_context"]["active"] is True
    items = _items(summary)
    assert items["NETWORK_EFFECTIVE_THROUGHPUT"]["movement_status"] == "TIME_VARYING"
    assert items["NETWORK_EFFECTIVE_THROUGHPUT"]["absolute_delta"] == 30.0
    assert items["NETWORK_EFFECTIVE_LOSS_PROXY"]["endpoint_delta"] == 0.12
    assert items["COMPUTE_CPU_FP32_USED"]["movement_status"] == "TIME_VARYING"
    assert items["COMPUTE_GPU_FP32_USED"]["movement_status"] == "FLAT_ZERO"
    assert summary["summary_hash"].startswith("sha256:")


def test_runtime_kpi_movement_summary_reports_flat_under_activity() -> None:
    series = {
        "version": "v1",
        "samples": (
            _sample(0.0, throughput=100.0),
            _sample(30.0, throughput=100.0),
        ),
    }
    metrics = {
        "network_quality_metric_model": "FLOW_LEVEL_PROXY",
        "network_quality_effective_throughput_mbps": 100.0,
        "network_quality_effective_latency_avg_s": 0.05,
        "network_quality_effective_loss_proxy_rate": 0.0,
        "network_quality_effective_delay_variation_proxy_s": 0.0,
        "network_quality_requested_route_demand_mbps": 100.0,
        "network_quality_offered_route_capacity_mbps": 120.0,
    }

    summary = build_runtime_kpi_movement_summary_v1(series, metrics)

    assert summary["movement_status"] == "FLAT_UNDER_ACTIVITY"
    assert summary["moving_metric_count"] == 0
    assert summary["flat_metric_count"] == 11
    assert summary["zero_latest_metric_count"] == 9
    items = _items(summary)
    assert items["NETWORK_EFFECTIVE_THROUGHPUT"]["movement_status"] == "FLAT_NONZERO"
    assert items["NETWORK_EFFECTIVE_LOSS_PROXY"]["movement_status"] == "FLAT_ZERO"


def _sample(
    sim_time: float,
    *,
    throughput: float = 0.0,
    latency: float = 0.05,
    loss: float = 0.0,
    jitter: float = 0.0,
    cpu_fp32: float = 0.0,
) -> dict[str, float]:
    return {
        "sim_time": sim_time,
        "network_effective_throughput_mbps": throughput,
        "network_effective_latency_s": latency,
        "network_effective_loss_proxy_rate": loss,
        "network_effective_delay_variation_s": jitter,
        "network_requested_route_demand_mbps": 160.0 if throughput > 0.0 else 0.0,
        "network_offered_route_capacity_mbps": 180.0 if throughput > 0.0 else 0.0,
        "network_recent_flow_count": 2.0 if throughput > 0.0 else 0.0,
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
