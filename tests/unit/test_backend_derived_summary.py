from __future__ import annotations

import pytest

from leo_twin.models.orbit import AutoPlaneAllocator, ConstellationProfile
from leo_twin.services.derived_summary import build_backend_derived_summary
from leo_twin.services.scale_fidelity import (
    ScaleFidelityConfig,
    build_scale_fidelity_summary,
)


def test_backend_derived_summary_is_deterministic_and_frontend_ready() -> None:
    allocation = AutoPlaneAllocator.allocate(
        satellite_count=300,
        profile=ConstellationProfile.STARLINK_SHELL_1_LIKE,
    )

    first = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=300,
        user_count=1000,
        compute_node_count=300,
        compute_capacity=10.0,
        flow_count=1200,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        arrival_interval_seconds=60,
        orbit_altitude_m=550_000.0,
        orbit_inclination_deg=53.0,
        phase_policy="TEST_PHASE_POLICY",
    )
    second = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=300,
        user_count=1000,
        compute_node_count=300,
        compute_capacity=10.0,
        flow_count=1200,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        arrival_interval_seconds=60,
        orbit_altitude_m=550_000.0,
        orbit_inclination_deg=53.0,
        phase_policy="TEST_PHASE_POLICY",
    )

    assert first == second
    assert first["derived_constellation_summary"] == {
        "profile": "STARLINK_SHELL_1_LIKE",
        "satellite_count": 300,
        "plane_count": 30,
        "satellites_per_plane": 10,
        "satellites_per_plane_distribution": [10] * 30,
        "total_slots": 300,
        "plane_count_explicit": False,
        "model_note": (
            "Approximate Starlink Shell 1-like plane allocation; "
            "not exact Starlink fidelity."
        ),
        "raan_spacing_deg": 12.0,
        "mean_anomaly_spacing_deg": 36.0,
        "phase_policy": "TEST_PHASE_POLICY",
        "altitude_m": 550_000.0,
        "orbital_period_minutes": pytest.approx(95.502118),
        "orbital_period_model_note": (
            "Simplified circular-orbit period estimate; no SGP4 or external ephemeris."
        ),
        "orbital_velocity_km_s": pytest.approx(7.588998),
        "orbital_velocity_model_note": (
            "Simplified circular-orbit speed estimate; no SGP4 or external ephemeris."
        ),
        "inclination_deg": 53.0,
    }
    assert first["traffic_demand_summary"] == {
        "traffic_class": "COMPUTE_SERVICE",
        "traffic_class_label": "通信-计算服务",
        "destination_type": "COMPUTE_NODE",
        "destination_type_label": "星上算力节点",
        "generated_flow_count": 1200,
        "generated_task_count": 1200,
        "generated_output_flow_metadata_count": 1200,
        "arrival_model": "DETERMINISTIC_INTERVAL",
        "source_selection_policy": "ROUND_ROBIN_GROUND_USERS",
        "destination_selection_policy": "ROUND_ROBIN_COMPUTE_NODES",
        "input_data_size_mb": 2.0,
        "output_data_size_mb": 0.0,
        "total_input_data_mb": 2400.0,
        "total_output_data_mb": 0.0,
        "priority": 0,
        "demand_capacity_mbps": 25.0,
        "task_compute_demand": 20.0,
        "service_mix_mode": "SINGLE_CLASS",
        "service_mix_weights": {
            "DATA_TRANSFER": 0.0,
            "TELEMETRY": 0.0,
            "BULK_DOWNLINK": 0.0,
            "COMPUTE_SERVICE": 1.0,
            "EMERGENCY": 0.0,
        },
        "service_mix_normalized_weights": {
            "DATA_TRANSFER": 0.0,
            "TELEMETRY": 0.0,
            "BULK_DOWNLINK": 0.0,
            "COMPUTE_SERVICE": 1.0,
            "EMERGENCY": 0.0,
        },
        "active_service_classes": ["COMPUTE_SERVICE"],
        "service_mix_generated_request_counts": {
            "DATA_TRANSFER": 0,
            "TELEMETRY": 0,
            "BULK_DOWNLINK": 0,
            "COMPUTE_SERVICE": 1200,
            "EMERGENCY": 0,
        },
        "execution_shape": "FLOW_THEN_COMPUTE_TASK",
        "execution_label": "输入流 + 计算任务",
        "requires_compute_node_destination": True,
        "compatibility_note": "通信-计算服务要求目的类型为星上算力节点。",
        "lifecycle_note": "输入流完成后触发计算任务；输出数据大小作为结果流元数据保留。",
        "arrival_interval_seconds": 60.0,
        "system_request_rate_per_minute": 1.0,
        "average_user_request_rate_per_minute": 0.001,
    }
    traffic_explanation = first["traffic_demand_explanation_v1"]
    assert traffic_explanation["explanation_id"] == (
        "leo_twin.traffic_demand_explanation.v1"
    )
    assert traffic_explanation["source"] == "backend_summary.traffic_demand_summary"
    assert traffic_explanation["request_count"] == 1200
    assert traffic_explanation["input_flow_count"] == 1200
    assert traffic_explanation["task_request_count"] == 1200
    assert traffic_explanation["output_flow_count"] == 1200
    assert traffic_explanation["communication_only_request_count"] == 0
    assert traffic_explanation["compute_service_request_count"] == 1200
    assert traffic_explanation["active_traffic_classes"] == ("COMPUTE_SERVICE",)
    assert traffic_explanation["arrival_window"] == {
        "first_arrival_time": 0.0,
        "last_arrival_time": 71940.0,
        "duration_seconds": 71940.0,
    }
    assert traffic_explanation["data_volume"] == {
        "total_input_data_mb": 2400.0,
        "total_output_data_mb": 0.0,
        "total_data_mb": 2400.0,
    }
    assert traffic_explanation["correlation_summary"] == {
        "all_compute_services_have_task": True,
        "all_compute_services_have_output_flow": True,
        "packet_level_simulation": False,
        "frontend_inference_required": False,
    }
    assert traffic_explanation["configured_request_count"] == 1200
    assert traffic_explanation["explained_request_count"] == 1200
    assert traffic_explanation["explanation_window_policy"] == "FULL_CONFIGURED_WINDOW"
    assert traffic_explanation["frontend_inference_required"] is False
    explanation_rows = {
        row["traffic_class"]: row
        for row in traffic_explanation["traffic_class_rows"]
        if isinstance(row, dict)
    }
    assert explanation_rows["COMPUTE_SERVICE"]["request_count"] == 1200
    assert explanation_rows["COMPUTE_SERVICE"]["destination_types"] == (
        "COMPUTE_NODE",
    )
    assert len(traffic_explanation["per_user_active_service_state"]) == 512
    assert first["compute_resource_summary"] == {
        "resource_model": "ComputeResourceVector",
        "node_role": "SATELLITE_HOSTED_COMPUTE",
        "compute_node_count": 300,
        "legacy_capacity_per_node": 10.0,
        "cpu_gflops_fp32_per_node": 10.0,
        "cpu_gflops_fp64_per_node": 0.0,
        "gpu_tflops_fp32_per_node": 0.0,
        "gpu_tflops_fp16_per_node": 0.0,
        "npu_tops_int8_per_node": 0.0,
        "memory_gb_per_node": 0.0,
        "storage_gb_per_node": 0.0,
        "total_cpu_gflops_fp32": 3000.0,
        "total_cpu_gflops_fp64": 0.0,
        "total_gpu_tflops_fp32": 0.0,
        "total_gpu_tflops_fp16": 0.0,
        "total_npu_tops_int8": 0.0,
        "total_memory_gb": 0.0,
        "total_storage_gb": 0.0,
        "capacity_unit": "GFLOPS FP32",
        "compatibility_note": "Legacy scalar capacity maps to cpu_gflops_fp32.",
    }
    cache_offload_migration = first["cache_offload_migration_contract_v1"]
    assert isinstance(cache_offload_migration, dict)
    assert cache_offload_migration["contract_id"] == (
        "leo_twin.cache_offload_migration_contract.v1"
    )
    assert cache_offload_migration["configured_observability"] == {
        "compute_node_count": 300,
        "cache_behavior_enabled": False,
        "offload_behavior_enabled": False,
        "migration_behavior_enabled": False,
        "observability_source": (
            "Future fields will be derived from service_latency_history_v1, "
            "compute_task_timeline_summary_v1, and node_detail_summary_v1."
        ),
    }
    assert tuple(
        item["action"] for item in cache_offload_migration["action_contracts"]
    ) == (
        "CACHE_LOOKUP",
        "CACHE_FILL",
        "TASK_OFFLOAD",
        "SERVICE_MIGRATION",
    )
    assert first["coverage_beam_summary"] == {
        "coverage_model": "DETERMINISTIC_GEOMETRIC_FOOTPRINT",
        "fidelity_level": "DISPLAY_APPROXIMATION",
        "selected_satellite_detail_mode": "SELECTED_SATELLITE_ONLY",
        "beam_pattern": "CENTER_PLUS_HEX_RING_VISUAL_APPROXIMATION",
        "footprint_intersection_policy": "VISUAL_GEOMETRIC_CONTAINMENT_ONLY",
        "default_beam_count": 7,
        "beam_radius_m": 160_000.0,
        "beam_length_m": 600_000.0,
        "global_beam_render_limit": 1,
        "excluded_physics": [
            "RF_PROPAGATION",
            "ANTENNA_PATTERN",
            "LINK_BUDGET",
            "INTERFERENCE",
        ],
        "model_note": (
            "Selected-satellite beam cells are deterministic visual footprints; "
            "no RF propagation or antenna-pattern simulation is performed."
        ),
        "intersection_note": (
            "Coverage/user intersections are deterministic geometric containment "
            "counts for visualization only; they are not access decisions."
        ),
    }
    scale_policy = first["scale_policy_v2"]
    assert isinstance(scale_policy, dict)
    assert scale_policy["policy_id"] == "leo_twin.scale_policy.v2"
    assert scale_policy["profile_targets"] == (72, 300, 1200, 3000, 6000, 12000)
    assert scale_policy["active_profile_id"] == "medium_300"
    assert scale_policy["active_scale_band"] == "MEDIUM_300"
    assert scale_policy["packet_level_simulation"] is False
    assert scale_policy["event_kernel_policy"] == "NO_EVENT_KERNEL_BEHAVIOR_CHANGE"
    lod_policy = first["lod_snapshot_policy_v2"]
    assert isinstance(lod_policy, dict)
    assert lod_policy["policy_id"] == "leo_twin.lod_snapshot_policy.v2"
    assert lod_policy["source_policy_id"] == "leo_twin.scale_policy.v2"
    assert lod_policy["active_profile_id"] == "medium_300"
    assert lod_policy["snapshot_lod_policy"] == (
        "BATCH_ORBIT_WITH_BOUNDED_RENDER_DETAIL"
    )
    assert lod_policy["cursor_required"] is False
    assert lod_policy["full_detail_allowed"] is False
    assert lod_policy["raw_count_policy"]["always_include_raw_counts"] is True
    assert any(
        "not exact Starlink fidelity" in assumption
        for assumption in first["model_assumptions"]
    )
    assert any(
        "Scale policy v2 classifies this scenario as MEDIUM_300" in assumption
        for assumption in first["model_assumptions"]
    )
    assert any(
        "LOD snapshot policy v2 uses HIDDEN_ROWS_REMAIN_WINDOWED" in assumption
        for assumption in first["model_assumptions"]
    )
    runtime_guardrails = first["runtime_guardrails_v2"]
    assert isinstance(runtime_guardrails, dict)
    assert runtime_guardrails["guardrail_id"] == "leo_twin.runtime_guardrails.v2"
    assert runtime_guardrails["active_profile_id"] == "medium_300"
    assert runtime_guardrails["decision"] == "DEGRADE"
    assert runtime_guardrails["source_policy_ids"] == {
        "scale_policy": "leo_twin.scale_policy.v2",
        "lod_snapshot_policy": "leo_twin.lod_snapshot_policy.v2",
    }
    assert runtime_guardrails["refusal_reasons"] == ()
    assert runtime_guardrails["estimates"]["event_volume"] > 0
    assert runtime_guardrails["estimates"]["stream_backlog"]["event_stream"][
        "cursor_required"
    ] is True
    assert any(
        "Runtime guardrails v2 classify pre-run execution as DEGRADE" in assumption
        for assumption in first["model_assumptions"]
    )
    detail_pagination = first["large_detail_pagination_contract_v2"]
    assert isinstance(detail_pagination, dict)
    assert detail_pagination["contract_id"] == (
        "leo_twin.large_detail_pagination_contract.v2"
    )
    assert detail_pagination["active_profile_id"] == "medium_300"
    detail_collections = {
        item["collection"]: item
        for item in detail_pagination["collections"]
        if isinstance(item, dict)
    }
    assert tuple(detail_collections) == (
        "ground_users",
        "satellites",
        "node_pressure",
        "routes",
        "services",
        "service_traces",
        "compute_nodes",
    )
    assert detail_collections["ground_users"]["endpoint"] == (
        "/runtime/details/users"
    )
    assert detail_collections["routes"]["endpoint"] == "/runtime/details/routes"
    assert detail_collections["services"]["estimated_total_count"] == 1200
    assert detail_collections["service_traces"]["endpoint"] == (
        "/runtime/details/service-traces"
    )
    assert detail_pagination["combined_node_endpoint"]["endpoint"] == (
        "/runtime/details/nodes"
    )
    assert any(
        "Large detail pagination contract v2 exposes 7 cursor-backed collections"
        in assumption
        for assumption in first["model_assumptions"]
    )
    assert any(
        "Coverage beams are bounded geometric visualization footprints" in assumption
        for assumption in first["model_assumptions"]
    )


