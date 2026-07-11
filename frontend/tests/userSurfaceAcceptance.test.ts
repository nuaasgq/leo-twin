import { describe, expect, it } from "vitest";

import appSource from "../src/app/App.tsx?raw";
import configPanelSource from "../src/config_panel/ConfigPanel.tsx?raw";
import dashboardSource from "../src/dashboard/Dashboard.tsx?raw";
import userOverviewSource from "../src/dashboard/user_overview/UserOverview.tsx?raw";

describe("user-facing frontend acceptance", () => {
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
    expect(userOverviewSource).toContain('className="user-overview-kpis"');
    expect(userOverviewSource).toContain('className="user-overview-charts"');
    expect(userOverviewSource).toContain('className="user-overview-business"');
    expect(userOverviewSource).toContain("高级诊断");
  });

  it("keeps only essential simulation controls expanded on the control surface", () => {
    expect(configPanelSource).toContain('aria-label="专业算力配置"');
    expect(configPanelSource).toContain('aria-label="业务详细参数"');
    expect(configPanelSource).toContain(
      'className="config-section config-disclosure" aria-label={CONFIG_PANEL_SECTION_LABELS.orbit}'
    );
    expect(configPanelSource).toContain(
      'className="config-section config-disclosure" aria-label={CONFIG_PANEL_SECTION_LABELS.network}'
    );
    expect(configPanelSource).toContain(
      'className="config-section config-disclosure" aria-label={CONFIG_PANEL_SECTION_LABELS.physical}'
    );
    expect(configPanelSource).toContain('className="config-subsection-content"');
  });

  it("loads operator diagnostics only after the advanced dashboard is opened", () => {
    const advancedGuards = appSource.match(
      /surface !== "dashboard" \|\| !advancedDashboardVisible/g
    );
    expect(advancedGuards).toHaveLength(3);
  });
});
