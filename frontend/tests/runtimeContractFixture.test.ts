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