@pytest.mark.parametrize(
    ("satellite_count", "plane_count", "profile", "expected_plane_count"),
    (
        (72, 12, ConstellationProfile.CUSTOM_WALKER, 12),
        (1200, 12, ConstellationProfile.CUSTOM_WALKER, 12),
        (1584, None, ConstellationProfile.STARLINK_SHELL_1_LIKE, 72),
    ),
)
def test_constellation_summary_is_deterministic_for_product_scales(
    satellite_count: int,
    plane_count: int | None,
    profile: ConstellationProfile,
    expected_plane_count: int,
) -> None:
    allocation = AutoPlaneAllocator.allocate(
        satellite_count=satellite_count,
        plane_count=plane_count,
        profile=profile,
    )

    first = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=satellite_count,
        user_count=20,
        compute_node_count=min(10, satellite_count),
        compute_capacity=10.0,
        flow_count=10,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        orbit_altitude_m=550_000.0,
        orbit_inclination_deg=53.0,
    )["derived_constellation_summary"]
    second = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=satellite_count,
        user_count=20,
        compute_node_count=min(10, satellite_count),
        compute_capacity=10.0,
        flow_count=10,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        orbit_altitude_m=550_000.0,
        orbit_inclination_deg=53.0,
    )["derived_constellation_summary"]

    assert first == second
    assert first["satellite_count"] == satellite_count
    assert first["plane_count"] == expected_plane_count
    assert sum(first["satellites_per_plane_distribution"]) == satellite_count
    assert len(first["satellites_per_plane_distribution"]) == expected_plane_count
    assert first["raan_spacing_deg"] == pytest.approx(360.0 / expected_plane_count)
    assert first["altitude_m"] == 550_000.0
    assert first["orbital_period_minutes"] == pytest.approx(95.502118)
    assert first["orbital_velocity_km_s"] == pytest.approx(7.588998)
    assert first["inclination_deg"] == 53.0
    assert first["phase_policy"] == "DETERMINISTIC_PLANE_SLOT_PHASE"


