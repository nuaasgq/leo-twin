import { describe, expect, it } from "vitest";

import runtimeStatusFixture from "./fixtures/runtimeStatus.contract.json";
import { decodeRuntimeStatusEnvelope } from "../src/app/api";
import { RuntimeStatusEnvelope } from "../src/core/event_types";

describe("runtime status contract fixture", () => {
  it("decodes backend runtime status fields consumed by the frontend", () => {
    const envelope: RuntimeStatusEnvelope =
      decodeRuntimeStatusEnvelope(runtimeStatusFixture);
    const status = envelope.status;

    expect(status.status).toBe("RUNNING");
    expect(status.lifecycle_state).toBe("RUNNING");
    expect(status.fidelity_summary?.orbit_update_mode).toBe("BATCH");
    expect(status.fidelity_summary?.satellite_count).toBe(1200);
    expect(status.reproducibility_manifest_v1).toMatchObject({
      version: "v1",
      source: "BACKEND_RUNTIME_STATUS",
      manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
      session_id: "integration-demo-20260705",
      artifact_policy: "LIVE_STATUS_MANIFEST_ONLY",
      artifact_count: 4
    });
    expect(status.reproducibility_manifest_v1?.manifest_hash).toMatch(/^sha256:/);
    expect(status.reproducibility_manifest_v1?.runtime_state?.current_sim_time).toBe(120);
    expect(status.reproducibility_manifest_v1?.artifacts.map((item) => item.name)).toEqual([
      "config_snapshot.json",
      "events.jsonl",
      "metrics.csv",
      "summary.json"
    ]);
    expect(status.runtime_export_history_v1).toMatchObject({
      version: "v1",
      source: "BACKEND_RUNTIME_STATUS",
      history_scope: "CURRENT_SESSION_RECENT_EXPORTS",
      export_count: 1,
      retained_count: 1
    });
    expect(status.runtime_export_history_v1?.latest_export).toMatchObject({
      export_type: "ARCHIVE",
      archive_filename: "integration-demo-20260705-t00000120p000-e00004096.zip",
      current_sim_time: 120,
      processed_event_count: 4096
    });
    expect(status.stream_diagnostics_v1?.event_stream.next_cursor).toBe(42);
    expect(status.kpi_time_series_v1?.samples[0]).toMatchObject({
      sim_time: 120,
      network_effective_loss_proxy_rate: 0.05,
      network_effective_delay_variation_s: 0.006,
      compute_resource_used_gpu_tflops_fp32: 2.5,
      compute_resource_used_npu_tops_int8: 8
    });
    expect(status.network_quality_provenance_v1).toMatchObject({
      version: "v1",
      metric_model: "FLOW_LEVEL_PROXY",
      packet_level_simulation: false
    });
    expect(status.network_quality_provenance_v1?.sources.loss?.source).toBe(
      "PRESSURE_LOSS_PROXY"
    );
    expect(status.network_kpi_provenance_v2).toMatchObject({
      version: "v2",
      provenance_id: "leo_twin.network_kpi_provenance.v2",
      network_model_contract_id: "leo_twin.network_model_contract.v2",
      metric_model: "FLOW_LEVEL_PROXY",
      packet_level_simulation: false
    });
    expect(status.network_kpi_provenance_v2?.kpis[0]).toMatchObject({
      metric: "EFFECTIVE_THROUGHPUT",
      runtime_summary_key: "network_quality_effective_throughput_mbps",
      current_value: 180,
      packet_level_metric: false
    });
    expect(status.network_kpi_provenance_v2?.kpis[1].observed_source.source).toBe(
      "PRESSURE_LOSS_PROXY"
    );
    expect(status.metrics_summary).toMatchObject({
      service_latency_model: "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
      service_latency_task_count: 2,
      service_latency_total_avg_s: 7.4
    });
    expect(status.service_latency_history_v1?.items[0]).toMatchObject({
      task_id: "svc-00001-task",
      input_flow_id: "svc-00001-input",
      output_flow_id: "svc-00001-output",
      input_route_id: "route:svc-00001-input",
      output_route_id: "route:svc-00001-output",
      compute_node_id: "sat-00001",
      service_placement_status: "PLACED",
      service_placement_policy: "MIN_ESTIMATED_FINISH_TIME",
      service_placement_bottleneck_resource: "cpu_gflops_fp32",
      service_placement_candidate_count: 4,
      service_placement_capable_candidate_count: 4,
      service_placement_candidate_queue_label:
        "sat-00001:PLACED/available=0s/q=0/finish=124s",
      first_sample_sim_time: 120,
      last_sample_sim_time: 124,
      complete: true,
      total_latency_s: 7.4
    });
    expect(status.service_latency_history_v1?.items[0].component_timeline).toEqual([
      {
        component: "input_network",
        metric_name: "service.input_network_latency",
        sample_sim_time: 120,
        duration_s: 4,
        input_flow_id: "svc-00001-input",
        route_id: "route:svc-00001-input"
      },
      {
        component: "compute_queue",
        metric_name: "service.compute_queue_delay",
        sample_sim_time: 121,
        duration_s: 0,
        input_flow_id: "svc-00001-input",
        route_id: "route:svc-00001-input"
      },
      {
        component: "compute_execution",
        metric_name: "service.compute_execution_delay",
        sample_sim_time: 122,
        duration_s: 2,
        input_flow_id: "svc-00001-input",
        route_id: "route:svc-00001-input"
      },
      {
        component: "output_network",
        metric_name: "service.output_network_latency",
        sample_sim_time: 124,
        duration_s: 1.4,
        input_flow_id: "svc-00001-input",
        output_flow_id: "svc-00001-output",
        route_id: "route:svc-00001-output"
      },
      {
        component: "total",
        metric_name: "service.total_latency",
        sample_sim_time: 124,
        duration_s: 7.4,
        input_flow_id: "svc-00001-input",
        output_flow_id: "svc-00001-output",
        route_id: "route:svc-00001-output"
      }
    ]);
    expect(status.compute_task_timeline_summary_v1).toMatchObject({
      version: "v1",
      source: "SERVICE_LATENCY_HISTORY",
      task_count: 1,
      queued_task_count: 0,
      total_compute_execution_delay_s: 2
    });
    expect(status.compute_task_timeline_summary_v1?.items[0]).toMatchObject({
      task_id: "svc-00001-task",
      compute_node_id: "sat-00001",
      queue_state: "NO_QUEUE",
      stage_count: 2
    });
    expect(status.node_detail_summary_v1).toMatchObject({
      version: "v1",
      source: "BACKEND_RUNTIME_STATUS",
      user_detail_count: 1,
      satellite_detail_count: 1
    });
    expect(status.node_detail_summary_v1?.users[0]).toMatchObject({
      entity_type: "USER",
      entity_id: "user-00001",
      title: "用户 user-00001"
    });
    expect(status.node_detail_summary_v1?.users[0].sections?.[0]).toMatchObject({
      section_id: "compute_placement",
      title: "计算与队列",
      fields: [
        {
          label: "服务放置",
          value: "节点 sat-00001 / PLACED / 瓶颈 cpu_gflops_fp32 / 候选 4/4",
          tone: "resource"
        }
      ]
    });
    expect(status.node_detail_summary_v1?.users[0].fields).toEqual([
      {
        label: "服务放置",
        value: "节点 sat-00001 / PLACED / 瓶颈 cpu_gflops_fp32 / 候选 4/4",
        tone: "resource"
      },
      {
        label: "路径",
        value: "user-00001 -> sat-00001 -> compute-00001",
        tone: "normal"
      }
    ]);
    expect(status.node_detail_summary_v1?.satellites[0].fields[0]).toEqual({
      label: "负载",
      value: "65%",
      tone: "resource"
    });
    expect(status.node_detail_summary_v1?.satellites[0].sections?.[1].title).toBe(
      "网络状态"
    );
    expect(status.satellite_kpi_slices_v1?.slices[0]).toMatchObject({
      satellite_id: "sat-00001",
      active_link_count: 4,
      route_loss_proxy_rate: 0.025,
      compute_used_gpu_tflops_fp32: 1.5,
      compute_used_npu_tops_int8: 6,
      compute_used_memory_gb: 10,
      compute_load_ratio: 0.65
    });
    expect(status.satellite_kpi_history_v1?.series[0]).toMatchObject({
      satellite_id: "sat-00001",
      sample_count: 2
    });
    expect(status.satellite_kpi_history_v1?.series[0].samples[1]).toMatchObject({
      sim_time: 120,
      compute_load_ratio: 0.65,
      compute_used_gpu_tflops_fp32: 1.5,
      compute_used_npu_tops_int8: 6
    });
  });

  it("keeps generated config backend summaries aligned with frontend types", () => {
    const envelope = decodeRuntimeStatusEnvelope(runtimeStatusFixture);
    const generated = envelope.generated_config;

    expect(generated?.satellite_count).toBe(1200);
    expect(generated?.transport_protocol).toBe("UDP");
    expect(generated?.backend_summary?.fidelity_summary?.space_link_mode).toBe(
      "BOUNDED_CANDIDATE"
    );
    expect(generated?.backend_summary?.compute_resource_summary).toMatchObject({
      resource_model: "ComputeResourceVector",
      node_role: "SATELLITE_HOSTED_COMPUTE",
      gpu_tflops_fp32_per_node: 2.5,
      npu_tops_int8_per_node: 12
    });
    expect(generated?.backend_summary?.compute_resource_contract_v2).toMatchObject({
      contract_id: "leo_twin.compute_resource_contract.v2",
      resource_model: "ComputeResourceVector",
      node_role: "SATELLITE_HOSTED_COMPUTE"
    });
    expect(
      generated?.backend_summary?.compute_resource_contract_v2?.resource_lanes[0]
    ).toMatchObject({
      lane: "CPU_FP32",
      capacity_field: "compute_capacity",
      compatibility_role: "legacy_scalar_capacity"
    });
    expect(
      generated?.backend_summary?.compute_resource_contract_v2?.configured_node_profile
        ?.compute_node_count
    ).toBe(1200);
    expect(generated?.backend_summary?.service_placement_contract_v2).toMatchObject({
      contract_id: "leo_twin.service_placement_contract.v2",
      default_policy: "MIN_ESTIMATED_FINISH_TIME",
      placement_model: "DETERMINISTIC_MIN_ESTIMATED_FINISH_TIME"
    });
    expect(
      generated?.backend_summary?.service_placement_contract_v2?.configured_policy
        ?.compute_node_count
    ).toBe(1200);
    expect(generated?.backend_summary?.configuration_explanation_v2).toMatchObject({
      version: "v2",
      explanation_id: "leo_twin.configuration_explanation.v2",
      schema_id: "sees.user_configuration.v2",
      source: "BACKEND_DERIVED_SUMMARY",
      frontend_policy: "CONTROL_PANEL_KEY_FIELDS_ONLY",
      mutation_policy: "READ_ONLY_EXPLANATION",
      packet_level_simulation: false
    });
    expect(
      generated?.backend_summary?.configuration_explanation_v2?.section_explanations.map(
        (section) => section.section
      )
    ).toEqual(["scenario", "runtime"]);
    expect(
      generated?.backend_summary?.configuration_explanation_v2?.determinism
        .unknown_key_policy
    ).toBe("REJECT");
  });

  it("rejects malformed runtime status envelopes before UI consumption", () => {
    expect(() => decodeRuntimeStatusEnvelope({ status: null })).toThrow(
      "runtime status response must include status object"
    );
    expect(() => decodeRuntimeStatusEnvelope({ status: {}, generated_config: [] })).toThrow(
      "generated scenario config must be an object"
    );
  });
});
