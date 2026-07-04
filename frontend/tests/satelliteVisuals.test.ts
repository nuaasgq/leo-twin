import { describe, expect, it } from "vitest";

import {
  NASA_SATELLITE_KIT_MODEL_PARTS,
  buildSatelliteModelParts,
  satelliteModelEntityIds
} from "../src/3d/orbit_renderer/satelliteModelEntities";
import {
  SATELLITE_DEPTH_TEST_DISABLE_DISTANCE,
  SATELLITE_ICON_DATA_URI
} from "../src/3d/orbit_renderer/satelliteEntities";
import {
  buildBeamCellFootprints,
  buildCoverageFootprint,
  coverageBeamDisplaySummary,
  coverageUserIntersectionSummary,
  resolveBeamGeometryOptions,
  selectedCoverageBeamSatellites
} from "../src/3d/beam_renderer/beamEntities";
import {
  appendSatelliteInsetTrail,
  satelliteComputeSummary,
  satelliteAltitudeKm,
  satelliteInsetPoint,
  selectedDisplaySatellite
} from "../src/3d/cesium/satelliteFollow";
import {
  ComputeResourceSummary,
  GroundUserState,
  SatelliteState,
  ScenarioConfig
} from "../src/core/event_types";

describe("satellite model entities", () => {
  it("builds a deterministic fallback multi-part satellite display model", () => {
    const parts = buildSatelliteModelParts(satelliteA);

    expect(parts.map((part) => part.kind)).toEqual([
      "bus",
      "panel-left",
      "panel-right",
      "antenna",
      "sensor"
    ]);
    expect(parts[0].position).toEqual([7_000_000, 0, 0]);
    expect(parts[1].position).toEqual([7_000_000, 0, -126_000]);
    expect(parts[2].position).toEqual([7_000_000, 0, 126_000]);
    expect(parts[3].position).toEqual([7_082_000, 0, 0]);
    expect(parts[4].position).toEqual([6_934_000, 0, 0]);
  });

  it("uses bundled NASA Satellite Kit GLB assets for the primary satellite model", () => {
    expect(NASA_SATELLITE_KIT_MODEL_PARTS.map((asset) => asset.idSuffix)).toEqual([
      "body",
      "wings",
      "radio"
    ]);
    expect(satelliteModelEntityIds(satelliteA)).toEqual([
      "satellite-model:nasa-kit:sat-a:body",
      "satellite-model:nasa-kit:sat-a:wings",
      "satellite-model:nasa-kit:sat-a:radio"
    ]);
    for (const asset of NASA_SATELLITE_KIT_MODEL_PARTS) {
      expect(asset.uri).toMatch(/^\/assets\/nasa-satellite-kit\/.+\.glb$/);
    }
  });
});

describe("satellite overview icon", () => {
  it("keeps satellite overlays depth-tested so the opaque globe occludes far-side satellites", () => {
    expect(SATELLITE_DEPTH_TEST_DISABLE_DISTANCE).toBe(0);
  });

  it("uses a recognizable satellite glyph instead of only a point marker", () => {
    const decodedIcon = decodeURIComponent(
      SATELLITE_ICON_DATA_URI.replace("data:image/svg+xml;charset=UTF-8,", "")
    );

    expect(decodedIcon).toContain("linearGradient");
    expect(decodedIcon).toContain("panel");
    expect(decodedIcon).toContain("antenna");
    expect(decodedIcon.match(/<rect/g)?.length ?? 0).toBeGreaterThanOrEqual(4);
  });
});