def test_compute_resource_summary_uses_configured_vector_lanes() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=12, plane_count=3)

    summary = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=12,
        user_count=20,
        compute_node_count=4,
        compute_capacity=40.0,
        flow_count=10,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        compute_cpu_gflops_fp64=8.0,
        compute_gpu_tflops_fp32=2.5,
        compute_gpu_tflops_fp16=5.0,
        compute_npu_tops_int8=12.0,
        compute_memory_gb=32.0,
        compute_storage_gb=512.0,
    )["compute_resource_summary"]

    assert summary["cpu_gflops_fp32_per_node"] == 40.0
    assert summary["cpu_gflops_fp64_per_node"] == 8.0
    assert summary["gpu_tflops_fp32_per_node"] == 2.5
    assert summary["gpu_tflops_fp16_per_node"] == 5.0
    assert summary["npu_tops_int8_per_node"] == 12.0
    assert summary["memory_gb_per_node"] == 32.0
    assert summary["storage_gb_per_node"] == 512.0
    assert summary["total_cpu_gflops_fp32"] == 160.0
    assert summary["total_cpu_gflops_fp64"] == 32.0
    assert summary["total_gpu_tflops_fp32"] == 10.0
    assert summary["total_gpu_tflops_fp16"] == 20.0
    assert summary["total_npu_tops_int8"] == 48.0
    assert summary["total_memory_gb"] == 128.0
    assert summary["total_storage_gb"] == 2048.0


