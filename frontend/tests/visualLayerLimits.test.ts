import { describe, expect, it } from "vitest";

import { ScenarioConfig } from "../src/core/event_types";
import {
  DEFAULT_LOCAL_VISUAL_LAYERS,
  applyLocalVisualLayerLimits,
  satelliteIconRenderLimit,
  visualLayerControlSummary,
  visualLayerLimits,
  visualSatelliteModelRenderSatellites
} from "../src/3d/cesium/renderLimits";

describe("visualLayerLimits", () => {
  it("enables bounded network visual layers by default", () => {
    expect(visualLayerLimits(null)).toEqual({
      showSatellites: true,
      satelliteIconRenderLimit: 120,
      satelliteModelRenderLimit: 32,
      orbitTrackRenderLimit: 48,
      beamRenderLimit: 1,
      groundUserRenderLimit: 80,
      linkRenderLimit: 96,
      routeRenderLimit: 8
    });
  });

  it("honors scenario visualization switches", () => {
    const config: ScenarioConfig = {
      ui: {
        visualization: {
          satellites: false,
          users: false,
          links: false,
          metrics: true
        }
      }
    };

    expect(visualLayerLimits(config)).toEqual({
      showSatellites: false,
      satelliteIconRenderLimit: 0,
      satelliteModelRenderLimit: 0,
      orbitTrackRenderLimit: 0,
      beamRenderLimit: 0,
      groundUserRenderLimit: 0,
      linkRenderLimit: 0,
      routeRenderLimit: 0
    });
  });

  it("uses the metrics switch for orbit and route auxiliary layers", () => {
    const config: ScenarioConfig = {
      ui: {
        visualization: {
          satellites: true,
          users: true,
          links: true,
          metrics: false
        }
      }
    };

    expect(visualLayerLimits(config)).toEqual({
      showSatellites: true,
      satelliteIconRenderLimit: 120,
      satelliteModelRenderLimit: 32,
      orbitTrackRenderLimit: 0,
      beamRenderLimit: 0,
      groundUserRenderLimit: 80,
      linkRenderLimit: 96,
      routeRenderLimit: 0
    });
  });

  it("keeps backend layer limits unchanged when local layers are all enabled", () => {
    const limits = visualLayerLimits(null);

    expect(applyLocalVisualLayerLimits(limits, DEFAULT_LOCAL_VISUAL_LAYERS)).toEqual(
      limits
    );
  });

  it("locally suppresses selected visual layers without changing other budgets", () => {
    expect(
      applyLocalVisualLayerLimits(visualLayerLimits(null), {
        ...DEFAULT_LOCAL_VISUAL_LAYERS,
        satellitePoints: false,
        satelliteIcons: false,
        coverageBeams: false,
        links: false
      })
    ).toEqual({
      showSatellites: false,
      satelliteIconRenderLimit: 0,
      satelliteModelRenderLimit: 32,
      orbitTrackRenderLimit: 48,
      beamRenderLimit: 0,
      groundUserRenderLimit: 80,
      linkRenderLimit: 0,
      routeRenderLimit: 8
    });
  });

  it("cannot re-enable layers disabled by scenario configuration", () => {
    const config: ScenarioConfig = {
      ui: {
        visualization: {
          satellites: false,
          users: false,
          links: false,
          metrics: false
        }
      }
    };
    const disabledLimits = visualLayerLimits(config);

    expect(
      applyLocalVisualLayerLimits(disabledLimits, DEFAULT_LOCAL_VISUAL_LAYERS)
    ).toEqual(disabledLimits);
  });

  it("shows every satellite icon for small 120-satellite scenarios", () => {
    const config: ScenarioConfig = {
      scenario: {
        satellite_count: 120
      }
    };

    expect(visualLayerLimits(config).satelliteIconRenderLimit).toBe(120);
    expect(satelliteIconRenderLimit(72)).toBe(72);
    expect(satelliteIconRenderLimit(1200)).toBe(120);
  });
});

