import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("user-facing frontend acceptance", () => {
  const appSource = readFileSync("src/app/App.tsx", "utf8");
  const dashboardSource = readFileSync("src/dashboard/Dashboard.tsx", "utf8");
  const appCss = readFileSync("src/app/App.css", "utf8");

  it("keeps engineering diagnostics behind explicit disclosure controls", () => {
    expect(appSource).toContain("const [advancedDashboardVisible, setAdvancedDashboardVisible]");
    expect(appSource).toContain("!advancedDashboardVisible ? (");
    expect(appSource.indexOf("<UserOverview")).toBeLessThan(appSource.indexOf("<DataPanel"));
    expect(appSource).toContain("高级诊断");
    expect(dashboardSource).toContain('<details className="dashboard-advanced">');
    expect(dashboardSource.indexOf("<NetworkView")).toBeLessThan(
      dashboardSource.indexOf('<details className="dashboard-advanced">')
    );
  });

  it("uses a compact responsive overview without horizontal overflow patterns", () => {
    expect(appCss).toContain(".user-overview-kpis");
    expect(appCss).toContain("grid-template-columns: repeat(4, minmax(0, 1fr));");
    expect(appCss).toContain(".user-overview-charts");
    expect(appCss).toContain(".sync-pill,");
    expect(appCss).toContain(".connection-diagnostics");
    expect(appCss).toContain("display: none;");
  });
});