def test_traffic_summary_uses_explicit_traffic_model_fields() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=12, plane_count=3)

    summary = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=12,
        user_count=20,
        compute_node_count=4,
        compute_capacity=40.0,
        flow_count=10,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        traffic_class="BULK_DOWNLINK",
        traffic_destination_type="GROUND_ENDPOINT",
        traffic_output_data_size=4.5,
    )["traffic_demand_summary"]

    assert summary["traffic_class"] == "BULK_DOWNLINK"
    assert summary["traffic_class_label"] == "批量下传"
    assert summary["destination_type"] == "GROUND_ENDPOINT"
    assert summary["destination_type_label"] == "地面端"
    assert summary["generated_flow_count"] == 10
    assert summary["generated_task_count"] == 0
    assert summary["generated_output_flow_metadata_count"] == 0
    assert summary["source_selection_policy"] == "ROUND_ROBIN_GROUND_USERS"
    assert summary["destination_selection_policy"] == "ROUND_ROBIN_GROUND_ENDPOINTS"
    assert summary["output_data_size_mb"] == 4.5
    assert summary["total_input_data_mb"] == 20.0
    assert summary["total_output_data_mb"] == 45.0
    assert summary["input_data_size_mb"] == 2.0
    assert summary["demand_capacity_mbps"] == 25.0
    assert summary["service_mix_mode"] == "SINGLE_CLASS"
    assert summary["service_mix_weights"] == {
        "DATA_TRANSFER": 0.0,
        "TELEMETRY": 0.0,
        "BULK_DOWNLINK": 1.0,
        "COMPUTE_SERVICE": 0.0,
        "EMERGENCY": 0.0,
    }
    assert summary["active_service_classes"] == ["BULK_DOWNLINK"]
    assert summary["service_mix_generated_request_counts"] == {
        "DATA_TRANSFER": 0,
        "TELEMETRY": 0,
        "BULK_DOWNLINK": 10,
        "COMPUTE_SERVICE": 0,
        "EMERGENCY": 0,
    }
    assert summary["execution_shape"] == "FLOW_ONLY"
    assert summary["execution_label"] == "流级网络业务"
    assert summary["requires_compute_node_destination"] is False
    assert summary["compatibility_note"] == "该业务类型按流级网络业务执行，不生成计算任务。"
    assert summary["lifecycle_note"] == "网络流完成即完成本次业务；不触发星上计算任务生命周期。"


