import { memo } from "react";

import { WorldSnapshot } from "../state/snapshot_engine";
import { ComputeView } from "./compute_view/ComputeView";
import { NetworkView } from "./network_view/NetworkView";
import { OrbitPanel } from "./orbit_panel/OrbitPanel";
import { SystemHealth } from "./system_health/SystemHealth";

export const Dashboard = memo(function Dashboard({ snapshot }: { snapshot: WorldSnapshot }) {
  return (
    <aside className="dashboard" aria-label="Observability dashboard">
      <NetworkView snapshot={snapshot} />
      <ComputeView snapshot={snapshot} />
      <OrbitPanel snapshot={snapshot} />
      <SystemHealth snapshot={snapshot} />
    </aside>
  );
});
