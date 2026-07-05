import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("dashboard scroll layout CSS", () => {
  const appCss = readFileSync("src/app/App.css", "utf8");
  const dataPanelSource = readFileSync("src/dashboard/data_panel/DataPanel.tsx", "utf8");

  it("allows page-level scrolling for the standalone dashboard", () => {
    expect(appCss).toContain('body[data-frontend-surface="dashboard"]');
    expect(appCss).toContain("overflow-y: auto;");
    expect(appCss).toContain('body[data-frontend-surface="dashboard"] .app-shell');
    expect(appCss).toContain("grid-template-rows: 66px minmax(0, 1fr);");
    expect(appCss).toContain("height: auto;");
    expect(appCss).toContain("overflow: visible;");
    expect(appCss).toContain('body[data-frontend-surface="dashboard"] .dashboard-page');
    expect(appCss).toContain("overflow-y: visible;");
  });

  it("keeps user and satellite detail tables visibly scrollable", () => {
    expect(appCss).toContain(".data-panel-detail-table");
    expect(appCss).toContain("min-height: 500px;");
    expect(appCss).toContain("max-height: min(780px, 76vh);");
    expect(appCss).toContain(".data-panel-table-scroll");
    expect(appCss).toContain("overflow: auto;");
  });

  it("shows observability scope notes inline without a floating overlay", () => {
    expect(appCss).toContain(".data-panel-observability-notes");
    expect(appCss).toContain("grid-template-columns: repeat(4, minmax(0, 1fr));");
    expect(appCss).toContain(".data-panel-observability-note.limit");
    expect(appCss).toContain(".data-panel-observability-note.history");
  });

  it("keeps dashboard notices in document flow instead of covering panel content", () => {
    expect(appCss).toContain(".fidelity-notice.dashboard");
    expect(appCss).toContain("position: relative;");
    expect(appCss).toContain("margin: 14px 18px 0;");
    expect(appCss).toContain(".fidelity-notice.completion.dashboard");
    expect(appCss).toContain("max-height: 92px;");
    expect(appCss).toContain("grid-template-columns: auto minmax(0, 1fr);");
  });

  it("uses a denser information hierarchy for the standalone data panel", () => {
    expect(appCss).toContain(".data-panel-summary");
    expect(appCss).toContain("grid-template-columns: repeat(4, minmax(0, 1fr));");
    expect(appCss).toContain(".data-panel-chart-grid");
    expect(appCss).toContain("grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr);");
    expect(appCss).toContain(".data-panel-chart.wide");
    expect(appCss).toContain("grid-column: 1 / -1;");
    expect(appCss).toContain(".data-panel-grid");
    expect(appCss).toContain("grid-template-columns: repeat(4, minmax(0, 1fr));");
    expect(appCss).toContain("min-height: 180px;");
  });

  it("places user and satellite detail tables before auxiliary model analysis", () => {
    expect(dataPanelSource.indexOf("用户节点与卫星运行明细")).toBeGreaterThan(-1);
    expect(dataPanelSource.indexOf("辅助模型分析")).toBeGreaterThan(-1);
    expect(dataPanelSource.indexOf("用户节点与卫星运行明细")).toBeLessThan(
      dataPanelSource.indexOf("辅助模型分析")
    );
  });

  it("shows visual layer budget details inline in the globe controls", () => {
    expect(appCss).toContain(".globe-layer-summary small");
    expect(appCss).toContain("grid-column: 1 / -1;");
    expect(appCss).toContain("font-size: 9px;");
  });
});
