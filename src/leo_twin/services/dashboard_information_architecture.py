"""Backend-owned dashboard information architecture contract."""

from __future__ import annotations


DASHBOARD_INFORMATION_ARCHITECTURE_V3_ID = (
    "leo_twin.dashboard_information_architecture.v3"
)


def dashboard_information_architecture_v3_to_dict() -> dict[str, object]:
    """Return the deterministic dashboard information architecture v3 contract."""

    section_order = (
        "OVERVIEW",
        "NETWORK",
        "BUSINESS",
        "COMPUTE",
        "NODE_DETAIL",
        "MODEL_ASSUMPTIONS",
        "DIAGNOSTICS",
    )
    return {
        "version": "v3",
        "architecture_id": DASHBOARD_INFORMATION_ARCHITECTURE_V3_ID,
        "source": "BACKEND_DERIVED_SUMMARY",
        "frontend_policy": "RENDER_BACKEND_SECTIONS_WITH_LOCAL_FORMATTING_ONLY",
        "backend_source_of_truth": True,
        "frontend_inference_policy": (
            "Frontend may sort, paginate, and format values, but must not invent "
            "business, network, compute, fidelity, or model-assumption semantics."
        ),
        "layout_policy": {
            "page_scroll": True,
            "primary_order": section_order,
            "section_grouping": (
                "overview first, then network/business/compute domains, then "
                "node detail, assumptions, and diagnostics"
            ),
            "card_policy": "no nested cards; sections and tables remain scan-friendly",
            "large_scale_policy": (
                "detail rows must be bounded, paginated, or virtualized before "
                "rendering large scenarios"
            ),
        },
        "sections": (
            _section(
                section="OVERVIEW",
                title_zh="总览",
                title_en="Overview",
                priority=10,
                purpose=(
                    "Show simulation time, run state, scale, event volume, "
                    "fidelity mode, and high-level health first."
                ),
                primary_data_sources=(
                    "RuntimeStatusPayload",
                    "WorldSnapshot.metrics_summary",
                    "backend_summary.fidelity_summary",
                    "runtime_export_history_v1",
                ),
                runtime_status_fields=(
                    "state",
                    "current_sim_time",
                    "duration",
                    "processed_event_count",
                    "metrics_summary.system",
                    "fidelity_summary",
                ),
                detail_surfaces=(
                    "runtime progress strip",
                    "scale and fidelity notice",
                    "core KPI cards",
                    "latest result package status",
                ),
                expected_controls=("time range", "export latest package"),
                empty_state="Waiting for initialized runtime status.",
                scale_behavior="Always visible; values are aggregated at large scale.",
            ),
            _section(
                section="NETWORK",
                title_zh="网络态势",
                title_en="Network",
                priority=20,
                purpose=(
                    "Explain throughput, latency, jitter, loss, routes, links, "
                    "and network model provenance."
                ),
                primary_data_sources=(
                    "metrics_summary.network",
                    "kpi_time_series_v1",
                    "network_quality_provenance_v1",
                    "route_explanation_summary_v1",
                    "network_model_contract_v2",
                ),
                runtime_status_fields=(
                    "metrics_summary.network",
                    "network_kpi_credibility_v1",
                    "network_quality_provenance_v1",
                    "route_explanation_summary_v1",
                ),
                detail_surfaces=(
                    "network KPI trends",
                    "route explanation table",
                    "link protocol summary",
                    "quality provenance and caveats",
                ),
                expected_controls=("route search", "KPI source filter"),
                empty_state="No network samples have been emitted yet.",
                scale_behavior=(
                    "Use aggregate KPI series and bounded route/link samples in "
                    "large-scale mode."
                ),
            ),
            _section(
                section="BUSINESS",
                title_zh="业务态势",
                title_en="Business",
                priority=30,
                purpose=(
                    "Show each user business request, service class, target "
                    "satellite, lifecycle stage, and service latency components."
                ),
                primary_data_sources=(
                    "traffic_demand_summary",
                    "user_request_summary_v1",
                    "user_request_history_v1",
                    "service_latency_history_v1",
                ),
                runtime_status_fields=(
                    "user_request_summary_v1",
                    "user_request_history_v1",
                    "service_latency_history_v1",
                ),
                detail_surfaces=(
                    "user business request table",
                    "service latency timeline",
                    "active request inspector",
                    "request generation explanation",
                ),
                expected_controls=("user search", "service class filter"),
                empty_state="No user business request is active in the current window.",
                scale_behavior="Use paginated user windows and retain raw counts.",
            ),
            _section(
                section="COMPUTE",
                title_zh="算力态势",
                title_en="Compute",
                priority=40,
                purpose=(
                    "Show satellite-hosted resource pools, task queue state, "
                    "bottleneck lanes, and compute execution timelines."
                ),
                primary_data_sources=(
                    "compute_resource_summary",
                    "compute_resource_contract_v2",
                    "metrics_summary.compute",
                    "compute_task_timeline_summary_v1",
                    "satellite_service_summary_v1",
                ),
                runtime_status_fields=(
                    "metrics_summary.compute",
                    "compute_task_timeline_summary_v1",
                    "satellite_service_summary_v1",
                    "satellite_kpi_history_v1",
                ),
                detail_surfaces=(
                    "compute resource pool chart",
                    "task timeline",
                    "top compute node table",
                    "single-satellite resource inspector",
                ),
                expected_controls=("resource lane selector", "satellite search"),
                empty_state="No compute task or resource update is available yet.",
                scale_behavior=(
                    "Rank top pressure nodes and paginate satellite resource rows."
                ),
            ),
            _section(
                section="NODE_DETAIL",
                title_zh="节点详情",
                title_en="Node Detail",
                priority=50,
                purpose=(
                    "Provide drill-down records for user nodes and satellite nodes "
                    "without overloading the overview."
                ),
                primary_data_sources=(
                    "runtime detail page endpoints",
                    "node_detail_summary_v1",
                    "user_request_summary_v1",
                    "satellite_service_summary_v1",
                ),
                runtime_status_fields=(
                    "node_detail_summary_v1",
                    "user_request_summary_v1",
                    "satellite_service_summary_v1",
                ),
                detail_surfaces=(
                    "user detail drawer",
                    "satellite detail drawer",
                    "paginated user table",
                    "paginated satellite table",
                ),
                expected_controls=("entity search", "previous/next page"),
                empty_state="Select or page to a node to inspect detailed state.",
                scale_behavior="Large scenarios must use backend windows or virtual tables.",
            ),
            _section(
                section="MODEL_ASSUMPTIONS",
                title_zh="模型假设",
                title_en="Model Assumptions",
                priority=60,
                purpose=(
                    "Make model boundaries, forbidden integrations, fidelity "
                    "degradation, and KPI credibility visible to users."
                ),
                primary_data_sources=(
                    "model_assumptions",
                    "configuration_explanation_v2",
                    "fidelity_summary",
                    "network_kpi_credibility_v1",
                ),
                runtime_status_fields=(
                    "fidelity_summary",
                    "network_kpi_credibility_v1",
                    "reproducibility_manifest_v1",
                ),
                detail_surfaces=(
                    "model assumptions panel",
                    "configuration semantics panel",
                    "fidelity notice",
                    "KPI credibility panel",
                ),
                expected_controls=("copy assumptions",),
                empty_state="Backend model assumptions have not been attached yet.",
                scale_behavior="Always visible when fidelity is reduced.",
            ),
            _section(
                section="DIAGNOSTICS",
                title_zh="诊断与复盘",
                title_en="Diagnostics",
                priority=70,
                purpose=(
                    "Expose reproducibility, result packages, health status, "
                    "warnings, and operator diagnostics."
                ),
                primary_data_sources=(
                    "reproducibility_manifest_v1",
                    "runtime_export_history_v1",
                    "runtime export catalog",
                    "launcher health summary",
                    "operator diagnostics bundle",
                ),
                runtime_status_fields=(
                    "reproducibility_manifest_v1",
                    "runtime_export_history_v1",
                    "warnings",
                ),
                detail_surfaces=(
                    "result package catalog",
                    "package compare and restore",
                    "diagnostics checklist",
                    "health and warning log",
                ),
                expected_controls=("export", "compare", "restore preflight"),
                empty_state="No completed run or diagnostics package is available.",
                scale_behavior="Keep logs bounded and link to exported artifacts.",
            ),
        ),
        "determinism": {
            "section_order": "priority_ascending_then_section_id",
            "unknown_section_policy": "display_after_known_sections_with_backend_label",
            "stable_identifiers": section_order,
        },
        "follow_up_tasks": (
            "V2-051 user detail drawer",
            "V2-052 satellite detail drawer",
            "V2-053 virtualized large tables",
            "V2-054 model assumptions panel",
        ),
    }


def _section(
    *,
    section: str,
    title_zh: str,
    title_en: str,
    priority: int,
    purpose: str,
    primary_data_sources: tuple[str, ...],
    runtime_status_fields: tuple[str, ...],
    detail_surfaces: tuple[str, ...],
    expected_controls: tuple[str, ...],
    empty_state: str,
    scale_behavior: str,
) -> dict[str, object]:
    return {
        "section": section,
        "title_zh": title_zh,
        "title_en": title_en,
        "priority": priority,
        "purpose": purpose,
        "primary_data_sources": primary_data_sources,
        "runtime_status_fields": runtime_status_fields,
        "detail_surfaces": detail_surfaces,
        "expected_controls": expected_controls,
        "empty_state": empty_state,
        "scale_behavior": scale_behavior,
        "owner": "BACKEND_SUMMARY_CONTRACT",
    }
