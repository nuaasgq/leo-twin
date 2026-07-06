from __future__ import annotations

from leo_twin.services.runtime_observability import (
    build_runtime_compute_node_detail_item,
    build_runtime_compute_node_detail_page,
    build_runtime_compute_task_timeline_summary,
    build_runtime_route_detail_item,
    build_runtime_service_detail_page,
    build_runtime_service_detail_item,
    build_runtime_service_lifecycle_trace_v2,
    build_runtime_lifecycle_summaries,
    build_runtime_node_detail_page,
    build_runtime_route_explanation_summary,
    build_runtime_satellite_detail_card,
    build_runtime_satellite_service_summary,
    build_runtime_user_detail_card,
    build_runtime_user_request_summary,
)


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
                "compute_node_id": "sat-0",
                "service_placement_status": "QUEUED",
                "service_placement_policy": "MIN_ESTIMATED_FINISH_TIME",
                "service_placement_bottleneck_resource": "gpu_tflops_fp32",
                "service_placement_candidate_count": 3,
                "service_placement_capable_candidate_count": 2,
                "service_placement_candidate_queue_label": (
                    "sat-0:QUEUED/available=4s/q=1/finish=6s; "
                    "sat-1:PLACED/available=0s/q=0/finish=7s"
                ),
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
                "route_capacity_mbps": 120.0,
                "route_demand_mbps": 90.0,
                "route_latency_avg_s": 0.045,
                "route_delay_variation_proxy_s": 0.006,
                "route_loss_proxy_rate": 0.02,
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
    assert first["compute_task_timeline_summary_v1"]["task_count"] == 1
    assert first["compute_task_timeline_summary_v1"]["queued_task_count"] == 1
    assert first["service_lifecycle_trace_v2"]["service_count"] == 1
    assert first["service_lifecycle_trace_v2"]["items"][0]["service_id"] == "task-0"
    assert first["route_explanation_summary_v1"] == {
        "version": "v1",
        "source": "BACKEND_RUNTIME_SNAPSHOT",
        "summary_scope": "ROUTE_EXPLANATION_WINDOW",
        "cursor": 0,
        "limit": 500,
        "next_cursor": 2,
        "has_more": False,
        "route_count": 2,
        "item_count": 2,
        "available_route_count": 1,
        "blocked_route_count": 1,
        "over_demand_route_count": 0,
        "compute_service_route_count": 1,
        "network_service_route_count": 1,
        "items": (
            {
                "route_id": "route-b",
                "flow_id": "flow-b",
                "user_id": "user-1",
                "source_id": "user-1",
                "destination_id": "service-0",
                "selected_satellite_id": "sat-0",
                "primary_next_hop_id": "sat-0",
                "next_hop_ids": ("sat-0", "sat-1", "service-0"),
                "hop_count": 3,
                "path_label": "user-1 -> sat-0 -> sat-1 -> service-0",
                "available": False,
                "capacity_mbps": 40.0,
                "demand_mbps": 30.0,
                "latency_s": 0.2,
                "loss_proxy_rate": 0.05,
                "route_pressure_proxy": 1.0,
                "business_type": "DATA_TRANSFER",
                "business_label": "数据传输",
                "bottleneck_component": "AVAILABILITY",
                "bottleneck_reason": "ROUTE_UNAVAILABLE",
                "bottleneck_reason_label": "Route unavailable",
                "explanation_label": "route is unavailable in the current snapshot",
            },
            {
                "route_id": "route-a",
                "flow_id": "flow-a",
                "user_id": "user-0",
                "source_id": "user-0",
                "destination_id": "compute-0",
                "selected_satellite_id": "sat-0",
                "primary_next_hop_id": "sat-0",
                "next_hop_ids": ("sat-0", "compute-0"),
                "hop_count": 2,
                "path_label": "user-0 -> sat-0 -> compute-0",
                "available": True,
                "capacity_mbps": 80.0,
                "demand_mbps": 60.0,
                "latency_s": 0.1,
                "loss_proxy_rate": 0.01,
                "route_pressure_proxy": 0.75,
                "business_type": "COMPUTE_SERVICE",
                "business_label": "通信-计算服务",
                "bottleneck_component": "LOSS_PROXY",
                "bottleneck_reason": "ROUTE_LOSS_PROXY_POSITIVE",
                "bottleneck_reason_label": "Route loss proxy is positive",
                "explanation_label": "route has a positive flow-level loss proxy",
            },
        ),
    }
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
                "compute_node_id": "sat-0",
                "service_placement_status": "QUEUED",
                "service_placement_policy": "MIN_ESTIMATED_FINISH_TIME",
                "service_placement_bottleneck_resource": "gpu_tflops_fp32",
                "service_placement_candidate_count": 3,
                "service_placement_capable_candidate_count": 2,
                "service_placement_candidate_queue_label": (
                    "sat-0:QUEUED/available=4s/q=1/finish=6s; "
                    "sat-1:PLACED/available=0s/q=0/finish=7s"
                ),
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
        "route_capacity_mbps": 120.0,
        "route_demand_mbps": 90.0,
        "route_latency_avg_s": 0.045,
        "route_delay_variation_proxy_s": 0.006,
        "route_loss_proxy_rate": 0.02,
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
    node_detail_summary = first["node_detail_summary_v1"]
    assert node_detail_summary["version"] == "v1"
    assert node_detail_summary["source"] == "BACKEND_RUNTIME_STATUS"
    assert node_detail_summary["summary_scope"] == "VISIBLE_RUNTIME_DETAIL_ROWS"
    assert node_detail_summary["user_detail_count"] == 2
    assert node_detail_summary["satellite_detail_count"] == 2
    assert node_detail_summary["users"][0] == {
        "entity_type": "USER",
        "entity_id": "user-0",
        "title": "用户 user-0",
        "subtitle": "ACTIVE/AVAILABLE",
        "sections": (
            {
                "section_id": "identity",
                "title": "节点身份",
                "fields": (
                    {"label": "平台", "value": "Ground user terminal / cell-a", "tone": "normal"},
                    {"label": "通信", "value": "1 / 1 条路由 / 下一跳 sat-0", "tone": "normal"},
                ),
            },
            {
                "section_id": "business_path",
                "title": "业务链路",
                "fields": (
                    {"label": "目标卫星", "value": "sat-0", "tone": "normal"},
                    {"label": "目标节点", "value": "compute-0", "tone": "normal"},
                    {"label": "时延/容量", "value": "0.1 s / 80 Mbps", "tone": "normal"},
                    {
                        "label": "服务链路",
                        "value": (
                            "通信-计算服务 / Compute service active / task-0 / "
                            "task-0/310ms/RUNNING"
                        ),
                        "tone": "normal",
                    },
                    {
                        "label": "路径",
                        "value": "user-0 -> sat-0 -> compute-0",
                        "tone": "normal",
                    },
                ),
            },
            {
                "section_id": "compute_placement",
                "title": "计算与队列",
                "fields": (
                    {"label": "计算", "value": "1 条计算业务", "tone": "resource"},
                    {"label": "网络队列", "value": "队列空", "tone": "normal"},
                    {
                        "label": "服务放置",
                        "value": (
                            "节点 sat-0 / QUEUED / 策略 MIN_ESTIMATED_FINISH_TIME / "
                            "瓶颈 gpu_tflops_fp32 / 候选 2/3 / "
                            "队列 sat-0:QUEUED/available=4s/q=1/finish=6s; "
                            "sat-1:PLACED/available=0s/q=0/finish=7s"
                        ),
                        "tone": "resource",
                    },
                ),
            },
        ),
        "fields": (
            {"label": "平台", "value": "Ground user terminal / cell-a", "tone": "normal"},
            {"label": "通信", "value": "1 / 1 条路由 / 下一跳 sat-0", "tone": "normal"},
            {"label": "计算", "value": "1 条计算业务", "tone": "resource"},
            {"label": "网络队列", "value": "队列空", "tone": "normal"},
            {"label": "目标卫星", "value": "sat-0", "tone": "normal"},
            {"label": "目标节点", "value": "compute-0", "tone": "normal"},
            {
                "label": "服务放置",
                "value": (
                    "节点 sat-0 / QUEUED / 策略 MIN_ESTIMATED_FINISH_TIME / "
                    "瓶颈 gpu_tflops_fp32 / 候选 2/3 / "
                    "队列 sat-0:QUEUED/available=4s/q=1/finish=6s; "
                    "sat-1:PLACED/available=0s/q=0/finish=7s"
                ),
                "tone": "resource",
            },
            {"label": "时延/容量", "value": "0.1 s / 80 Mbps", "tone": "normal"},
            {
                "label": "服务链路",
                "value": (
                    "通信-计算服务 / Compute service active / task-0 / "
                    "task-0/310ms/RUNNING"
                ),
                "tone": "normal",
            },
            {
                "label": "路径",
                "value": "user-0 -> sat-0 -> compute-0",
                "tone": "normal",
            },
        ),
    }
    assert node_detail_summary["satellites"][0]["entity_id"] == "sat-0"
    assert node_detail_summary["satellites"][0]["fields"][0] == {
        "label": "负载",
        "value": "75%",
        "tone": "resource",
    }
    assert node_detail_summary["satellites"][0]["fields"][-1] == {
        "label": "网络",
        "value": "链路 2 / 接入 1 / 星间 1 / 路由 1/2 / 排队 1 / 时延 0.045 s / 损耗 2%",
        "tone": "normal",
    }
    assert [section["section_id"] for section in node_detail_summary["satellites"][0]["sections"]] == [
        "service_routing",
        "compute_resources",
        "network_state",
    ]
    node_page = build_runtime_node_detail_page(
        snapshot,
        service_latency_history=service_history,
        satellite_kpi_slices=kpi_slices,
        cursor=1,
        limit=2,
    )
    assert node_page["version"] == "v1"
    assert node_page["source"] == "BACKEND_RUNTIME_STATUS"
    assert node_page["summary_scope"] == "COMBINED_USER_SATELLITE_NODE_DETAIL_WINDOW"
    assert node_page["cursor"] == 1
    assert node_page["limit"] == 2
    assert node_page["next_cursor"] == 3
    assert node_page["has_more"] is True
    assert node_page["node_count"] == 4
    assert node_page["user_count"] == 2
    assert node_page["satellite_count"] == 2
    assert node_page["item_count"] == 2
    assert node_page["window_user_detail_count"] == 1
    assert node_page["window_satellite_detail_count"] == 1
    assert [item["entity_id"] for item in node_page["items"]] == ["user-1", "sat-0"]
    user_detail_card = build_runtime_user_detail_card(
        snapshot,
        "user-1",
        service_latency_history=service_history,
    )
    assert user_detail_card is not None
    assert user_detail_card["entity_type"] == "USER"
    assert user_detail_card["entity_id"] == "user-1"
    assert user_detail_card["fields"][0]["label"] == "平台"
    assert build_runtime_user_detail_card(snapshot, "missing-user") is None
    satellite_detail_card = build_runtime_satellite_detail_card(
        snapshot,
        "sat-0",
        service_latency_history=service_history,
        satellite_kpi_slices=kpi_slices,
    )
    assert satellite_detail_card is not None
    assert satellite_detail_card["entity_type"] == "SATELLITE"
    assert satellite_detail_card["entity_id"] == "sat-0"
    assert satellite_detail_card["fields"][0]["value"] == "75%"
    assert build_runtime_satellite_detail_card(snapshot, "missing-sat") is None
    route_detail_item = build_runtime_route_detail_item(
        snapshot,
        "route-a",
        service_latency_history=service_history,
    )
    assert route_detail_item is not None
    assert route_detail_item["route_id"] == "route-a"
    assert route_detail_item["business_type"] == "COMPUTE_SERVICE"
    assert build_runtime_route_detail_item(snapshot, "missing-route") is None
    service_detail_item = build_runtime_service_detail_item(service_history, "task-0")
    assert service_detail_item is not None
    assert service_detail_item["service_id"] == "task-0"
    assert service_detail_item["compute_node_id"] == "sat-0"
    assert build_runtime_service_detail_item(service_history, "missing-service") is None
    compute_node_detail_item = build_runtime_compute_node_detail_item(
        snapshot,
        "sat-0",
        satellite_kpi_slices=kpi_slices,
    )
    assert compute_node_detail_item is not None
    assert compute_node_detail_item["node_id"] == "sat-0"
    assert compute_node_detail_item["compute_used_gflops_fp32"] == 75.0
    assert build_runtime_compute_node_detail_item(snapshot, "missing-node") is None
    route_page = build_runtime_route_explanation_summary(
        snapshot,
        service_latency_history=service_history,
        cursor=1,
        limit=1,
    )
    assert route_page["cursor"] == 1
    assert route_page["limit"] == 1
    assert route_page["next_cursor"] == 2
    assert route_page["has_more"] is False
    assert route_page["item_count"] == 1
    assert route_page["items"][0]["route_id"] == "route-a"
    service_page = build_runtime_service_detail_page(
        service_history,
        cursor=0,
        limit=1,
    )
    assert service_page["summary_scope"] == "SERVICE_LIFECYCLE_DETAIL_WINDOW"
    assert service_page["service_count"] == 1
    assert service_page["queued_service_count"] == 1
    assert service_page["items"][0]["service_id"] == "task-0"
    assert service_page["items"][0]["compute_node_id"] == "sat-0"
    compute_node_page = build_runtime_compute_node_detail_page(
        snapshot,
        satellite_kpi_slices=kpi_slices,
        cursor=0,
        limit=1,
    )
    assert compute_node_page["summary_scope"] == "COMPUTE_NODE_DETAIL_WINDOW"
    assert compute_node_page["compute_node_count"] == 1
    assert compute_node_page["busy_compute_node_count"] == 1
    assert compute_node_page["items"][0]["node_id"] == "sat-0"
    assert compute_node_page["items"][0]["compute_used_gflops_fp32"] == 75.0


