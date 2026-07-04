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
  demand_capacity?: number;
  loss_rate?: number;
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
  cpu_gflops_fp64?: number;
  gpu_tflops_fp32?: number;
  gpu_tflops_fp16?: number;
  npu_tops_int8?: number;
  memory_gb?: number;
  storage_gb?: number;
  resource_usage_mode?: string;
  available_cpu_gflops_fp32?: number;
  used_cpu_gflops_fp32?: number;
  available_cpu_gflops_fp64?: number;
  used_cpu_gflops_fp64?: number;
  available_gpu_tflops_fp32?: number;
  used_gpu_tflops_fp32?: number;
  available_gpu_tflops_fp16?: number;
  used_gpu_tflops_fp16?: number;
  available_npu_tops_int8?: number;
  used_npu_tops_int8?: number;
  available_memory_gb?: number;
  used_memory_gb?: number;
  available_storage_gb?: number;
  used_storage_gb?: number;
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
  backend_summary?: BackendDerivedSummary;
  derived_constellation_summary?: ConstellationDerivedSummary;
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
    compute_cpu_gflops_fp64?: number;
    compute_gpu_tflops_fp32?: number;
    compute_gpu_tflops_fp16?: number;
    compute_npu_tops_int8?: number;
    compute_memory_gb?: number;
    compute_storage_gb?: number;
    compute_scheduling_policy?: string;
    initial_workload_smoothing_enabled?: boolean;
    initial_workload_window_s?: number;
    max_initial_events_per_tick?: number;
    workload_smoothing_mode?: string;
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
      traffic_class?: string;
      destination_type?: string;
      output_data_size?: number;
      initial_workload_smoothing_enabled?: boolean;
      initial_workload_window_s?: number;
      max_initial_events_per_tick?: number;
      workload_smoothing_mode?: string;
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
    space_link_mode?: string | null;
    max_space_link_candidates_per_satellite?: number;
    batch_space_link_update_limit?: number;
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

export interface ConstellationDerivedSummary {
  profile: string;
  satellite_count: number;
  plane_count: number;
  satellites_per_plane: number;
  satellites_per_plane_distribution?: readonly number[];
  total_slots: number;
  plane_count_explicit: boolean;
  model_note: string;
  altitude_m?: number;
  orbital_period_minutes?: number;
  orbital_period_model_note?: string;
  orbital_velocity_km_s?: number;
  orbital_velocity_model_note?: string;
  inclination_deg?: number;
  raan_spacing_deg?: number;
  mean_anomaly_spacing_deg?: number;
  phase_policy?: string;
}

export interface TrafficDemandSummary {
  traffic_class: string;
  traffic_class_label?: string;
  destination_type: string;
  destination_type_label?: string;
  generated_flow_count: number;
  arrival_model: string;
  input_data_size_mb: number;
  output_data_size_mb: number;
  priority: number;
  demand_capacity_mbps: number;
  task_compute_demand: number;
  execution_shape?: string;
  execution_label?: string;
  requires_compute_node_destination?: boolean;
  compatibility_note?: string;
  lifecycle_note?: string;
  arrival_interval_seconds?: number;
}

export interface ComputeResourceSummary {
  resource_model: string;
  node_role: string;
  compute_node_count: number;
  legacy_capacity_per_node: number;
  cpu_gflops_fp32_per_node: number;
  cpu_gflops_fp64_per_node: number;
  gpu_tflops_fp32_per_node: number;
  gpu_tflops_fp16_per_node: number;
  npu_tops_int8_per_node: number;
  memory_gb_per_node: number;
  storage_gb_per_node: number;
  total_cpu_gflops_fp32: number;
  total_cpu_gflops_fp64: number;
  total_gpu_tflops_fp32: number;
  total_gpu_tflops_fp16: number;
  total_npu_tops_int8: number;
  total_memory_gb: number;
  total_storage_gb: number;
  capacity_unit: string;
  compatibility_note: string;
}

export interface FidelitySummary {
  orbit_update_mode: string;
  metrics_mode: string;
  space_link_mode: string;
  detailed_space_link_enabled: boolean;
  space_link_candidate_policy: string;
  max_space_link_candidates_per_satellite: number;
  batch_space_link_update_limit: number;
  scale_limit_reason: string;
  current_scale_mode: string;
  fidelity_warnings: readonly string[];
  satellite_count: number;
  user_count: number;
}

export interface BackendDerivedSummary {
  derived_constellation_summary?: ConstellationDerivedSummary;
  traffic_demand_summary?: TrafficDemandSummary;
  compute_resource_summary?: ComputeResourceSummary;
  coverage_beam_summary?: CoverageBeamSummary;
  fidelity_summary?: FidelitySummary;
  workload_smoothing_summary?: WorkloadSmoothingSummary;
  model_assumptions?: readonly string[];
}

