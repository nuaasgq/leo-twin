export type EventType =
  | "ORBIT_UPDATE"
  | "LINK_UPDATE"
  | "ACCESS_START"
  | "ACCESS_END"
  | "ROUTE_UPDATE"
  | "TASK_START"
  | "TASK_FINISH"
  | "METRIC_SAMPLE";

export const EVENT_TYPES: readonly EventType[] = [
  "ORBIT_UPDATE",
  "LINK_UPDATE",
  "ACCESS_START",
  "ACCESS_END",
  "ROUTE_UPDATE",
  "TASK_START",
  "TASK_FINISH",
  "METRIC_SAMPLE"
] as const;

export interface SimEvent<TPayload = unknown> {
  event_id: string | number;
  sim_time: number;
  priority: number;
  source: string;
  target: string;
  event_type: EventType;
  payload: TPayload;
}

export interface SatelliteState {
  satellite_id: string;
  sim_time: number;
  position: Vector3;
  velocity?: Vector3;
  status: string;
}

export interface GroundUserState {
  user_id: string;
  position?: GeoPosition;
  cell_id?: string;
  status?: string;
}

export interface LinkState {
  source_id: string;
  target_id: string;
  latency: number;
  capacity: number;
  availability: boolean;
  utilization?: number;
}

export interface Route {
  route_id: string;
  flow_id: string;
  path: readonly string[];
  latency: number;
  capacity: number;
  available: boolean;
}

export interface TaskState {
  task_id: string;
  node_id: string;
  sim_time: number;
  progress: number;
  status: string;
}

export interface MetricRecord {
  metric_name: string;
  sim_time: number;
  entity_id: string;
  value: string | number | boolean;
  tags?: readonly [string, string][];
}

export interface ScenarioConfig {
  scenario_id?: string;
  satellites?: readonly { satellite_id: string; label?: string }[];
  ground_users?: readonly GroundUserState[];
  render?: {
    beam_length_m?: number;
    beam_radius_m?: number;
    max_satellites?: number;
  };
  scenario?: {
    satellite_count?: number;
    user_count?: number;
    compute_nodes?: number;
  };
  runtime?: {
    mode?: RuntimeMode;
    speed_factor?: number;
    seed?: number;
    duration?: number;
    status?: RuntimeStatus;
  };
  ui?: {
    visualization?: {
      satellites?: boolean;
      links?: boolean;
      users?: boolean;
      metrics?: boolean;
    };
    update_frequency_hz?: number;
    dashboard_layout?: string;
  };
  endpoints?: {
    events?: string;
    state?: string;
    metrics?: string;
    config?: string;
    control?: string;
    runtime_status?: string;
  };
}

export interface StateSnapshot {
  satellites?: readonly SatelliteState[];
  ground_users?: readonly GroundUserState[];
  links?: readonly LinkState[];
  routes?: readonly Route[];
  tasks?: readonly TaskState[];
  metrics?: readonly MetricRecord[];
}

export type Vector3 = readonly [number, number, number];
export type GeoPosition = readonly [number, number, number?];
export type RuntimeMode = "REAL_TIME" | "ACCELERATED" | "PAUSED";
export type RuntimeStatus = "STOPPED" | "RUNNING" | "PAUSED";

export interface RuntimeStatusPayload {
  status: RuntimeStatus;
  mode: RuntimeMode;
  speed_factor: number;
  seed: number;
  duration: number;
  config_version: number;
  last_action: string;
}