def test_compute_task_timeline_summary_is_backend_owned_and_deterministic() -> None:
    history = {
        "items": [
            {
                "task_id": "task-b",
                "compute_node_id": "sat-b",
                "service_placement_status": "PLACED",
                "service_placement_bottleneck_resource": "cpu_gflops_fp32",
                "complete": True,
                "first_sample_sim_time": 5.0,
                "last_sample_sim_time": 9.0,
                "compute_queue_delay_s": 0.0,
                "compute_execution_delay_s": 2.0,
                "total_latency_s": 6.0,
                "component_timeline": [
                    {
                        "component": "compute_execution",
                        "sample_sim_time": 7.0,
                        "duration_s": 2.0,
                    },
                    {
                        "component": "total",
                        "sample_sim_time": 9.0,
                        "duration_s": 6.0,
                    },
                ],
            },
            {
                "task_id": "task-a",
                "compute_node_id": "sat-a",
                "service_placement_status": "QUEUED",
                "service_placement_bottleneck_resource": "gpu_tflops_fp32",
                "complete": False,
                "first_sample_sim_time": 2.0,
                "last_sample_sim_time": 12.0,
                "compute_queue_delay_s": 3.0,
                "compute_execution_delay_s": 4.0,
                "total_latency_s": 0.0,
                "component_timeline": [
                    {
                        "component": "compute_queue",
                        "sample_sim_time": 6.0,
                        "duration_s": 3.0,
                    },
                    {
                        "component": "compute_execution",
                        "sample_sim_time": 10.0,
                        "duration_s": 4.0,
                    },
                    {
                        "component": "ignored_debug_stage",
                        "sample_sim_time": 11.0,
                        "duration_s": 1.0,
                    },
                ],
            },
        ],
    }

    first = build_runtime_compute_task_timeline_summary(history)
    second = build_runtime_compute_task_timeline_summary(history)

    assert first == second
    assert first["version"] == "v1"
    assert first["source"] == "SERVICE_LATENCY_HISTORY"
    assert first["summary_scope"] == "RECENT_COMPUTE_TASK_QUEUE_EXECUTION"
    assert first["task_count"] == 2
    assert first["item_count"] == 2
    assert first["complete_task_count"] == 1
    assert first["queued_task_count"] == 1
    assert first["total_compute_queue_delay_s"] == 3.0
    assert first["total_compute_execution_delay_s"] == 6.0
    assert first["avg_compute_queue_delay_s"] == 1.5
    assert first["avg_compute_execution_delay_s"] == 3.0
    assert first["items"][0] == {
        "task_id": "task-a",
        "compute_node_id": "sat-a",
        "placement_status": "QUEUED",
        "placement_bottleneck_resource": "gpu_tflops_fp32",
        "queue_delay_s": 3.0,
        "execution_delay_s": 4.0,
        "total_latency_s": 0.0,
        "complete": False,
        "queue_state": "QUEUED",
        "queue_state_label": "Compute queue waiting",
        "first_sample_sim_time": 2.0,
        "last_sample_sim_time": 12.0,
        "stage_count": 2,
        "stages": (
            {
                "component": "compute_queue",
                "label": "Compute queue",
                "sample_sim_time": 6.0,
                "duration_s": 3.0,
                "route_id": "",
            },
            {
                "component": "compute_execution",
                "label": "Compute execution",
                "sample_sim_time": 10.0,
                "duration_s": 4.0,
                "route_id": "",
            },
        ),
    }
    assert build_runtime_compute_task_timeline_summary(None)["task_count"] == 0