export interface CoverageBeamSummary {
  coverage_model: string;
  fidelity_level?: string;
  selected_satellite_detail_mode: string;
  beam_pattern: string;
  footprint_intersection_policy?: string;
  default_beam_count: number;
  beam_radius_m: number;
  beam_length_m: number;
  global_beam_render_limit: number;
  excluded_physics?: readonly string[];
  model_note: string;
  intersection_note?: string;
}

export interface WorkloadSmoothingSummary {
  enabled: boolean;
  mode: string;
  scale_triggered: boolean;
  initial_workload_window_s: number;
  max_initial_events_per_tick: number;
  workload_count: number;
  spacing_s: number;
}

export interface RuntimeProfilingSummary {
  orbit_batch_update_time_ms: number;
  network_batch_ingestion_time_ms: number;
  access_update_time_ms: number;
  space_space_candidate_update_time_ms: number;
  flow_arrival_processing_time_ms: number;
  route_update_time_ms: number;
  compute_task_arrival_processing_time_ms: number;
  compute_queue_update_time_ms: number;
  metrics_aggregation_time_ms: number;
  snapshot_projection_time_ms: number;
  total_tick_time_ms: number;
  processed_event_count: number;
  event_type_counts?: Record<string, number>;
}

export interface RuntimeBackpressureSummary {
  tick_duration_ms: number;
  tick_budget_ms: number;
  overloaded: boolean;
  queue_depth: number;
  processed_event_count: number;
  deferred_event_count: number;
  first_tick_heavy: boolean;
  bottleneck_component: string;
  recommended_action: string;
}

export interface StateSnapshot {
  event_count?: number;
  last_sim_time?: number;
  satellites?: readonly SatelliteState[];
  ground_users?: readonly GroundUserState[];
  links?: readonly LinkState[];
  routes?: readonly Route[];
  tasks?: readonly TaskState[];
  compute_nodes?: readonly ComputeNodeState[];
  metrics?: readonly MetricRecord[];
  fidelity_summary?: FidelitySummary;
}

export type Vector3 = readonly [number, number, number];
export type GeoPosition = readonly [number, number, number?];
export type RuntimeMode = "REAL_TIME" | "ACCELERATED" | "PAUSED";
export type RuntimeStatus = "STOPPED" | "RUNNING" | "PAUSED";
export type RuntimeLifecycleState =
  | "UNINITIALIZED"
  | "INITIALIZED"
  | "RUNNING"
  | "PAUSED"
  | "STOPPED"
  | "COMPLETED"
  | "ERROR";

export interface RuntimeStatusPayload {
  status: RuntimeStatus;
  lifecycle_state?: RuntimeLifecycleState;
  mode: RuntimeMode;
  speed_factor: number;
  seed: number;
  duration: number;
  config_version: number;
  last_action: string;
  initialized?: boolean;
  current_sim_time?: number;
  wall_clock_start_time?: number | null;
  processed_event_count?: number;
  queued_event_count?: number | null;
  deterministic_replay?: boolean;
  last_error?: string | null;
  fidelity_summary?: FidelitySummary;
  metrics_summary?: RuntimeMetricsSummary;
  kpi_time_series_v1?: RuntimeKpiTimeSeriesV1;
  profiling_summary?: RuntimeProfilingSummary | null;
  backpressure_summary?: RuntimeBackpressureSummary | null;
}

export type RuntimeMetricsSummaryValue = string | number | boolean | null;
export type RuntimeMetricsSummary = Record<string, RuntimeMetricsSummaryValue>;

export interface RuntimeKpiTimeSeriesV1 {
  version: "v1" | string;
  sample_count?: number;
  tail_sample_source?: string;
  tail_sample_source_label?: string;
  samples: readonly RuntimeKpiSampleV1[];
}

export interface RuntimeKpiSampleV1 {
  sim_time: number;
  network_effective_throughput_mbps: number;
  network_requested_route_demand_mbps?: number;
  network_demand_pressure_proxy?: number;
  network_effective_latency_s: number;
  network_effective_loss_proxy_rate: number;
  network_effective_delay_variation_s: number;
  compute_resource_used_gflops_fp32: number;
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
  compute_cpu_gflops_fp64?: number;
  compute_gpu_tflops_fp32?: number;
  compute_gpu_tflops_fp16?: number;
  compute_npu_tops_int8?: number;
  compute_memory_gb?: number;
  compute_storage_gb?: number;
  demand_capacity: number;
  task_compute_demand: number;
  task_data_size: number;
  traffic_class?: string;
  traffic_destination_type?: string;
  traffic_output_data_size?: number;
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
  space_link_mode?: string | null;
  max_space_link_candidates_per_satellite?: number;
  batch_space_link_update_limit?: number;
  backend_summary?: BackendDerivedSummary;
}

export interface RuntimeStatusEnvelope {
  type?: "RUNTIME_STATUS";
  status: RuntimeStatusPayload;
  config?: unknown;
  generated_config?: GeneratedScenarioConfig;
}
