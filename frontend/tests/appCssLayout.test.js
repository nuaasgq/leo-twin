import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("dashboard scroll layout CSS", () => {
  const appCss = readFileSync("src/app/App.css", "utf8");

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
    expect(appCss).toContain("min-height: 420px;");
    expect(appCss).toContain("max-height: min(720px, 72vh);");
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
  });

  it("shows visual layer budget details inline in the globe controls", () => {
    expect(appCss).toContain(".globe-layer-summary small");
    expect(appCss).toContain("grid-column: 1 / -1;");
    expect(appCss).toContain("font-size: 9px;");
  });
});
