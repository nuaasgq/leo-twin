import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("dashboard scroll layout CSS", () => {
  const appCss = readFileSync("src/app/App.css", "utf8");

  it("keeps the standalone dashboard as the scroll container", () => {
    expect(appCss).toContain('body[data-frontend-surface="dashboard"] .app-shell');
    expect(appCss).toContain("grid-template-rows: 66px minmax(0, 1fr);");
    expect(appCss).toContain('body[data-frontend-surface="dashboard"] .dashboard-page');
    expect(appCss).toContain("overflow-y: auto;");
  });

  it("keeps user and satellite detail tables visibly scrollable", () => {
    expect(appCss).toContain(".data-panel-detail-table");
    expect(appCss).toContain("min-height: 420px;");
    expect(appCss).toContain("max-height: min(720px, 72vh);");
    expect(appCss).toContain(".data-panel-table-scroll");
    expect(appCss).toContain("overflow: auto;");
  });
});
