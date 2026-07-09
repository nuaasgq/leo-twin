import { describe, expect, it } from "vitest";

import {
  buildDataPanelExecutableReadinessDisplay,
  buildDataPanelTrafficBusinessActivityDisplay
} from "../src/dashboard/data_panel/DataPanel";

describe("data panel v2 executable readiness display", () => {
  it("surfaces backend ready status without frontend inference", () => {
    const display = buildDataPanelExecutableReadinessDisplay({
      version: "v1",
      readiness_id: "ready-1",
      source: "runtime.v2_executable_readiness_v1",
      target: "industrial-v2-demo-loop",
      readiness_status: "READY",
      executable_ready: true,
      gate_count: 8,
      passed_gate_count: 8,
      failed_gate_count: 0,
      gates: [
        {
          gate_id: "runtime",
          label: "runtime session",
          status: "PASS",
          required_paths: ["/runtime/status"],
          missing_paths: [],
          issue_count: 0,
          issues: [],
          evidence: [{ path: "/runtime/status", present: true, value_summary: "ok" }]
        }
      ],
      missing_required_gate_ids: [],
      frontend_inference_required: false,
      packet_level_simulation: false,
      operator_next_action: "继续运行 72/300/1200 标准场景验收",
      readiness_hash: "abcdef1234567890"
    });

    expect(display).not.toBeNull();
    expect(display?.tone).toBe("match");
    expect(display?.statusLabel).toBe("已就绪");
    expect(display?.summaryLabel).toBe("8 / 8 gates passed");
    expect(display?.sourceLabel).toBe("runtime.v2_executable_readiness_v1");
    expect(display?.issueLabels).toEqual([]);
    expect(display?.metaLabels).toContain("frontend inference not required");
    expect(display?.metaLabels).toContain(
      "配置、运行时、业务、网络、算力、节点详情、fidelity、复现导出 gate 均通过"
    );
  });

  it("lists failed backend readiness gates as actionable issues", () => {
    const display = buildDataPanelExecutableReadinessDisplay({
      version: "v1",
      readiness_id: "blocked-1",
      source: "runtime.v2_executable_readiness_v1",
      target: "industrial-v2-demo-loop",
      readiness_status: "BLOCKED",
      executable_ready: false,
      gate_count: 8,
      passed_gate_count: 7,
      failed_gate_count: 1,
      gates: [
        {
          gate_id: "export",
          label: "复现导出",
          status: "FAIL",
          required_paths: ["artifacts/summary.json"],
          missing_paths: ["artifacts/summary.json"],
          issue_count: 1,
          issues: ["export package not generated"],
          evidence: [{ path: "artifacts/summary.json", present: false, value_summary: null }]
        }
      ],
      missing_required_gate_ids: ["export"],
      frontend_inference_required: false,
      packet_level_simulation: false,
      operator_next_action: "生成复现实验包"
    });

    expect(display?.tone).toBe("error");
    expect(display?.statusLabel).toBe("未就绪");
    expect(display?.issueLabels).toEqual([
      "复现导出: missing artifacts/summary.json / export package not generated"
    ]);
  });
});

describe("data panel traffic business activity display", () => {
  it("surfaces backend activity window and bounded user samples", () => {
    const display = buildDataPanelTrafficBusinessActivityDisplay(
      {
        version: "v1",
        summary_id: "activity-1",
        source: "runtime.traffic_business_activity_window_v1",
        metric_model: "business-window",
        packet_level_simulation: false,
        frontend_inference_required: false,
        current_sim_time: 12.5,
        request_count: 4,
        user_count: 2,
        active_user_count: 1,
        recent_user_count: 0,
        pending_user_count: 1,
        idle_user_count: 0,
        window_user_count: 2,
        window_active_user_count: 1,
        window_recent_user_count: 0,
        window_pending_user_count: 1,
        window_idle_user_count: 0,
        window: {
          lookback_window_s: 5,
          lookahead_window_s: 10,
          window_start_s: 7.5,
          window_end_s: 22.5,
          assumed_service_duration_s: 2
        },
        item_limit: 2,
        item_count: 2,
        hidden_window_user_count: 0,
        state_counts: { ACTIVE_BUSINESS: 1, PENDING_BUSINESS: 1 },
        window_state_counts: { ACTIVE_BUSINESS: 1, PENDING_BUSINESS: 1 },
        items: [
          {
            user_id: "user-001",
            platform_type: "GROUND_USER",
            business_state: "ACTIVE_BUSINESS",
            request_count: 2,
            active_request_count: 1,
            recent_request_count: 0,
            pending_request_count: 1,
            past_request_count: 0,
            window_request_count: 2,
            communication_request_count: 1,
            compute_request_count: 1,
            service_classes: ["COMPUTE_SERVICE"],
            active_business_types: ["COMPUTE_SERVICE"],
            window_business_types: ["COMPUTE_SERVICE"],
            current_or_next_business_type: "COMPUTE_SERVICE",
            primary_request_id: "req-001",
            primary_flow_id: "flow-001",
            primary_target_id: "sat-001",
            selected_satellite_id: "sat-001",
            current_or_next_arrival_time: 12,
            last_arrival_time: 12,
            next_arrival_time: 18,
            time_to_next_request_s: 5.5,
            active_flow_ids: ["flow-001"],
            recent_flow_ids: [],
            pending_flow_ids: ["flow-002"],
            total_input_data_mb: 64,
            total_output_data_mb: 8,
            network_queue_model: "flow-level-queue",
            compute_execution_model: "resource-vector-estimator"
          },
          {
            user_id: "user-002",
            platform_type: "GROUND_USER",
            business_state: "PENDING_BUSINESS",
            request_count: 2,
            active_request_count: 0,
            recent_request_count: 0,
            pending_request_count: 2,
            past_request_count: 0,
            window_request_count: 2,
            communication_request_count: 2,
            compute_request_count: 0,
            service_classes: ["DATA_TRANSFER"],
            active_business_types: [],
            window_business_types: ["DATA_TRANSFER"],
            current_or_next_business_type: "DATA_TRANSFER",
            primary_request_id: "req-002",
            primary_flow_id: "flow-003",
            primary_target_id: "sat-002",
            selected_satellite_id: "sat-002",
            current_or_next_arrival_time: 14,
            last_arrival_time: null,
            next_arrival_time: 14,
            time_to_next_request_s: 1.5,
            active_flow_ids: [],
            recent_flow_ids: [],
            pending_flow_ids: ["flow-003", "flow-004"],
            total_input_data_mb: 16,
            total_output_data_mb: 0,
            network_queue_model: "flow-level-queue",
            compute_execution_model: "none"
          }
        ],
        model_assumptions: ["flow-level business window"],
        summary_hash: "123456abcdef"
      },
      1
    );

    expect(display).not.toBeNull();
    expect(display?.sourceLabel).toBe("runtime.traffic_business_activity_window_v1");
    expect(display?.summaryLabel).toContain("t=12.5s");
    expect(display?.activeUserLabel).toBe("1 total / 1 window");
    expect(display?.pendingUserLabel).toBe("1 total / 1 window");
    expect(display?.metaLabels).toContain("lookback 5s");
    expect(display?.metaLabels).toContain("lookahead 10s");
    expect(display?.rows).toHaveLength(1);
    expect(display?.rows[0]).toMatchObject({
      userId: "user-001",
      stateLabel: "活跃"
    });
    expect(display?.rows[0]?.detailLabel).toContain("通信-计算服务");
    expect(display?.rows[0]?.detailLabel).toContain("target sat-001");
    expect(display?.rows[0]?.title).toContain("resource-vector-estimator");
  });
});