describe("selected satellite coverage beams", () => {
  it("renders coverage only for the selected satellite within the bounded limit", () => {
    expect(selectedCoverageBeamSatellites([satelliteA, satelliteB], "sat-b", 1)).toEqual([
      satelliteB
    ]);
    expect(selectedCoverageBeamSatellites([satelliteA, satelliteB], "sat-b", 0)).toEqual([]);
    expect(selectedCoverageBeamSatellites([satelliteA, satelliteB], "", 1)).toEqual([]);
    expect(selectedCoverageBeamSatellites([satelliteA, satelliteB], "missing", 1)).toEqual([]);
  });

  it("builds bounded deterministic honeycomb beam footprints for the selected satellite", () => {
    const cells = buildBeamCellFootprints(satelliteA, 160_000);

    expect(cells.map((cell) => cell.id)).toEqual([
      "beam-cell:sat-a:0",
      "beam-cell:sat-a:1",
      "beam-cell:sat-a:2",
      "beam-cell:sat-a:3",
      "beam-cell:sat-a:4",
      "beam-cell:sat-a:5",
      "beam-cell:sat-a:6"
    ]);
    expect(cells.map((cell) => cell.ring)).toEqual([0, 1, 1, 1, 1, 1, 1]);
    expect(cells[0].position).toEqual([6_377_000, 0, 0]);
    expect(cells[1].position).toEqual([6_377_000, 83_200, 0]);
    expect(cells[1].radiusMeters).toBeCloseTo(54_400, 6);
    expect(buildBeamCellFootprints(satelliteA, 160_000, 32)).toHaveLength(7);
    expect(buildBeamCellFootprints(satelliteA, 160_000, 0)).toHaveLength(1);
    expect(buildBeamCellFootprints(satelliteA, 160_000, 4)).toHaveLength(4);
  });

  it("builds a deterministic selected-satellite coverage footprint boundary", () => {
    expect(buildCoverageFootprint(satelliteA, 160_000)).toEqual({
      id: "beam-footprint:sat-a",
      position: [6_375_500, 0, 0],
      radiusMeters: 160_000
    });
    expect(buildCoverageFootprint(satelliteA, 0).radiusMeters).toBe(1);
  });

  it("resolves beam geometry from backend coverage summary before render defaults", () => {
    const options = resolveBeamGeometryOptions({
      render: {
        beam_length_m: 300_000,
        beam_radius_m: 90_000
      },
      backend_summary: {
        coverage_beam_summary: coverageSummary({
          default_beam_count: 4,
          beam_length_m: 700_000,
          beam_radius_m: 220_000
        })
      }
    });

    expect(options).toEqual({
      beamLengthMeters: 700_000,
      beamRadiusMeters: 220_000,
      beamCellCount: 4
    });
  });

  it("summarizes selected satellite coverage model for the follow inset", () => {
    expect(
      coverageBeamDisplaySummary({
        backend_summary: {
          coverage_beam_summary: coverageSummary({
            default_beam_count: 4,
            beam_length_m: 700_000,
            beam_radius_m: 220_000,
            model_note: "backend note"
          })
        }
      })
    ).toEqual({
      footprintRadiusLabel: "覆盖半径 220 km",
      beamLengthLabel: "波束长度 700 km",
      beamCountLabel: "蜂窝波束 4 个",
      modelLabel: "DETERMINISTIC_GEOMETRIC_FOOTPRINT",
      note: "backend note"
    });
    expect(coverageBeamDisplaySummary(null)).toMatchObject({
      footprintRadiusLabel: "覆盖半径 160 km",
      beamLengthLabel: "波束长度 600 km",
      beamCountLabel: "蜂窝波束 7 个"
    });
    expect(coverageBeamDisplaySummary(null).note).toContain("未进行 RF");
  });

  it("counts positioned ground users inside the selected visual footprint", () => {
    const users: GroundUserState[] = [
      { user_id: "user-center", position: [0, 0, 0] },
      { user_id: "user-near", position: [0.5, 0, 0] },
      { user_id: "user-far", position: [3, 0, 0] },
      { user_id: "user-unpositioned" }
    ];

    expect(coverageUserIntersectionSummary(satelliteA, users, null)).toEqual({
      totalUserCount: 4,
      positionedUserCount: 3,
      coveredUserCount: 2,
      coveredUserIds: ["user-center", "user-near"],
      label: "覆盖内用户 2/3",
      coveredUserLabel: "覆盖用户 user-center、user-near",
      note:
        "基于 4 个地面用户中的 3 个定位用户做几何足迹包含统计；不是 RF 覆盖或接入判定。"
    });
  });

  it("keeps backend beam counts bounded for large-scale rendering safety", () => {
    expect(
      resolveBeamGeometryOptions({
        backend_summary: {
          coverage_beam_summary: coverageSummary({
            default_beam_count: 99,
            beam_length_m: 0,
            beam_radius_m: -1
          })
        }
      })
    ).toEqual({
      beamLengthMeters: 600_000,
      beamRadiusMeters: 160_000,
      beamCellCount: 7
    });
  });
});