def test_service_lifecycle_trace_v2_is_backend_owned_and_deterministic() -> None:
    history = {
        "items": [
            {
                "task_id": "svc-02-compute_service-00000-task",
                "input_flow_id": "svc-02-compute_service-00000-input",
                "output_flow_id": "svc-02-compute_service-00000-output",
                "input_route_id": "route:input",
                "output_route_id": "route:output",
                "compute_node_id": "sat-a",
                "service_placement_status": "PLACED",
                "service_placement_policy": "MIN_ESTIMATED_FINISH_TIME",
                "service_placement_bottleneck_resource": "cpu_gflops_fp32",
                "complete": True,
                "first_sample_sim_time": 6.0,
                "last_sample_sim_time": 8.0,
                "input_network_latency_s": 3.0,
                "compute_queue_delay_s": 0.0,
                "compute_execution_delay_s": 2.0,
                "output_network_latency_s": 1.5,
                "total_latency_s": 6.5,
                "component_timeline": [
                    {
                        "component": "input_network",
                        "sample_sim_time": 6.0,
                        "duration_s": 3.0,
                        "input_flow_id": "svc-02-compute_service-00000-input",
                        "route_id": "route:input",
                    },
                    {
                        "component": "compute_queue",
                        "sample_sim_time": 6.0,
                        "duration_s": 0.0,
                        "route_id": "route:input",
                    },
                    {
                        "component": "compute_execution",
                        "sample_sim_time": 6.0,
                        "duration_s": 2.0,
                    },
                    {
                        "component": "output_network",
                        "sample_sim_time": 8.0,
                        "duration_s": 1.5,
                        "output_flow_id": "svc-02-compute_service-00000-output",
                        "route_id": "route:output",
                    },
                ],
            },
            {
                "task_id": "svc-01-compute_service-00000-task",
                "input_flow_id": "svc-01-compute_service-00000-input",
                "output_flow_id": "svc-01-compute_service-00000-output",
                "input_route_id": "route:pending-input",
                "compute_node_id": "sat-b",
                "complete": False,
                "last_sample_sim_time": 10.0,
                "input_network_latency_s": 4.0,
                "compute_queue_delay_s": 1.0,
                "compute_execution_delay_s": 2.5,
                "component_timeline": [
                    {
                        "component": "compute_execution",
                        "sample_sim_time": 10.0,
                        "duration_s": 2.5,
                    }
                ],
            },
        ],
    }

    first = build_runtime_service_lifecycle_trace_v2(history, cursor=0, limit=1)
    second = build_runtime_service_lifecycle_trace_v2(history, cursor=0, limit=1)

    assert first == second
    assert first["version"] == "v2"
    assert first["source_summary"] == "service_latency_history_v1"
    assert first["summary_scope"] == "SERVICE_LIFECYCLE_TRACE_WINDOW"
    assert first["service_count"] == 2
    assert first["trace_count"] == 1
    assert first["has_more"] is True
    assert first["complete_trace_count"] == 1
    assert first["running_trace_count"] == 1
    assert first["hidden_trace_count"] == 1
    trace = first["items"][0]
    assert trace["service_id"] == "svc-01-compute_service-00000"
    assert trace["terminal_state"] == "RUNNING"
    assert trace["terminal_state_reason"] == "OUTPUT_NETWORK_PENDING"
    assert trace["stage_count"] == 4
    assert trace["observed_stage_count"] == 3
    assert trace["pending_stage_count"] == 1
    assert trace["stages"][-1] == {
        "stage_index": 3,
        "stage_id": "svc-01-compute_service-00000:output_network",
        "component": "output_network",
        "stage_kind": "OUTPUT_NETWORK",
        "stage_label": "Output network",
        "stage_status": "PENDING",
        "sample_sim_time": 10.0,
        "duration_s": 0.0,
        "flow_id": "svc-01-compute_service-00000-output",
        "route_id": "",
        "compute_node_id": "",
    }
    complete = build_runtime_service_lifecycle_trace_v2(
        history,
        query="sat-a",
    )
    assert complete["trace_count"] == 1
    assert complete["items"][0]["terminal_state"] == "COMPLETE"
    assert complete["items"][0]["total_latency_s"] == 6.5


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


