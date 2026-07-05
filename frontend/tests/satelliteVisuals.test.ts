import { ArcType, EntityCollection, JulianDate } from "cesium";
import { describe, expect, it } from "vitest";

import {
  NASA_SATELLITE_KIT_MODEL_PARTS,
  buildSatelliteModelParts,
  satelliteModelEntityIds
} from "../src/3d/orbit_renderer/satelliteModelEntities";
import {
  SATELLITE_DEPTH_TEST_DISABLE_DISTANCE,
  SATELLITE_ICON_DATA_URI,
  upsertSatelliteOrbitEntity
} from "../src/3d/orbit_renderer/satelliteEntities";
import {
  upsertLinkEntity,
  upsertRouteEntity
} from "../src/3d/link_renderer/linkEntities";
import {
  buildBeamCellFootprints,
  buildCoverageFootprint,
  coverageBeamDisplaySummary,
  coverageUserIntersectionSummary,
  resolveBeamGeometryOptions,
  selectedCoverageBeamSatellites,
  selectedCoverageVisualPolicyV2LayerSummary,
  selectedCoverageVisualPolicyV2Summary
} from "../src/3d/beam_renderer/beamEntities";
import {
  appendSatelliteInsetTrail,
  satelliteComputeSummary,
  satelliteAltitudeKm,
  satelliteInsetPoint,
  selectableSatelliteTargets,
  selectedDisplaySatellite
} from "../src/3d/cesium/satelliteFollow";
import {
  selectedSatelliteDetailSummary,
  appendSelectedSatelliteResourceHistory,
  selectedSatelliteResourceHistoryFromBackend,
  selectedSatelliteResourceHistoryPoints,
  selectedSatelliteResourceUsageRows
} from "../src/3d/cesium/satelliteDetailSummary";
import {
  ComputeResourceSummary,
  GroundUserState,
  LinkState,
  Route,
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
      expect(asset.sourceFile).toMatch(/^Satellite Kit .+\.glb$/);
      expect(asset.sha256).toMatch(/^[a-f0-9]{64}$/);
    }
    expect(new Set(NASA_SATELLITE_KIT_MODEL_PARTS.map((asset) => asset.sha256)).size).toBe(
      NASA_SATELLITE_KIT_MODEL_PARTS.length
    );
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

