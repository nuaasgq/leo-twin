"""Product-facing network flow lifecycle summary v1."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


NETWORK_FLOW_LIFECYCLE_SUMMARY_V1_ID = "leo_twin.network_flow_lifecycle_summary.v1"

NetworkFlowLifecycleSummaryV1 = dict[str, object]


def build_network_flow_lifecycle_summary_v1(
    metrics: Mapping[str, Any],
) -> NetworkFlowLifecycleSummaryV1:
    """Build a backend-owned flow lifecycle summary from metrics_summary.

    This is a flow-level product summary. It does not infer packet-level state
    or replay events; it only exposes the runtime lifecycle window already
    maintained by MetricsCollector.
    """

    if not isinstance(metrics, Mapping):
        raise TypeError("metrics must be a mapping")

    active = _int(metrics.get("network_flow_lifecycle_active_flow_count"))
    active_available = _int(
        metrics.get("network_flow_lifecycle_active_available_flow_count")
    )
    active_blocked = _int(
        metrics.get("network_flow_lifecycle_active_blocked_flow_count")
    )
    completed = _int(metrics.get("network_flow_lifecycle_completed_flow_count"))
    successful = _int(metrics.get("network_flow_lifecycle_successful_flow_count"))
    failed = _int(metrics.get("network_flow_lifecycle_failed_flow_count"))
    payload: dict[str, object] = {
        "version": "v1",
        "summary_id": NETWORK_FLOW_LIFECYCLE_SUMMARY_V1_ID,
        "source": "METRICS_SUMMARY_NETWORK_FLOW_LIFECYCLE_FIELDS",
        "metrics_source": str(
            metrics.get(
                "network_flow_lifecycle_source",
                "BACKEND_METRICS_COLLECTOR",
            )
        ),
        "lifecycle_model": str(
            metrics.get(
                "network_flow_lifecycle_model",
                "ROUTE_UPDATE_TO_FLOW_COMPLETE_WINDOW",
            )
        ),
        "packet_level_simulation": bool(
            metrics.get("network_flow_lifecycle_packet_level_simulation") is True
        ),
        "frontend_inference_required": False,
        "active_flow_count": active,
        "active_available_flow_count": active_available,
        "active_blocked_flow_count": active_blocked,
        "active_demand_mbps": _float(
            metrics.get("network_flow_lifecycle_active_demand_mbps")
        ),
        "active_capacity_mbps": _float(
            metrics.get("network_flow_lifecycle_active_capacity_mbps")
        ),
        "active_latency_avg_s": _float(
            metrics.get("network_flow_lifecycle_active_latency_avg_s")
        ),
        "oldest_active_age_s": _float(
            metrics.get("network_flow_lifecycle_oldest_active_age_s")
        ),
        "completed_flow_count": completed,
        "successful_flow_count": successful,
        "failed_flow_count": failed,
        "lifecycle_status": _lifecycle_status(
            active=active,
            active_blocked=active_blocked,
            completed=completed,
            failed=failed,
        ),
        "model_assumptions": _model_assumptions(),
    }
    payload["summary_hash"] = stable_hash_payload(payload)
    return payload


def _lifecycle_status(
    *,
    active: int,
    active_blocked: int,
    completed: int,
    failed: int,
) -> str:
    if active_blocked > 0:
        return "ACTIVE_WITH_NETWORK_WAIT"
    if active > 0:
        return "ACTIVE"
    if failed > 0:
        return "COMPLETED_WITH_FAILURES"
    if completed > 0:
        return "COMPLETED"
    return "IDLE_NO_FLOW_SAMPLE"


def _model_assumptions() -> tuple[str, ...]:
    return (
        "Flow lifecycle state is derived from ROUTE_UPDATE and FLOW_COMPLETE observations.",
        "Active demand and capacity are flow-level route proxies, not packet queues.",
        "Packet-level behavior is not simulated.",
    )


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return max(0, int(value))


def _float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    if value != value or value in {float("inf"), float("-inf")}:
        return 0.0
    return float(value)


__all__ = [
    "NETWORK_FLOW_LIFECYCLE_SUMMARY_V1_ID",
    "NetworkFlowLifecycleSummaryV1",
    "build_network_flow_lifecycle_summary_v1",
]