def test_traffic_summary_exposes_weighted_service_mix() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=12, plane_count=3)

    summary = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=12,
        user_count=20,
        compute_node_count=4,
        compute_capacity=40.0,
        flow_count=10,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        traffic_data_transfer_weight=2.0,
        traffic_compute_service_weight=1.0,
    )["traffic_demand_summary"]

    assert summary["service_mix_mode"] == "WEIGHTED_MIX"
    assert summary["service_mix_weights"] == {
        "DATA_TRANSFER": 2.0,
        "TELEMETRY": 0.0,
        "BULK_DOWNLINK": 0.0,
        "COMPUTE_SERVICE": 1.0,
        "EMERGENCY": 0.0,
    }
    assert summary["service_mix_normalized_weights"]["DATA_TRANSFER"] == pytest.approx(
        2.0 / 3.0
    )
    assert summary["service_mix_normalized_weights"]["COMPUTE_SERVICE"] == pytest.approx(
        1.0 / 3.0
    )
    assert summary["active_service_classes"] == ["DATA_TRANSFER", "COMPUTE_SERVICE"]
    assert summary["service_mix_generated_request_counts"] == {
        "DATA_TRANSFER": 7,
        "TELEMETRY": 0,
        "BULK_DOWNLINK": 0,
        "COMPUTE_SERVICE": 3,
        "EMERGENCY": 0,
    }
    assert summary["generated_task_count"] == 3

    backend_summary = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=12,
        user_count=20,
        compute_node_count=4,
        compute_capacity=40.0,
        flow_count=10,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        traffic_data_transfer_weight=2.0,
        traffic_compute_service_weight=1.0,
    )
    explanation = backend_summary["traffic_demand_explanation_v1"]
    rows = {
        row["traffic_class"]: row
        for row in explanation["traffic_class_rows"]
        if isinstance(row, dict)
    }
    assert explanation["active_traffic_classes"] == (
        "DATA_TRANSFER",
        "COMPUTE_SERVICE",
    )
    assert explanation["request_count"] == 10
    assert explanation["input_flow_count"] == 10
    assert explanation["task_request_count"] == 3
    assert explanation["output_flow_count"] == 3
    assert explanation["communication_only_request_count"] == 7
    assert explanation["compute_service_request_count"] == 3
    assert explanation["configured_request_count"] == 10
    assert explanation["explained_request_count"] == 10
    assert rows["DATA_TRANSFER"]["request_count"] == 7
    assert rows["DATA_TRANSFER"]["destination_types"] == ("SERVICE_ENDPOINT",)
    assert rows["COMPUTE_SERVICE"]["request_count"] == 3
    assert rows["COMPUTE_SERVICE"]["task_request_count"] == 3
    assert rows["COMPUTE_SERVICE"]["output_flow_count"] == 3
    assert rows["COMPUTE_SERVICE"]["destination_types"] == ("COMPUTE_NODE",)
    assert explanation["frontend_inference_required"] is False