describe("satellite follow inset", () => {
  it("selects a stable target satellite and projects it into the inset", () => {
    expect(selectedDisplaySatellite([satelliteA, satelliteB], "sat-b")).toBe(satelliteB);
    expect(selectedDisplaySatellite([satelliteA, satelliteB], "missing")).toBe(
      satelliteA
    );
    expect(selectedDisplaySatellite([], "sat-a")).toBeNull();

    const insetPoint = satelliteInsetPoint(satelliteA);

    expect(insetPoint.satelliteId).toBe("sat-a");
    expect(insetPoint.simTime).toBe(1);
    expect(insetPoint.x).toBeCloseTo(84, 3);
    expect(insetPoint.y).toBeCloseTo(50.026, 3);
    expect(satelliteAltitudeKm(satelliteA)).toBeCloseTo(629, 6);
  });

  it("appends incremental motion and resets when the followed satellite changes", () => {
    const firstTrail = appendSatelliteInsetTrail([], satelliteA);
    const duplicateTrail = appendSatelliteInsetTrail(firstTrail, satelliteA);
    const secondTrail = appendSatelliteInsetTrail(firstTrail, {
      ...satelliteA,
      sim_time: 2,
      position: [0, 7_000_000, 0]
    });
    const switchedTrail = appendSatelliteInsetTrail(secondTrail, satelliteB);

    expect(duplicateTrail).toBe(firstTrail);
    expect(secondTrail).toHaveLength(2);
    expect(secondTrail[1].x).toBeCloseTo(49.927, 3);
    expect(secondTrail[1].y).toBeCloseTo(74, 2);
    expect(switchedTrail).toHaveLength(1);
    expect(switchedTrail[0].satelliteId).toBe("sat-b");
  });

  it("summarizes selected satellite compute-node resources", () => {
    expect(
      satelliteComputeSummary({
        capacity: 20,
        available_capacity: 5,
        load_ratio: 0.75,
        status: "BUSY"
      })
    ).toMatchObject({
      resourceModelLabel: "LegacyScalarCapacity",
      resourceRoleLabel: "卫星算力节点",
      capacityLabel: "20 GFLOPS FP32",
      availableLabel: "5 GFLOPS",
      utilizationLabel: "75%",
      utilizationPercent: 75,
      availablePercent: 25,
      statusLabel: "BUSY",
      cpuVectorLabel: "CPU FP32 20 GFLOPS / FP64 0 GFLOPS",
      gpuVectorLabel: "GPU FP32 0 TFLOPS / FP16 0 TFLOPS",
      npuVectorLabel: "NPU INT8 0 TOPS",
      memoryStorageLabel: "内存 0 GB / 存储 0 GB",
      processingUsageLabel:
        "使用 CPU FP32 0 GFLOPS / FP64 0 GFLOPS / GPU FP32 0 TFLOPS / FP16 0 TFLOPS / NPU 0 TOPS",
      memoryUsageLabel: "使用 内存 0 GB / 存储 0 GB",
      compatibilityNote: "实时节点状态仍使用标量 capacity。"
    });
    expect(satelliteComputeSummary(null)).toBeNull();
  });

  it("uses backend compute resource vectors for selected satellite details", () => {
    expect(
      satelliteComputeSummary(
        {
          capacity: 40,
          available_capacity: 10,
          status: "BUSY"
        },
        computeResourceSummary({
          cpu_gflops_fp32_per_node: 40,
          cpu_gflops_fp64_per_node: 8,
          gpu_tflops_fp32_per_node: 2.5,
          gpu_tflops_fp16_per_node: 5,
          npu_tops_int8_per_node: 12,
          memory_gb_per_node: 32,
          storage_gb_per_node: 512
        })
      )
    ).toMatchObject({
      resourceModelLabel: "ComputeResourceVector",
      resourceRoleLabel: "卫星载荷算力节点",
      capacityLabel: "40 GFLOPS FP32",
      availableLabel: "10 GFLOPS",
      utilizationLabel: "75%",
      utilizationPercent: 75,
      availablePercent: 25,
      statusLabel: "BUSY",
      cpuVectorLabel: "CPU FP32 40 GFLOPS / FP64 8 GFLOPS",
      gpuVectorLabel: "GPU FP32 2.5 TFLOPS / FP16 5 TFLOPS",
      npuVectorLabel: "NPU INT8 12 TOPS",
      memoryStorageLabel: "内存 32 GB / 存储 512 GB",
      processingUsageLabel:
        "使用 CPU FP32 0 GFLOPS / FP64 0 GFLOPS / GPU FP32 0 TFLOPS / FP16 0 TFLOPS / NPU 0 TOPS",
      memoryUsageLabel: "使用 内存 0 GB / 存储 0 GB",
      compatibilityNote: "Legacy scalar capacity maps to cpu_gflops_fp32."
    });
  });

  it("prefers live compute-node resource vectors for selected satellite details", () => {
    const summary = satelliteComputeSummary({
      capacity: 44,
      available_capacity: 11,
      status: "BUSY",
      cpu_gflops_fp64: 9,
      gpu_tflops_fp32: 3.5,
      gpu_tflops_fp16: 7,
      npu_tops_int8: 16,
      memory_gb: 48,
      storage_gb: 1024,
      used_cpu_gflops_fp32: 12,
      used_gpu_tflops_fp32: 2.5,
      used_npu_tops_int8: 4,
      used_memory_gb: 8,
      used_storage_gb: 16
    });

    expect(summary).toMatchObject({
      resourceModelLabel: "ComputeResourceVector",
      capacityLabel: "44 GFLOPS FP32",
      availableLabel: "11 GFLOPS",
      utilizationLabel: "75%",
      utilizationPercent: 75,
      availablePercent: 25,
      cpuVectorLabel: "CPU FP32 44 GFLOPS / FP64 9 GFLOPS",
      gpuVectorLabel: "GPU FP32 3.5 TFLOPS / FP16 7 TFLOPS",
      npuVectorLabel: "NPU INT8 16 TOPS",
      memoryStorageLabel: "内存 48 GB / 存储 1,024 GB",
      processingUsageLabel:
        "使用 CPU FP32 12 GFLOPS / FP64 0 GFLOPS / GPU FP32 2.5 TFLOPS / FP16 0 TFLOPS / NPU 4 TOPS",
      memoryUsageLabel: "使用 内存 8 GB / 存储 16 GB"
    });

    expect(
      summary?.resourceBreakdown.map(({ label, capacityLabel, usedLabel }) => ({
        label,
        capacityLabel,
        usedLabel
      }))
    ).toEqual([
      { label: "CPU FP32", capacityLabel: "44 GFLOPS", usedLabel: "12 GFLOPS" },
      { label: "CPU FP64", capacityLabel: "9 GFLOPS", usedLabel: "0 GFLOPS" },
      { label: "GPU FP32", capacityLabel: "3.5 TFLOPS", usedLabel: "2.5 TFLOPS" },
      { label: "GPU FP16", capacityLabel: "7 TFLOPS", usedLabel: "0 TFLOPS" },
      { label: "NPU INT8", capacityLabel: "16 TOPS", usedLabel: "4 TOPS" },
      { label: "内存", capacityLabel: "48 GB", usedLabel: "8 GB" },
      { label: "存储", capacityLabel: "1,024 GB", usedLabel: "16 GB" }
    ]);
    expect(summary?.resourceBreakdown[0].utilizationPercent).toBeCloseTo(27.27, 2);
    expect(summary?.resourceBreakdown[2].utilizationPercent).toBeCloseTo(71.43, 2);
  });
});