def test_runtime_detail_pages_apply_filters_before_cursor_pagination() -> None:
    snapshot = {
        "ground_users": [
            {"user_id": "user-0", "status": "ACTIVE"},
            {"user_id": "user-1", "status": "ACTIVE"},
        ],
        "satellites": [
            {"satellite_id": "sat-0", "status": "ACTIVE"},
            {"satellite_id": "sat-1", "status": "ACTIVE"},
        ],
        "compute_nodes": [
            {"node_id": "sat-0", "capacity": 100.0, "available_capacity": 80.0},
            {"node_id": "sat-1", "capacity": 100.0, "available_capacity": 30.0},
        ],
        "links": [
            {"source_id": "sat-0", "target_id": "user-0", "availability": True},
            {"source_id": "sat-1", "target_id": "user-1", "availability": True},
        ],
        "routes": [
            {
                "route_id": "route-compute",
                "flow_id": "flow-compute",
                "path": ["user-0", "sat-0", "compute-0"],
                "capacity": 80.0,
                "demand_capacity": 50.0,
                "available": True,
            },
            {
                "route_id": "route-blocked",
                "flow_id": "flow-data",
                "path": ["user-1", "sat-1", "service-1"],
                "capacity": 30.0,
                "demand_capacity": 20.0,
                "available": False,
            },
        ],
    }
    service_history = {
        "items": [
            {
                "task_id": "task-compute",
                "input_flow_id": "flow-compute",
                "compute_node_id": "sat-0",
            }
        ]
    }

    user_page = build_runtime_user_request_summary(
        snapshot,
        service_latency_history=service_history,
        query="user-1",
        cursor=0,
        limit=10,
    )
    assert user_page["summary_scope"] == "FILTERED_USER_SET_WITH_WINDOW_ITEMS"
    assert user_page["user_count"] == 1
    assert user_page["unfiltered_user_count"] == 2
    assert user_page["filter_query"] == "user-1"
    assert user_page["filter_applied"] is True
    assert user_page["items"][0]["user_id"] == "user-1"

    satellite_page = build_runtime_satellite_service_summary(
        snapshot,
        service_latency_history=service_history,
        query="sat-1",
        cursor=0,
        limit=10,
    )
    assert satellite_page["summary_scope"] == "FILTERED_SATELLITE_SET_WITH_WINDOW_ITEMS"
    assert satellite_page["satellite_count"] == 1
    assert satellite_page["unfiltered_satellite_count"] == 2
    assert satellite_page["filter_query"] == "sat-1"
    assert satellite_page["items"][0]["satellite_id"] == "sat-1"

    route_page = build_runtime_route_explanation_summary(
        snapshot,
        service_latency_history=service_history,
        query="sat-1",
        availability="BLOCKED",
        business_type="DATA_TRANSFER",
        bottleneck_component="AVAILABILITY",
        cursor=0,
        limit=10,
    )
    assert route_page["summary_scope"] == "FILTERED_ROUTE_EXPLANATION_WINDOW"
    assert route_page["route_count"] == 1
    assert route_page["unfiltered_route_count"] == 2
    assert route_page["available_route_count"] == 0
    assert route_page["blocked_route_count"] == 1
    assert route_page["filter_query"] == "sat-1"
    assert route_page["filter_availability"] == "BLOCKED"
    assert route_page["filter_business_type"] == "DATA_TRANSFER"
    assert route_page["filter_bottleneck_component"] == "AVAILABILITY"
    assert route_page["filter_applied"] is True
    assert route_page["items"][0]["route_id"] == "route-blocked"