def test_traffic_summary_exposes_emergency_service_mix() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=12, plane_count=3)

    summary = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=12,
        user_count=20,
        compute_node_count=4,
        compute_capacity=40.0,
        flow_count=8,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="EMERGENCY_ALERT",
        traffic_class="EMERGENCY",
        traffic_destination_type="SERVICE_ENDPOINT",
        traffic_emergency_weight=2.0,
    )["traffic_demand_summary"]

    assert summary["traffic_class"] == "EMERGENCY"
    assert summary["traffic_class_label"] == "应急业务"
    assert summary["destination_type"] == "SERVICE_ENDPOINT"
    assert summary["service_mix_mode"] == "SINGLE_CLASS"
    assert summary["service_mix_weights"]["EMERGENCY"] == 2.0
    assert summary["active_service_classes"] == ["EMERGENCY"]
    assert summary["service_mix_generated_request_counts"] == {
        "DATA_TRANSFER": 0,
        "TELEMETRY": 0,
        "BULK_DOWNLINK": 0,
        "COMPUTE_SERVICE": 0,
        "EMERGENCY": 8,
    }
    assert summary["generated_task_count"] == 0
    assert summary["execution_shape"] == "FLOW_ONLY"


def test_traffic_summary_rejects_compute_service_non_compute_destination() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=12, plane_count=3)

    with pytest.raises(ValueError, match="COMPUTE_NODE"):
        build_backend_derived_summary(
            constellation=allocation,
            satellite_count=12,
            user_count=20,
            compute_node_count=4,
            compute_capacity=40.0,
            flow_count=10,
            demand_capacity=25.0,
            task_compute_demand=20.0,
            task_data_size=2.0,
            application_protocol="TASK_OFFLOAD_FLOW",
            traffic_class="COMPUTE_SERVICE",
            traffic_destination_type="GROUND_ENDPOINT",
        )