const satelliteA: SatelliteState = {
  satellite_id: "sat-a",
  sim_time: 1,
  position: [7_000_000, 0, 0],
  velocity: [0, 7_500, 0],
  status: "ACTIVE"
};

const satelliteB: SatelliteState = {
  satellite_id: "sat-b",
  sim_time: 1,
  position: [0, 0, 7_000_000],
  velocity: [7_500, 0, 0],
  status: "ACTIVE"
};

function coverageSummary(
  overrides: Partial<
    NonNullable<NonNullable<ScenarioConfig["backend_summary"]>["coverage_beam_summary"]>
  >
): NonNullable<NonNullable<ScenarioConfig["backend_summary"]>["coverage_beam_summary"]> {
  return {
    coverage_model: "DETERMINISTIC_GEOMETRIC_FOOTPRINT",
    selected_satellite_detail_mode: "SELECTED_SATELLITE_ONLY",
    beam_pattern: "CENTER_PLUS_HEX_RING_VISUAL_APPROXIMATION",
    default_beam_count: 7,
    beam_radius_m: 160_000,
    beam_length_m: 600_000,
    global_beam_render_limit: 1,
    model_note:
      "Selected-satellite beam cells are deterministic visual footprints; no RF propagation or antenna-pattern simulation is performed.",
    ...overrides
  };
}

function computeResourceSummary(
  overrides: Partial<ComputeResourceSummary>
): ComputeResourceSummary {
  return {
    resource_model: "ComputeResourceVector",
    node_role: "SATELLITE_HOSTED_COMPUTE",
    compute_node_count: 1,
    legacy_capacity_per_node: 40,
    cpu_gflops_fp32_per_node: 40,
    cpu_gflops_fp64_per_node: 0,
    gpu_tflops_fp32_per_node: 0,
    gpu_tflops_fp16_per_node: 0,
    npu_tops_int8_per_node: 0,
    memory_gb_per_node: 0,
    storage_gb_per_node: 0,
    total_cpu_gflops_fp32: 40,
    total_cpu_gflops_fp64: 0,
    total_gpu_tflops_fp32: 0,
    total_gpu_tflops_fp16: 0,
    total_npu_tops_int8: 0,
    total_memory_gb: 0,
    total_storage_gb: 0,
    capacity_unit: "GFLOPS FP32",
    compatibility_note: "Legacy scalar capacity maps to cpu_gflops_fp32.",
    ...overrides
  };
}