describe("space polyline render safety", () => {
  it("renders near-antipodal space links as direct 3D segments", () => {
    const entities = new EntityCollection();
    const cache = new Map();
    const nodes = {
      satellites: new Map([
        ["sat-a", satelliteA],
        [
          "sat-antipodal",
          {
            ...satelliteB,
            satellite_id: "sat-antipodal",
            position: [-6_999_900, 28_258, 0]
          }
        ]
      ]),
      groundUsers: new Map()
    };

    upsertLinkEntity(
      entities,
      cache,
      {
        source_id: "sat-a",
        target_id: "sat-antipodal",
        latency: 0.08,
        capacity: 40,
        availability: true
      },
      nodes
    );

    const entity = entities.getById("link:sat-a->sat-antipodal");
    expect(entity?.polyline?.arcType?.getValue(new JulianDate())).toBe(ArcType.NONE);
  });

  it("renders near-antipodal routes as direct 3D segments", () => {
    const entities = new EntityCollection();
    const cache = new Map();
    const nodes = {
      satellites: new Map([
        ["sat-a", satelliteA],
        [
          "sat-antipodal",
          {
            ...satelliteB,
            satellite_id: "sat-antipodal",
            position: [-6_999_900, 28_258, 0]
          }
        ]
      ]),
      groundUsers: new Map()
    };

    upsertRouteEntity(
      entities,
      cache,
      {
        route_id: "route-antipodal",
        flow_id: "flow-antipodal",
        path: ["sat-a", "sat-antipodal"],
        latency: 0.12,
        capacity: 20,
        available: true
      },
      nodes
    );

    const entity = entities.getById("route:route-antipodal");
    expect(entity?.polyline?.arcType?.getValue(new JulianDate())).toBe(ArcType.NONE);
  });

  it("renders orbit tracks as direct 3D space polylines", () => {
    const entities = new EntityCollection();
    const cache = new Map();

    upsertSatelliteOrbitEntity(entities, cache, satelliteA);

    const entity = entities.getById("satellite-orbit:sat-a");
    expect(entity?.polyline?.arcType?.getValue(new JulianDate())).toBe(ArcType.NONE);
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
      beamPatternLabel: "波束模式 中心 + 六邻区蜂窝",
      fidelityLabel: "覆盖保真 显示近似",
      intersectionPolicyLabel: "判定策略 仅视觉几何包含",
      modelLabel: "DETERMINISTIC_GEOMETRIC_FOOTPRINT",
      note: "backend note"
    });
    expect(coverageBeamDisplaySummary(null)).toMatchObject({
      footprintRadiusLabel: "覆盖半径 160 km",
      beamLengthLabel: "波束长度 600 km",
      beamCountLabel: "蜂窝波束 7 个",
      beamPatternLabel: "波束模式 中心 + 六邻区蜂窝",
      fidelityLabel: "覆盖保真 显示近似",
      intersectionPolicyLabel: "判定策略 仅视觉几何包含"
    });
    expect(coverageBeamDisplaySummary(null).note).toContain("未进行 RF");
  });

  it("exposes selected-satellite coverage visual policy v2 from backend summary", () => {
    const config = {
      backend_summary: {
        coverage_beam_summary: coverageSummary({
          default_beam_count: 4,
          beam_length_m: 700_000,
          beam_radius_m: 220_000,
          global_beam_render_limit: 1
        })
      }
    };

    expect(selectedCoverageVisualPolicyV2Summary(config)).toEqual({
      version: "v2",
      policy_id: "leo_twin.selected_coverage_visual_policy.v2",
      selected_satellite_detail_mode: "SELECTED_SATELLITE_ONLY",
      coverage_model: "DETERMINISTIC_GEOMETRIC_FOOTPRINT",
      fidelity_level: "DISPLAY_APPROXIMATION",
      beam_pattern: "CENTER_PLUS_HEX_RING_VISUAL_APPROXIMATION",
      footprint_intersection_policy: "VISUAL_GEOMETRIC_CONTAINMENT_ONLY",
      beam_cell_count: 4,
      beam_radius_m: 220_000,
      beam_length_m: 700_000,
      global_beam_render_limit: 1,
      local_layer_enabled: true,
      excluded_physics: [
        "RF_PROPAGATION",
        "ANTENNA_PATTERN",
        "LINK_BUDGET",
        "INTERFERENCE"
      ],
      visual_only: true,
      no_access_semantics: true
    });
    expect(selectedCoverageVisualPolicyV2LayerSummary(config)).toEqual({
      label: "覆盖",
      value: "选中卫星 / v2",
      detail: "蜂窝 4 / 半径 220 km / RF排除 / 接入无语义"
    });
  });

  it("keeps coverage visual policy deterministic when the local layer is hidden", () => {
    expect(selectedCoverageVisualPolicyV2Summary(null, false)).toMatchObject({
      beam_cell_count: 7,
      beam_radius_m: 160_000,
      beam_length_m: 600_000,
      global_beam_render_limit: 1,
      local_layer_enabled: false,
      visual_only: true,
      no_access_semantics: true
    });
    expect(selectedCoverageVisualPolicyV2LayerSummary(null, false)).toEqual({
      label: "覆盖",
      value: "隐藏 / v2",
      detail: "蜂窝 7 / 半径 160 km / RF排除 / 接入无语义"
    });
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

  it("keeps every snapshot satellite selectable for follow mode", () => {
    const satellites = Array.from({ length: 120 }, (_, index) => ({
      ...satelliteA,
      satellite_id: `sat-${index}`,
    }));

    const selectable = selectableSatelliteTargets(satellites);

    expect(selectable).toHaveLength(120);
    expect(selectable[119].satellite_id).toBe("sat-119");
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

describe("selected satellite detail summary", () => {
  it("aggregates deterministic orbit, network, coverage, and compute facts", () => {
    const summary = selectedSatelliteDetailSummary({
      satellite: satelliteA,
      computeNode: {
        node_id: "sat-a",
        running_tasks: 2,
        finished_tasks: 3,
        capacity: 40,
        available_capacity: 10,
        status: "BUSY",
        load_ratio: 0.75
      },
      computeResourceSummary: computeResourceSummary({
        cpu_gflops_fp32_per_node: 40,
        gpu_tflops_fp32_per_node: 2
      }),
      links: detailLinks,
      routes: detailRoutes,
      groundUsers: [
        { user_id: "user-center", position: [0, 0, 0] },
        { user_id: "user-far", position: [4, 0, 0] }
      ],
      scenarioConfig: null
    });

    expect(summary).toMatchObject({
      satelliteId: "sat-a",
      statusLabel: "状态 ACTIVE",
      simTimeLabel: "t=1s",
      altitudeLabel: "高度 629 km",
      speedLabel: "速度 7.5 km/s",
      activeLinksLabel: "链路 2 条（接入 1 / 星间 1）",
      routeLabel: "相关路由 2 条 / 可用 2 条",
      routeLatencyLabel: "平均路由时延 50 ms",
      routeCapacityLabel: "可用路由容量 50 Mbps",
      routeLossLabel: "路由丢包代理 7%",
      routeJitterLabel: "路由抖动代理 60 ms",
      linkUtilizationLabel: "平均链路利用率 50%",
      computeLoadLabel: "算力负载 75%",
      computeCapacityLabel: "容量 40 GFLOPS FP32",
      runningTaskLabel: "任务 运行 2 / 完成 3",
      resourceModelLabel: "ComputeResourceVector",
      routeIds: ["route-a", "route-b"]
    });
    expect(summary.coverageLabel).toContain("user-center");
    expect(summary.note).toContain("流级聚合态势");
  });

  it("builds selected satellite resource usage rows for the control strip", () => {
    const summary = selectedSatelliteDetailSummary({
      satellite: satelliteA,
      computeNode: {
        node_id: "sat-a",
        running_tasks: 2,
        finished_tasks: 3,
        capacity: 44,
        available_capacity: 11,
        status: "BUSY",
        load_ratio: 0.75,
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
      },
      links: [],
      routes: [],
      groundUsers: [],
      scenarioConfig: null
    });

    expect(selectedSatelliteResourceUsageRows(summary, 3)).toEqual([
      {
        label: "CPU FP32",
        usedLabel: "12 GFLOPS",
        capacityLabel: "44 GFLOPS",
        utilizationPercent: 27.27272727272727,
        utilizationLabel: "27.3%"
      },
      {
        label: "CPU FP64",
        usedLabel: "0 GFLOPS",
        capacityLabel: "9 GFLOPS",
        utilizationPercent: 0,
        utilizationLabel: "0%"
      },
      {
        label: "GPU FP32",
        usedLabel: "2.5 TFLOPS",
        capacityLabel: "3.5 TFLOPS",
        utilizationPercent: 71.42857142857143,
        utilizationLabel: "71.4%"
      }
    ]);
  });

  it("appends bounded selected satellite resource history and sparkline points", () => {
    const first = selectedSatelliteDetailSummary({
      satellite: satelliteA,
      computeNode: {
        node_id: "sat-a",
        running_tasks: 1,
        finished_tasks: 0,
        capacity: 40,
        available_capacity: 30,
        status: "BUSY",
        load_ratio: 0.25
      },
      links: [],
      routes: [],
      groundUsers: [],
      scenarioConfig: null
    });
    const second = selectedSatelliteDetailSummary({
      satellite: { ...satelliteA, sim_time: 2 },
      computeNode: {
        node_id: "sat-a",
        running_tasks: 2,
        finished_tasks: 0,
        capacity: 40,
        available_capacity: 20,
        status: "BUSY",
        load_ratio: 0.5
      },
      links: [],
      routes: [],
      groundUsers: [],
      scenarioConfig: null
    });
    const switched = selectedSatelliteDetailSummary({
      satellite: satelliteB,
      computeNode: {
        node_id: "sat-b",
        running_tasks: 0,
        finished_tasks: 0,
        capacity: 40,
        available_capacity: 40,
        status: "IDLE",
        load_ratio: 0
      },
      links: [],
      routes: [],
      groundUsers: [],
      scenarioConfig: null
    });

    const firstHistory = appendSelectedSatelliteResourceHistory([], first, 1);
    const duplicateHistory = appendSelectedSatelliteResourceHistory(firstHistory, first, 1);
    const secondHistory = appendSelectedSatelliteResourceHistory(
      duplicateHistory,
      second,
      2
    );
    const switchedHistory = appendSelectedSatelliteResourceHistory(
      secondHistory,
      switched,
      1
    );

    expect(duplicateHistory).toBe(firstHistory);
    expect(secondHistory.map((point) => point.utilizationPercent)).toEqual([25, 50]);
    expect(selectedSatelliteResourceHistoryPoints(secondHistory, 100, 36)).toBe(
      "0,27 100,18"
    );
    expect(switchedHistory).toEqual([
      {
        satelliteId: "sat-b",
        simTime: 1,
        utilizationPercent: 0
      }
    ]);
  });

  it("builds selected satellite resource history from backend KPI samples", () => {
    const history = selectedSatelliteResourceHistoryFromBackend(
      {
        version: "v1",
        mode: "RECENT_COMPUTE_LIMITED",
        slice_limit: 64,
        sample_limit: 32,
        satellite_count: 2,
        series_count: 1,
        series: [
          {
            satellite_id: "sat-a",
            sample_count: 2,
            samples: [
              {
                sim_time: 1,
                compute_load_ratio: 0.25,
                compute_used_gflops_fp32: 25
              },
              {
                sim_time: 2,
                compute_load_ratio: 1.25,
                compute_used_gflops_fp32: 125
              }
            ]
          }
        ]
      },
      "sat-a"
    );

    expect(history).toEqual([
      {
        satelliteId: "sat-a",
        simTime: 1,
        utilizationPercent: 25
      },
      {
        satelliteId: "sat-a",
        simTime: 2,
        utilizationPercent: 100
      }
    ]);
    expect(
      selectedSatelliteResourceHistoryFromBackend(
        {
          version: "v1",
          mode: "RECENT_COMPUTE_LIMITED",
          series: []
        },
        "sat-missing"
      )
    ).toEqual([]);
  });

  it("reports empty network and compute data without inventing values", () => {
    const summary = selectedSatelliteDetailSummary({
      satellite: satelliteB,
      links: [],
      routes: [],
      groundUsers: [],
      scenarioConfig: null
    });

    expect(summary).toMatchObject({
      satelliteId: "sat-b",
      activeLinksLabel: "链路 0 条（接入 0 / 星间 0）",
      routeLabel: "相关路由 0 条 / 可用 0 条",
      routeLatencyLabel: "平均路由时延 --",
      routeCapacityLabel: "可用路由容量 0 Mbps",
      routeLossLabel: "路由丢包代理 --",
      routeJitterLabel: "路由抖动代理 --",
      linkUtilizationLabel: "平均链路利用率 --",
      computeLoadLabel: "算力节点未同步",
      computeCapacityLabel: "容量 --",
      runningTaskLabel: "任务 --",
      resourceModelLabel: "资源模型未同步",
      routeIds: []
    });
  });

  it("prefers backend runtime satellite KPI slices for selected satellite facts", () => {
    const summary = selectedSatelliteDetailSummary({
      satellite: satelliteA,
      links: [],
      routes: [],
      groundUsers: [],
      scenarioConfig: null,
      satelliteKpiSlices: {
        version: "v1",
        mode: "TOP_ACTIVITY_LIMITED",
        slice_limit: 64,
        satellite_count: 1,
        slice_count: 1,
        slices: [
          {
            satellite_id: "sat-a",
            active_link_count: 4,
            active_access_link_count: 2,
            active_space_link_count: 2,
            route_count: 3,
            available_route_count: 2,
            route_capacity_mbps: 180,
            route_demand_mbps: 160,
            route_latency_avg_s: 0.045,
            route_delay_variation_proxy_s: 0.006,
            route_loss_proxy_rate: 0.025,
            compute_capacity_gflops_fp32: 100,
            compute_used_gflops_fp32: 65,
            compute_capacity_gflops_fp64: 8,
            compute_used_gflops_fp64: 2,
            compute_capacity_gpu_tflops_fp32: 2.5,
            compute_used_gpu_tflops_fp32: 1.5,
            compute_capacity_gpu_tflops_fp16: 5,
            compute_used_gpu_tflops_fp16: 3,
            compute_capacity_npu_tops_int8: 12,
            compute_used_npu_tops_int8: 6,
            compute_capacity_memory_gb: 32,
            compute_used_memory_gb: 10,
            compute_capacity_storage_gb: 512,
            compute_used_storage_gb: 64,
            compute_load_ratio: 0.65,
            running_task_count: 2,
            finished_task_count: 7
          }
        ]
      }
    });

    expect(summary).toMatchObject({
      activeLinksLabel: "链路 4 条（接入 2 / 星间 2）",
      routeLabel: "相关路由 3 条 / 可用 2 条",
      routeLatencyLabel: "平均路由时延 45 ms",
      routeCapacityLabel: "可用路由容量 180 Mbps",
      routeLossLabel: "路由丢包代理 2.5%",
      routeJitterLabel: "路由抖动代理 6 ms",
      computeLoadLabel: "算力负载 65%",
      computeCapacityLabel: "容量 65 / 100 GFLOPS FP32",
      runningTaskLabel: "任务 运行 2 / 完成 7",
      resourceModelLabel: "RuntimeSatelliteKpiSlicesV1"
    });
    expect(summary.computeSummary).toMatchObject({
      resourceModelLabel: "ComputeResourceVector",
      cpuVectorLabel: "CPU FP32 100 GFLOPS / FP64 8 GFLOPS",
      gpuVectorLabel: "GPU FP32 2.5 TFLOPS / FP16 5 TFLOPS",
      npuVectorLabel: "NPU INT8 12 TOPS"
    });
    expect(
      selectedSatelliteResourceUsageRows(summary, 3).map((row) => [
        row.label,
        row.usedLabel,
        row.capacityLabel
      ])
    ).toEqual([
      ["CPU FP32", "65 GFLOPS", "100 GFLOPS"],
      ["CPU FP64", "2 GFLOPS", "8 GFLOPS"],
      ["GPU FP32", "1.5 TFLOPS", "2.5 TFLOPS"]
    ]);
    expect(summary.note).toContain("runtime satellite KPI");
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

const detailLinks: readonly LinkState[] = [
  {
    source_id: "sat-a",
    target_id: "sat-b",
    latency: 0.012,
    capacity: 80,
    availability: true,
    utilization: 0.25
  },
  {
    source_id: "user-center",
    target_id: "sat-a",
    latency: 0.02,
    capacity: 20,
    availability: true,
    utilization: 0.75
  },
  {
    source_id: "sat-a",
    target_id: "user-far",
    latency: 0.06,
    capacity: 10,
    availability: false,
    utilization: 0.9
  }
];

const detailRoutes: readonly Route[] = [
  {
    route_id: "route-a",
    flow_id: "flow-a",
    path: ["user-center", "sat-a", "sat-b"],
    latency: 0.02,
    capacity: 40,
    available: true,
    loss_rate: 0.04
  },
  {
    route_id: "route-b",
    flow_id: "flow-b",
    path: ["sat-a", "user-far"],
    latency: 0.08,
    capacity: 10,
    available: true,
    loss_rate: 0.1
  }
];

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