describe("visualLayerControlSummary", () => {
  it("explains local layer limits shown by the 3D control toggles", () => {
    expect(visualLayerControlSummary(null)).toEqual([
      {
        label: "资产",
        value: "v1 / 6 项",
        detail: "地球底图 1 / 国界 1 / 模型 3 / 图标 1 / SHA 4"
      },
      {
        label: "地球",
        value: "不透明 / v2",
        detail: "NaturalEarthII / 国界显示 / 背面遮挡开启 / 日夜关闭"
      },
      {
        label: "覆盖",
        value: "选中卫星 / v2",
        detail: "蜂窝 7 / 半径 160 km / RF排除 / 接入无语义"
      },
      { label: "国界", value: "显示", detail: "Natural Earth 国家边界" },
      { label: "点位", value: "显示", detail: "全部卫星点位" },
      { label: "图标", value: "≤120", detail: "卫星图标上限" },
      { label: "模型", value: "≤32", detail: "GLB 模型上限，选中卫星优先" },
      { label: "轨迹", value: "≤48", detail: "轨道轨迹上限" },
      { label: "波束", value: "≤1", detail: "选中卫星覆盖波束" },
      { label: "用户", value: "≤80", detail: "地面用户上限" },
      { label: "链路", value: "≤96", detail: "可视链路上限" },
      { label: "路由", value: "≤8", detail: "路径高亮上限" }
    ]);
  });

  it("reports hidden layer effects after local toggles are disabled", () => {
    const summary = visualLayerControlSummary(null, {
      ...DEFAULT_LOCAL_VISUAL_LAYERS,
      countryOverlays: false,
      satelliteIcons: false,
      coverageBeams: false,
      links: false
    });

    expect(summary.find((item) => item.label === "国界")?.value).toBe("隐藏");
    expect(summary.find((item) => item.label === "地球")?.detail).toBe(
      "NaturalEarthII / 国界隐藏 / 背面遮挡开启 / 日夜关闭"
    );
    expect(summary.find((item) => item.label === "图标")?.value).toBe("隐藏");
    expect(summary.find((item) => item.label === "波束")?.value).toBe("隐藏");
    expect(summary.find((item) => item.label === "覆盖")).toEqual({
      label: "覆盖",
      value: "隐藏 / v2",
      detail: "蜂窝 7 / 半径 160 km / RF排除 / 接入无语义"
    });
    expect(summary.find((item) => item.label === "链路")?.value).toBe("隐藏");
    expect(summary.find((item) => item.label === "模型")?.value).toBe("≤32");
  });

  it("reports translucent observation mode in the layer summary", () => {
    const summary = visualLayerControlSummary(
      null,
      DEFAULT_LOCAL_VISUAL_LAYERS,
      "TRANSLUCENT"
    );

    expect(summary.find((item) => item.label === "地球")).toEqual({
      label: "地球",
      value: "透明观测 / v2",
      detail: "NaturalEarthII / 国界显示 / 背面遮挡关闭 / 日夜关闭"
    });
  });
});

describe("visualSatelliteModelRenderSatellites", () => {
  const satellites = Array.from({ length: 8 }, (_, index) => ({
    satellite_id: `sat-${index}`
  }));

  it("keeps model rendering bounded by default", () => {
    expect(
      visualSatelliteModelRenderSatellites(satellites, 3).map(
        (satellite) => satellite.satellite_id
      )
    ).toEqual(["sat-0", "sat-1", "sat-2"]);
  });

  it("adds the selected satellite model when it is outside the default model budget", () => {
    expect(
      visualSatelliteModelRenderSatellites(satellites, 3, "sat-6").map(
        (satellite) => satellite.satellite_id
      )
    ).toEqual(["sat-0", "sat-1", "sat-2", "sat-6"]);
  });

  it("does not duplicate selected satellites already inside the model budget", () => {
    expect(
      visualSatelliteModelRenderSatellites(satellites, 3, "sat-1").map(
        (satellite) => satellite.satellite_id
      )
    ).toEqual(["sat-0", "sat-1", "sat-2"]);
  });
});
