from __future__ import annotations

from leo_twin.services.runtime_observability import build_runtime_lifecycle_summaries


def test_runtime_lifecycle_summaries_are_deterministic_and_backend_owned() -> None:
    snapshot = {
        "ground_users": [
            {"user_id": "user-1", "cell_id": "cell-b", "status": "ACTIVE"},
            {"user_id": "user-0", "cell_id": "cell-a", "status": "ACTIVE"},
        ],
        "satellites": [
            {"satellite_id": "sat-0", "status": "ACTIVE"},
            {"satellite_id": "sat-1", "status": "ACTIVE"},
        ],
        "links": [
            {"source_id": "sat-0", "target_id": "user-0", "availability": True},
            {"source_id": "sat-0", "target_id": "sat-1", "availability": True},
        ],
        "routes": [
            {
                "route_id": "route-b",
                "flow_id": "flow-b",
                "path": ["user-1", "sat-0", "sat-1", "service-0"],
                "latency": 0.2,
                "capacity": 40.0,
                "demand_capacity": 30.0,
                "loss_rate": 0.05,
                "available": False,
            },
            {
                "route_id": "route-a",
                "flow_id": "flow-a",
                "path": ["user-0", "sat-0", "compute-0"],
                "latency": 0.1,
                "capacity": 80.0,
                "demand_capacity": 60.0,
                "loss_rate": 0.01,
                "available": True,
            },
        ],
        "compute_nodes": [
            {
                "node_id": "sat-0",
                "capacity": 100.0,
                "available_capacity": 25.0,
                "status": "BUSY",
                "running_tasks": 2,
                "finished_tasks": 7,
                "gpu_tflops_fp32": 2.0,
                "used_gpu_tflops_fp32": 1.0,
            }
        ],
    }
    service_history = {
        "items": [
            {
                "task_id": "task-0",
                "input_flow_id": "flow-a",
                "complete": False,
                "total_latency_s": 0.31,
            }
        ]
    }
    kpi_slices = {
        "slices": [
            {
                "satellite_id": "sat-0",
                "compute_capacity_gflops_fp32": 100.0,
                "compute_used_gflops_fp32": 75.0,
                "compute_load_ratio": 0.75,
                "active_link_count": 2,
                "running_task_count": 2,
                "finished_task_count": 7,
            }
        ]
    }

    first = build_runtime_lifecycle_summaries(
        snapshot,
        service_latency_history=service_history,
        satellite_kpi_slices=kpi_slices,
    )
    second = build_runtime_lifecycle_summaries(
        snapshot,
        service_latency_history=service_history,
        satellite_kpi_slices=kpi_slices,
    )

    assert first == second
    assert first["user_request_summary_v1"] == {
        "version": "v1",
        "source": "BACKEND_RUNTIME_SNAPSHOT",
        "user_count": 2,
        "item_count": 2,
        "active_user_count": 2,
        "compute_service_user_count": 1,
        "waiting_user_count": 1,
        "hidden_user_count": 0,
        "items": (
            {
                "user_id": "user-0",
                "platform_type": "GROUND_USER_TERMINAL",
                "cell_id": "cell-a",
                "communication_route_count": 1,
                "available_route_count": 1,
                "compute_service_count": 1,
                "network_queue_count": 0,
                "selected_satellite_id": "sat-0",
                "destination_id": "compute-0",
                "status": "ACTIVE/AVAILABLE",
                "primary_route_id": "route-a",
                "primary_flow_id": "flow-a",
                "latency_s": 0.1,
                "capacity_mbps": 80.0,
                "loss_proxy_rate": 0.01,
                "service_state": "task-0/310ms/RUNNING",
                "path": ("user-0", "sat-0", "compute-0"),
            },
            {
                "user_id": "user-1",
                "platform_type": "GROUND_USER_TERMINAL",
                "cell_id": "cell-b",
                "communication_route_count": 1,
                "available_route_count": 0,
                "compute_service_count": 0,
                "network_queue_count": 1,
                "selected_satellite_id": "sat-0",
                "destination_id": "service-0",
                "status": "ACTIVE/WAITING_ROUTE",
                "primary_route_id": "route-b",
                "primary_flow_id": "flow-b",
                "latency_s": 0.2,
                "capacity_mbps": 40.0,
                "loss_proxy_rate": 0.05,
                "service_state": "",
                "path": ("user-1", "sat-0", "sat-1", "service-0"),
            },
        ),
    }
    assert first["satellite_service_summary_v1"]["items"][0] == {
        "satellite_id": "sat-0",
        "status": "BUSY",
        "service_user_ids": ("user-0", "user-1"),
        "next_hop_ids": ("compute-0", "sat-1"),
        "route_count": 2,
        "available_route_count": 1,
        "active_link_count": 2,
        "active_access_link_count": 1,
        "active_space_link_count": 1,
        "compute_load_ratio": 0.75,
        "compute_capacity_gflops_fp32": 100.0,
        "compute_used_gflops_fp32": 75.0,
        "compute_capacity_gflops_fp64": 0.0,
        "compute_used_gflops_fp64": 0.0,
        "compute_capacity_gpu_tflops_fp32": 2.0,
        "compute_used_gpu_tflops_fp32": 1.0,
        "compute_capacity_gpu_tflops_fp16": 0.0,
        "compute_used_gpu_tflops_fp16": 0.0,
        "compute_capacity_npu_tops_int8": 0.0,
        "compute_used_npu_tops_int8": 0.0,
        "compute_capacity_memory_gb": 0.0,
        "compute_used_memory_gb": 0.0,
        "compute_capacity_storage_gb": 0.0,
        "compute_used_storage_gb": 0.0,
        "running_task_count": 2,
        "finished_task_count": 7,
    }
