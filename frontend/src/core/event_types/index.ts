export type EventType =
  | "ORBIT_UPDATE"
  | "LINK_UPDATE"
  | "ACCESS_START"
  | "ACCESS_END"
  | "ROUTE_UPDATE"
  | "TASK_START"
  | "TASK_FINISH"
  | "COMPUTE_NODE_UPDATE"
  | "METRIC_SAMPLE";

export const EVENT_TYPES: readonly EventType[] = [
  "ORBIT_UPDATE",
  "LINK_UPDATE",
  "ACCESS_START",
  "ACCESS_END",
  "ROUTE_UPDATE",
  "TASK_START",
  "TASK_FINISH",
  "COMPUTE_NODE_UPDATE",
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

export interface ComputeNodeState {
  node_id: string;
  sim_time: number;
  capacity: number;
  available_capacity: number;
  status: string;
  load_ratio?: number;
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
    compute_capacity?: number;
    compute_scheduling_policy?: string;
    orbit?: {
      update_interval_seconds?: number;
      plane_count?: number;
      altitude_m?: number;
      inclination_deg?: number;
    };
    traffic_model?: {
      flow_interval_seconds?: number;
      task_interval_seconds?: number;
      flow_demand_capacity?: number;
      task_compute_demand?: number;
      task_data_size?: number;
    };
  };
  network?: {
    application_protocol?: string;
    transport_protocol?: string;
    transport_loss_rate?: number;
    transport_congestion_window_segments?: number;
    routing_protocol?: string;
    datalink_mac_protocol?: string;
    routing_latency_weight?: number;
    routing_inverse_capacity_weight?: number;
    routing_hop_weight?: number;
    carrier_frequency_hz?: number;
    channel_bandwidth_hz?: number;
    rain_rate_mm_h?: number;
    rain_attenuation_coefficient_db_per_km_per_mm_h?: number;
    rain_effective_path_km?: number;
    antenna_diameter_m?: number;
    antenna_aperture_efficiency?: number;
    transmit_power_dbw?: number;
    system_loss_db?: number;
    noise_temperature_k?: number;
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
  compute_nodes?: readonly ComputeNodeState[];
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
  initialized?: boolean;
}

export interface GeneratedScenarioConfig {
  seed: number;
  satellite_count: number;
  user_count: number;
  compute_node_count: number;
  flow_count: number;
  compute_scheduling_policy?: string;
  orbit_plane_count: number;
  epoch: number;
  semi_major_axis_km: number;
  eccentricity: number;
  inclination_deg: number;
  earth_radius_km: number;
  min_elevation_deg: number;
  max_range_km: number;
  compute_capacity: number;
  demand_capacity: number;
  task_compute_demand: number;
  task_data_size: number;
  application_protocol?: string;
  transport_protocol?: string;
  transport_loss_rate?: number;
  transport_congestion_window_segments?: number;
  routing_protocol?: string;
  datalink_mac_protocol?: string;
  routing_latency_weight?: number;
  routing_inverse_capacity_weight?: number;
  routing_hop_weight?: number;
  carrier_frequency_hz?: number;
  channel_bandwidth_hz?: number;
  rain_rate_mm_h?: number;
  rain_attenuation_coefficient_db_per_km_per_mm_h?: number;
  rain_effective_path_km?: number;
  antenna_diameter_m?: number;
  antenna_aperture_efficiency?: number;
  transmit_power_dbw?: number;
  system_loss_db?: number;
  noise_temperature_k?: number;
}

export interface RuntimeStatusEnvelope {
  type?: "RUNTIME_STATUS";
  status: RuntimeStatusPayload;
  config?: unknown;
  generated_config?: GeneratedScenarioConfig;
}
