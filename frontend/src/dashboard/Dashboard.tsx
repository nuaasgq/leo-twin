import { memo } from "react";

import { WorldSnapshot } from "../state/snapshot_engine";
import { ComputeQueuePanel } from "./compute_queue/ComputeQueuePanel";
import { ComputeView } from "./compute_view/ComputeView";
import { DomainSummary } from "./domain_summary/DomainSummary";
import { LinkProtocolPanel } from "./link_protocol/LinkProtocolPanel";
import { NetworkView } from "./network_view/NetworkView";
import { OrbitPanel } from "./orbit_panel/OrbitPanel";
import { SystemHealth } from "./system_health/SystemHealth";

export const Dashboard = memo(function Dashboard({ snapshot }: { snapshot: WorldSnapshot }) {
  return (
    <aside className="dashboard" aria-label="仿真状态仪表盘">
      <DomainSummary snapshot={snapshot} />
      <LinkProtocolPanel snapshot={snapshot} />
      <NetworkView snapshot={snapshot} />
      <ComputeView snapshot={snapshot} />
      <ComputeQueuePanel snapshot={snapshot} />
      <OrbitPanel snapshot={snapshot} />
      <SystemHealth snapshot={snapshot} />
    </aside>
  );
});
