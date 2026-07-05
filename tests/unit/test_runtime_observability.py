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
                "input_route_id": "route-a",
                "output_route_id": "route-output",
                "complete": False,
                "input_network_latency_s": 0.1,
                "compute_queue_delay_s": 0.02,
                "compute_execution_delay_s": 0.18,
                "output_network_latency_s": 0.01,
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
        "summary_scope": "FULL_USER_SET_WITH_WINDOW_ITEMS",
        "cursor": 0,
        "limit": 1000,
        "next_cursor": 2,
        "has_more": False,
        "user_count": 2,
        "item_count": 2,
        "active_user_count": 2,
        "compute_service_user_count": 1,
        "waiting_user_count": 1,
        "window_user_count": 2,
        "window_active_user_count": 2,
        "window_compute_service_user_count": 1,
        "window_waiting_user_count": 1,
        "hidden_user_count": 0,
        "items": (
            {
                "user_id": "user-0",
                "platform_type": "GROUND_USER_TERMINAL",
                "platform_type_label": "Ground user terminal",
                "cell_id": "cell-a",
                "communication_route_count": 1,
                "available_route_count": 1,
                "compute_service_count": 1,
                "network_queue_count": 0,
                "network_queue_reason": "NO_QUEUE",
                "network_queue_reason_label": "No network queue",
                "selected_satellite_id": "sat-0",
                "destination_id": "compute-0",
                "status": "ACTIVE/AVAILABLE",
                "primary_route_id": "route-a",
                "primary_flow_id": "flow-a",
                "primary_next_hop_id": "sat-0",
                "route_hop_count": 2,
                "route_path_label": "user-0 -> sat-0 -> compute-0",
                "latency_s": 0.1,
                "capacity_mbps": 80.0,
                "loss_proxy_rate": 0.01,
                "service_state": "task-0/310ms/RUNNING",
                "service_task_id": "task-0",
                "service_complete": False,
                "service_total_latency_s": 0.31,
                "input_network_latency_s": 0.1,
                "compute_queue_delay_s": 0.02,
                "compute_execution_delay_s": 0.18,
                "output_network_latency_s": 0.01,
                "input_route_id": "route-a",
                "output_route_id": "route-output",
                "active_business_type": "COMPUTE_SERVICE",
                "active_business_label": "通信-计算服务",
                "request_state": "COMPUTE_SERVICE_ACTIVE",
                "request_state_label": "Compute service active",
                "path": ("user-0", "sat-0", "compute-0"),
            },
            {
                "user_id": "user-1",
                "platform_type": "GROUND_USER_TERMINAL",
                "platform_type_label": "Ground user terminal",
                "cell_id": "cell-b",
                "communication_route_count": 1,
                "available_route_count": 0,
                "compute_service_count": 0,
                "network_queue_count": 1,
                "network_queue_reason": "ROUTE_UNAVAILABLE",
                "network_queue_reason_label": "Route unavailable",
                "selected_satellite_id": "sat-0",
                "destination_id": "service-0",
                "status": "ACTIVE/WAITING_ROUTE",
                "primary_route_id": "route-b",
                "primary_flow_id": "flow-b",
                "primary_next_hop_id": "sat-0",
                "route_hop_count": 3,
                "route_path_label": "user-1 -> sat-0 -> sat-1 -> service-0",
                "latency_s": 0.2,
                "capacity_mbps": 40.0,
                "loss_proxy_rate": 0.05,
                "service_state": "",
                "service_task_id": "",
                "service_complete": False,
                "service_total_latency_s": None,
                "input_network_latency_s": None,
                "compute_queue_delay_s": None,
                "compute_execution_delay_s": None,
                "output_network_latency_s": None,
                "input_route_id": "",
                "output_route_id": "",
                "active_business_type": "DATA_TRANSFER",
                "active_business_label": "数据传输",
                "request_state": "NETWORK_WAITING",
                "request_state_label": "Waiting for network route",
                "path": ("user-1", "sat-0", "sat-1", "service-0"),
            },
        ),
    }
    assert first["satellite_service_summary_v1"][
        "summary_scope"
    ] == "FULL_SATELLITE_SET_WITH_WINDOW_ITEMS"
    assert first["satellite_service_summary_v1"]["cursor"] == 0
    assert first["satellite_service_summary_v1"]["limit"] == 1500
    assert first["satellite_service_summary_v1"]["next_cursor"] == 2
    assert first["satellite_service_summary_v1"]["has_more"] is False
    assert first["satellite_service_summary_v1"]["window_satellite_count"] == 2
    assert first["satellite_service_summary_v1"]["items"][0] == {
        "satellite_id": "sat-0",
        "status": "BUSY",
        "resource_role": "COMPUTE_NODE",
        "resource_role_label": "Satellite compute node",
        "service_user_ids": ("user-0", "user-1"),
        "service_user_count": 2,
        "primary_service_user_id": "user-0",
        "next_hop_ids": ("compute-0", "sat-1"),
        "next_hop_count": 2,
        "primary_next_hop_id": "compute-0",
        "primary_route_id": "route-a",
        "primary_flow_id": "flow-a",
        "route_count": 2,
        "available_route_count": 1,
        "network_queue_route_count": 1,
        "compute_service_route_count": 1,
        "network_service_route_count": 1,
        "route_mix_label": "compute=1; network=1; queued=1",
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


def test_runtime_user_summary_counts_full_set_when_items_are_limited() -> None:
    snapshot = {
        "ground_users": [
            {"user_id": "user-0", "status": "ACTIVE"},
            {"user_id": "user-1", "status": "ACTIVE"},
            {"user_id": "user-2", "status": "ACTIVE"},
        ],
        "routes": [
            {
                "route_id": "route-0",
                "flow_id": "flow-0",
                "path": ["user-0", "sat-0", "compute-0"],
                "available": True,
            },
            {
                "route_id": "route-1",
                "flow_id": "flow-1",
                "path": ["user-1", "sat-1", "service-0"],
                "available": False,
            },
            {
                "route_id": "route-2",
                "flow_id": "flow-2",
                "path": ["user-2", "sat-2", "compute-2"],
                "available": True,
            },
        ],
    }

    summary = build_runtime_lifecycle_summaries(
        snapshot,
        service_latency_history={"items": [{"task_id": "task-0", "input_flow_id": "flow-2"}]},
        user_limit=1,
    )["user_request_summary_v1"]

    assert summary["user_count"] == 3
    assert summary["cursor"] == 0
    assert summary["limit"] == 1
    assert summary["next_cursor"] == 1
    assert summary["has_more"] is True
    assert summary["item_count"] == 1
    assert summary["active_user_count"] == 3
    assert summary["compute_service_user_count"] == 2
    assert summary["waiting_user_count"] == 1
    assert summary["window_user_count"] == 1
    assert summary["window_active_user_count"] == 1
    assert summary["window_compute_service_user_count"] == 1
    assert summary["window_waiting_user_count"] == 0
    assert summary["hidden_user_count"] == 2