def test_runtime_service_and_compute_detail_pages_apply_text_filters() -> None:
    service_page = build_runtime_service_detail_page(
        {
            "items": [
                {
                    "task_id": "task-a",
                    "input_flow_id": "flow-a",
                    "compute_node_id": "sat-0",
                    "complete": True,
                },
                {
                    "task_id": "task-b",
                    "input_flow_id": "flow-b",
                    "compute_node_id": "sat-1",
                    "compute_queue_delay_s": 0.5,
                    "complete": False,
                },
            ]
        },
        query="sat-1",
        cursor=0,
        limit=10,
    )
    assert service_page["summary_scope"] == "FILTERED_SERVICE_LIFECYCLE_DETAIL_WINDOW"
    assert service_page["service_count"] == 1
    assert service_page["unfiltered_service_count"] == 2
    assert service_page["filter_query"] == "sat-1"
    assert service_page["filter_applied"] is True
    assert service_page["queued_service_count"] == 1
    assert service_page["items"][0]["service_id"] == "task-b"

    compute_page = build_runtime_compute_node_detail_page(
        {
            "compute_nodes": [
                {
                    "node_id": "sat-0",
                    "status": "BUSY",
                    "capacity": 100.0,
                    "available_capacity": 10.0,
                },
                {
                    "node_id": "sat-1",
                    "status": "IDLE",
                    "capacity": 100.0,
                    "available_capacity": 100.0,
                },
            ]
        },
        query="busy",
        cursor=0,
        limit=10,
    )
    assert compute_page["summary_scope"] == "FILTERED_COMPUTE_NODE_DETAIL_WINDOW"
    assert compute_page["compute_node_count"] == 1
    assert compute_page["unfiltered_compute_node_count"] == 2
    assert compute_page["filter_query"] == "busy"
    assert compute_page["filter_applied"] is True
    assert compute_page["items"][0]["node_id"] == "sat-0"
