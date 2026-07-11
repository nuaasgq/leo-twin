import { memo } from "react";

import { WorldSnapshot } from "../state/snapshot_engine";
import { ChannelHealthPanel } from "./channel_health/ChannelHealthPanel";
import { CouplingFeedbackPanel } from "./coupling_feedback/CouplingFeedbackPanel";
import { ComputeQueuePanel } from "./compute_queue/ComputeQueuePanel";
import { ComputeView } from "./compute_view/ComputeView";
import { DomainSummary } from "./domain_summary/DomainSummary";
import { GroundTrackPanel } from "./ground_track/GroundTrackPanel";
import { LinkProtocolPanel } from "./link_protocol/LinkProtocolPanel";
import { NetworkView } from "./network_view/NetworkView";
import { OrbitPanel } from "./orbit_panel/OrbitPanel";
import { SystemHealth } from "./system_health/SystemHealth";
import { TopologyChangePanel } from "./topology_change/TopologyChangePanel";

export const Dashboard = memo(function Dashboard({ snapshot }: { snapshot: WorldSnapshot }) {
  return (
    <aside className="dashboard" aria-label="仿真状态仪表盘">
      <DomainSummary snapshot={snapshot} />
      <NetworkView snapshot={snapshot} />
      <ComputeView snapshot={snapshot} />
      <details className="dashboard-advanced">
        <summary>高级诊断</summary>
        <div className="dashboard-advanced-content">
          <TopologyChangePanel snapshot={snapshot} />
          <LinkProtocolPanel snapshot={snapshot} />
          <CouplingFeedbackPanel snapshot={snapshot} />
          <ChannelHealthPanel snapshot={snapshot} />
          <ComputeQueuePanel snapshot={snapshot} />
          <OrbitPanel snapshot={snapshot} />
          <GroundTrackPanel snapshot={snapshot} />
          <SystemHealth snapshot={snapshot} />
        </div>
      </details>
    </aside>
  );
});