def test_configuration_explanation_v2_binds_config_to_backend_semantics() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=72, plane_count=12)

    first = build_backend_derived_summary(
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
        transport_protocol="TCP",
        routing_protocol="LINK_STATE",
        datalink_mac_protocol="TDMA",
        traffic_class="COMPUTE_SERVICE",
        traffic_destination_type="COMPUTE_NODE",
        compute_gpu_tflops_fp32=2.5,
        compute_npu_tops_int8=12.0,
        orbit_altitude_m=550_000.0,
        orbit_inclination_deg=53.0,
        runtime_mode="REAL_TIME",
        runtime_speed_factor=1.0,
        runtime_duration_seconds=600,
        runtime_seed=20260703,
    )["configuration_explanation_v2"]
    second = build_backend_derived_summary(
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
        transport_protocol="TCP",
        routing_protocol="LINK_STATE",
        datalink_mac_protocol="TDMA",
        traffic_class="COMPUTE_SERVICE",
        traffic_destination_type="COMPUTE_NODE",
        compute_gpu_tflops_fp32=2.5,
        compute_npu_tops_int8=12.0,
        orbit_altitude_m=550_000.0,
        orbit_inclination_deg=53.0,
        runtime_mode="REAL_TIME",
        runtime_speed_factor=1.0,
        runtime_duration_seconds=600,
        runtime_seed=20260703,
    )["configuration_explanation_v2"]

    assert first == second
    assert first["version"] == "v2"
    assert first["explanation_id"] == "leo_twin.configuration_explanation.v2"
    assert first["schema_id"] == "sees.user_configuration.v2"
    assert first["source"] == "BACKEND_DERIVED_SUMMARY"
    assert first["frontend_policy"] == "CONTROL_PANEL_KEY_FIELDS_ONLY"
    assert first["mutation_policy"] == "READ_ONLY_EXPLANATION"
    assert [surface["surface"] for surface in first["configuration_surfaces"]] == [
        "CONTROL_PANEL_KEY_FIELDS",
        "DETAILED_YAML_JSON_FILE",
        "APPROVED_TEMPLATE_CATALOG",
        "CURRENT_EFFECTIVE_CONFIG_EXPORT",
    ]
    sections = {
        section["section"]: section
        for section in first["section_explanations"]
    }
    assert tuple(sections) == ("scenario", "traffic", "network", "compute", "runtime", "ui")
    assert sections["scenario"]["current_values"]["satellite_count"] == 72
    assert sections["scenario"]["current_values"]["plane_count"] == 12
    assert sections["traffic"]["current_values"] == {
        "traffic_class": "COMPUTE_SERVICE",
        "destination_type": "COMPUTE_NODE",
        "generated_flow_count": 24,
        "generated_task_count": 24,
        "arrival_model": "DETERMINISTIC_INTERVAL",
        "service_mix_mode": "SINGLE_CLASS",
        "active_service_classes": ["COMPUTE_SERVICE"],
    }
    assert sections["network"]["current_values"] == {
        "application_protocol": "TASK_OFFLOAD_FLOW",
        "transport_protocol": "TCP",
        "routing_protocol": "LINK_STATE",
        "datalink_mac_protocol": "TDMA",
    }
    assert sections["compute"]["current_values"]["compute_node_count"] == 72
    assert sections["compute"]["current_values"]["gpu_tflops_fp32_per_node"] == 2.5
    assert sections["compute"]["current_values"]["npu_tops_int8_per_node"] == 12.0
    assert sections["runtime"]["current_values"] == {
        "runtime.mode": "REAL_TIME",
        "runtime.speed_factor": 1.0,
        "runtime.duration": 600.0,
        "runtime.seed": 20260703,
    }
    assert first["determinism"] == {
        "seed_source": "runtime.seed",
        "ordered_generation": True,
        "unknown_key_policy": "REJECT",
        "defaulting_policy": "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        "result_package_expectation": (
            "config snapshot, events.jsonl, metrics.csv, summary.json"
        ),
    }
    assert first["forbidden_integrations"] == ("STK", "EXATA", "AFSIM", "DDS")
    assert first["packet_level_simulation"] is False
    assert "not a mutable configuration API" in first["model_boundary_note"]


def test_scale_fidelity_summary_reports_large_scale_degradation() -> None:
    summary = build_scale_fidelity_summary(
        ScaleFidelityConfig(
            satellite_count=1200,
            user_count=20,
            space_link_enabled=True,
        )
    )

    assert summary == {
        "satellite_count": 1200,
        "user_count": 20,
        "orbit_update_mode": "BATCH",
        "metrics_mode": "AGGREGATED",
        "space_link_mode": "BOUNDED_CANDIDATE",
        "detailed_space_link_enabled": False,
        "space_link_candidate_policy": (
            "SAME_PLANE_AND_ADJACENT_PLANE_BOUNDED_CANDIDATES"
        ),
        "max_space_link_candidates_per_satellite": 4,
        "batch_space_link_update_limit": 999,
        "scale_limit_reason": (
            "orbit updates are batched; metrics are aggregated; "
            "detailed all-pairs space-space link updates are disabled because "
            "satellite_count=1200 exceeds batch_space_link_update_limit=999; "
            "bounded candidate updates are enabled with "
            "max_space_link_candidates_per_satellite=4"
        ),
        "current_scale_mode": "LARGE_SCALE_AGGREGATED",
        "fidelity_warnings": (
            "Orbit updates are batched to avoid per-satellite event flood.",
            "Metrics are aggregated for large-scale responsiveness.",
            "Space-space links use bounded candidate updates capped at "
            "4 candidates per satellite.",
        ),
    }
