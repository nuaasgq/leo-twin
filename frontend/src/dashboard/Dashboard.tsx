import { ObservabilityState } from "../stream/state_store";
import { ComputeView } from "./compute_view/ComputeView";
import { NetworkView } from "./network_view/NetworkView";
import { OrbitPanel } from "./orbit_panel/OrbitPanel";
import { SystemHealth } from "./system_health/SystemHealth";

export function Dashboard({ state }: { state: ObservabilityState }) {
  return (
    <aside className="dashboard" aria-label="Observability dashboard">
      <NetworkView state={state} />
      <ComputeView state={state} />
      <OrbitPanel state={state} />
      <SystemHealth state={state} />
    </aside>
  );
}
