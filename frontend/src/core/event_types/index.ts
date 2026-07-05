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
  generated_task_count?: number;
  generated_output_flow_metadata_count?: number;
  arrival_model: string;
  source_selection_policy?: string;
  destination_selection_policy?: string;
  input_data_size_mb: number;
  output_data_size_mb: number;
  total_input_data_mb?: number;
  total_output_data_mb?: number;
  priority: number;
  demand_capacity_mbps: number;
  task_compute_demand: number;
  service_mix_mode?: string;
  service_mix_weights?: Record<string, number>;
  service_mix_normalized_weights?: Record<string, number>;
  active_service_classes?: readonly string[];
  service_mix_generated_request_counts?: Record<string, number>;
  execution_shape?: string;
  execution_label?: string;
  requires_compute_node_destination?: boolean;
  compatibility_note?: string;
  lifecycle_note?: string;
  arrival_interval_seconds?: number;
  system_request_rate_per_minute?: number;
  average_user_request_rate_per_minute?: number;
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
  compute_resource_contract_v2?: ComputeResourceContractV2;
  service_placement_contract_v2?: ServicePlacementContractV2;
  coverage_beam_summary?: CoverageBeamSummary;
  network_model_contract_v2?: NetworkModelContractV2;
  fidelity_summary?: FidelitySummary;
  workload_smoothing_summary?: WorkloadSmoothingSummary;
  configuration_surface_summary?: ConfigurationSurfaceSummary;
  model_assumptions?: readonly string[];
}

export interface ComputeResourceContractV2 {
  contract_id: string;
  version: "v2" | string;
  resource_model: string;
  node_role: string;
  resource_lanes: readonly ComputeResourceLaneContractV2[];
  task_demand_lanes: readonly TaskDemandLaneContractV2[];
  service_time_estimator: ComputeServiceTimeEstimatorContractV2;
  runtime_event_inputs: readonly string[];
  runtime_state_outputs: readonly string[];
  deterministic_inputs: readonly string[];
  model_note: string;
  configured_node_profile?: ComputeResourceConfiguredNodeProfileV2;
}

export interface ComputeResourceLaneContractV2 {
  lane: string;
  capacity_field: string;
  unit: string;
  node_state_capacity_field: string;
  node_state_used_field: string;
  node_state_available_field: string;
  throughput_lane: boolean;
  compatibility_role: string;
}

export interface TaskDemandLaneContractV2 {
  lane: string;
  demand_field: string;
  required_resource_lane: string;
  unit: string;
  estimator_role: string;
}

export interface ComputeServiceTimeEstimatorContractV2 {
  estimator_id: string;
  model: string;
  formula_summary: string;
  bottleneck_policy: string;
  capacity_limit_policy: string;
  legacy_mapping: string;
  excluded_semantics: readonly string[];
}

export interface ComputeResourceConfiguredNodeProfileV2 {
  compute_node_count: number;
  legacy_capacity_per_node: number;
  cpu_gflops_fp32_per_node: number;
  cpu_gflops_fp64_per_node: number;
  gpu_tflops_fp32_per_node: number;
  gpu_tflops_fp16_per_node: number;
  npu_tops_int8_per_node: number;
  memory_gb_per_node: number;
  storage_gb_per_node: number;
}

export interface ServicePlacementContractV2 {
  contract_id: string;
  version: "v2" | string;
  placement_model: string;
  default_policy: string;
  candidate_source: string;
  candidate_order: readonly string[];
  decision_fields: readonly string[];
  rejection_reasons: readonly string[];
  queue_semantics: string;
  deterministic_inputs: readonly string[];
  excluded_semantics: readonly string[];
  model_note: string;
  configured_policy?: ServicePlacementConfiguredPolicyV2;
}

export interface ServicePlacementConfiguredPolicyV2 {
  compute_node_count: number;
  default_policy: string;
  queue_state_source: string;
  max_queue_depth: number | null;
  candidate_count_policy: string;
}

export interface NetworkModelContractV2 {
  contract_id: string;
  version: "v2" | string;
  fidelity: string;
  packet_level_simulation: boolean;
  layer_contracts: readonly NetworkLayerContractV2[];
  kpi_contracts: readonly NetworkKpiContractV2[];
  event_inputs: readonly string[];
  deterministic_inputs: readonly string[];
  excluded_capabilities: readonly string[];
  model_note: string;
  configured_protocol_profile?: NetworkConfiguredProtocolProfileV2;
}

export interface NetworkLayerContractV2 {
  layer: string;
  product_name: string;
  responsibility: string;
  input_contracts: readonly string[];
  output_contracts: readonly string[];
  state_sources: readonly string[];
  excluded_semantics: readonly string[];
}

export interface NetworkKpiContractV2 {
  metric: string;
  runtime_summary_key: string;
  display_name: string;
  layer: string;
  unit: string;
  source_fields: readonly string[];
  formula_summary: string;
  interpretation: string;
  zero_value_semantics: string;
  packet_level_metric: boolean;
}

export interface NetworkConfiguredProtocolProfileV2 {
  application_protocol: string;
  transport_protocol: string;
  routing_protocol: string;
  datalink_mac_protocol: string;
}

export interface ConfigurationSurfaceSummary {
  version: "v1" | string;
  schema_version?: "v2" | string;
  schema_id?: string;
  source: string;
  detailed_config_file: string;
  template_config_file: string;
  template_profiles?: readonly ConfigurationTemplateProfile[];
  frontend_policy: string;
  key_field_count: number;
  detailed_field_count: number;
  key_fields: readonly ConfigurationSurfaceField[];
  detailed_file_sections: readonly ConfigurationSurfaceSection[];
  file_only_sections?: readonly ConfigurationSurfaceSection[];
  file_only_fields: readonly string[];
  user_config_schema_v2?: UserConfigurationSchemaV2;
  notes?: readonly string[];
}

export interface ConfigurationTemplateProfile {
  id: string;
  label: string;
  path: string;
  purpose: string;
}

export interface ConfigurationSurfaceField {
  path: string;
  label: string;
  section: string;
  value: string | number | boolean | null;
  role: string;
  editable_in_ui: boolean;
  unit?: string;
}

export interface ConfigurationSurfaceSection {
  section: string;
  purpose: string;
  field_count: number;
  example_paths: readonly string[];
}

export interface UserConfigurationSchemaV2 {
  version: "v2" | string;
  schema_id: string;
  source: string;
  format: string;
  unknown_key_policy: string;
  defaulting_policy: string;
  frontend_policy: string;
  forbidden_integrations: readonly string[];
  packet_level_simulation: boolean;
  field_count: number;
  key_field_count: number;
  file_only_field_count: number;
  root_sections: readonly UserConfigurationSchemaSectionV2[];
  fields: readonly UserConfigurationFieldSchemaV2[];
  templates: readonly UserConfigurationTemplateReferenceV2[];
  examples: readonly UserConfigurationExampleV2[];
  notes?: readonly string[];
}

export interface UserConfigurationSchemaSectionV2 {
  path: string;
  purpose: string;
}

export interface UserConfigurationFieldSchemaV2 {
  path: string;
  section: string;
  label: string;
  description: string;
  value_type: string;
  default_value: string | number | boolean | null;
  current_value: string | number | boolean | null;
  required_in_effective_config: boolean;
  required_in_user_file: boolean;
  editable_surface: string;
  validation_rules: readonly string[];
  enum_values?: readonly string[];
  nullable?: boolean;
  unit?: string;
  minimum?: number;
  maximum?: number;
  exclusive_minimum?: number;
  exclusive_maximum?: number;
}

export interface UserConfigurationTemplateReferenceV2 {
  id: string;
  path: string;
  scale: string;
  comment_policy: string;
}

export interface UserConfigurationExampleV2 {
  id: string;
  purpose: string;
  mapping: Record<string, unknown>;
  expected: string;
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

export interface RuntimeReproducibilityManifestV1 {
  version: "v1" | string;
  source: string;
  manifest_id: string;
  session_id: string;
  seed?: number | string | null;
  duration_s?: number | string | null;
  runtime_mode?: string | null;
  speed_factor?: number | string | null;
  config_version?: number | string | null;
  deterministic_replay?: boolean | null;
  runtime_state?: Record<string, RuntimeMetricsSummaryValue | RuntimeMetricsSummary>;
  scenario_hash: string;
  control_config_hash: string;
  generated_config_hash: string;
  metrics_summary_hash: string;
  runtime_state_hash: string;
  manifest_hash: string;
  artifact_policy: string;
  artifact_policy_note?: string;
  artifacts: readonly RuntimeReproducibilityArtifactV1[];
  artifact_count?: number;
  excluded_runtime_fields?: readonly string[];
  notes?: readonly string[];
}

export interface RuntimeReproducibilityArtifactV1 {
  name: string;
  format: string;
  status: string;
  source: string;
}

export interface RuntimeExportHistoryV1 {
  version: "v1" | string;
  source: string;
  history_scope: string;
  history_limit: number;
  export_count: number;
  retained_count: number;
  latest_export?: RuntimeExportHistoryRecordV1 | null;
  items: readonly RuntimeExportHistoryRecordV1[];
}

export interface RuntimeExportHistoryRecordV1 {
  sequence: number;
  export_type: "PACKAGE" | "ARCHIVE" | string;
  package_id: string;
  package_dir: string;
  file_count: number;
  manifest_hash: string;
  current_sim_time: number;
  processed_event_count: number;
  archive_filename?: string;
  archive_sha256?: string;
  archive_bytes?: number;
}

export interface RuntimeExportHistoryEnvelope {
  type: "RUNTIME_EXPORT_HISTORY" | string;
  summary: RuntimeExportHistoryV1;
}

export interface RuntimeExportCatalogV1 {
  version: "v1" | string;
  source: string;
  catalog_scope: string;
  catalog_file: string;
  export_root: string;
  record_count: number;
  catalog_hash: string;
  latest_export?: RuntimeExportCatalogRecordV1 | null;
  records: readonly RuntimeExportCatalogRecordV1[];
}

export interface RuntimeExportCatalogRecordV1 {
  catalog_key: string;
  export_type: "PACKAGE" | "ARCHIVE" | string;
  package_id: string;
  package_dir: string;
  relative_package_dir: string;
  file_count: number;
  manifest_hash: string;
  current_sim_time: number;
  processed_event_count: number;
  files: readonly RuntimeExportCatalogFileV1[];
  archive_filename?: string;
  archive_sha256?: string;
  archive_bytes?: number;
}

export interface RuntimeExportCatalogFileV1 {
  name: string;
  filename: string;
  bytes: number;
  sha256: string;
}

export interface RuntimeExportCatalogEnvelope {
  type: "RUNTIME_EXPORT_CATALOG" | string;
  summary: RuntimeExportCatalogV1;
}

export interface RuntimeExportPackageCompareV1 {
  version: "v1" | string;
  source: string;
  comparison_scope: string;
  package_id: string;
  compatibility: "MATCH" | "DIFFERENT" | string;
  same_config: boolean;
  same_generated_config: boolean;
  same_manifest_hash: boolean;
  package_manifest_hash: string;
  current_manifest_hash: string;
  diff_count: number;
  diff_limit: number;
  diff_truncated: boolean;
  sections: readonly RuntimeExportPackageCompareSectionV1[];
  differences: readonly RuntimeExportPackageCompareDifferenceV1[];
  compare_hash: string;
}

export interface RuntimeExportPackageCompareSectionV1 {
  section: string;
  diff_count: number;
  matches: boolean;
}

export interface RuntimeExportPackageCompareDifferenceV1 {
  section: string;
  path: string;
  package_missing: boolean;
  current_missing: boolean;
  package_value: unknown;
  current_value: unknown;
}

export interface RuntimeExportPackageCompareEnvelope {
  type: "RUNTIME_EXPORT_PACKAGE_COMPARE" | string;
  summary: RuntimeExportPackageCompareV1;
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
export type RuntimeStatus =
  | "UNINITIALIZED"
  | "INITIALIZED"
  | "STOPPED"
  | "RUNNING"
  | "PAUSED"
  | "COMPLETED"
  | "ERROR";
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
  configuration_surface_summary?: ConfigurationSurfaceSummary;
  metrics_summary?: RuntimeMetricsSummary;
  network_quality_provenance_v1?: RuntimeNetworkQualityProvenanceV1;
  network_kpi_provenance_v2?: RuntimeNetworkKpiProvenanceV2;
  kpi_time_series_v1?: RuntimeKpiTimeSeriesV1;
  satellite_kpi_slices_v1?: RuntimeSatelliteKpiSlicesV1;
  satellite_kpi_history_v1?: RuntimeSatelliteKpiHistoryV1;
  service_latency_history_v1?: RuntimeServiceLatencyHistoryV1;
  user_request_summary_v1?: RuntimeUserRequestSummaryV1;
  user_request_history_v1?: RuntimeUserRequestHistoryV1;
  satellite_service_summary_v1?: RuntimeSatelliteServiceSummaryV1;
  node_detail_summary_v1?: RuntimeNodeDetailSummaryV1;
  stream_diagnostics_v1?: RuntimeStreamDiagnosticsV1;
  reproducibility_manifest_v1?: RuntimeReproducibilityManifestV1;
  runtime_export_history_v1?: RuntimeExportHistoryV1;
  profiling_summary?: RuntimeProfilingSummary | null;
  backpressure_summary?: RuntimeBackpressureSummary | null;
}

export type RuntimeMetricsSummaryValue = string | number | boolean | null;
export type RuntimeMetricsSummary = Record<string, RuntimeMetricsSummaryValue>;

export interface RuntimeNetworkQualityProvenanceV1 {
  version: "v1" | string;
  metric_model: string;
  packet_level_simulation: boolean;
  proxy_note?: string;
  provenance_note?: string;
  sources: RuntimeNetworkQualityProvenanceSourcesV1;
  zero_reasons: RuntimeNetworkQualityZeroReasonsV1;
}

export interface RuntimeNetworkQualityProvenanceSourcesV1 {
  throughput?: RuntimeNetworkQualitySourceV1;
  latency?: RuntimeNetworkQualitySourceV1;
  loss?: RuntimeNetworkQualitySourceV1;
  delay_variation?: RuntimeNetworkQualitySourceV1;
}

export interface RuntimeNetworkQualityZeroReasonsV1 {
  loss?: RuntimeNetworkQualityZeroReasonV1;
  delay_variation?: RuntimeNetworkQualityZeroReasonV1;
}

export interface RuntimeNetworkQualitySourceV1 {
  source: string;
  label: string;
}

export interface RuntimeNetworkQualityZeroReasonV1 {
  reason: string;
  label: string;
}

export interface RuntimeNetworkKpiProvenanceV2 {
  version: "v2" | string;
  provenance_id: string;
  source: string;
  network_model_contract_id: string;
  network_model_contract_version: string;
  metric_model: string;
  packet_level_simulation: boolean;
  proxy_note?: string;
  provenance_note?: string;
  kpi_count: number;
  kpis: readonly RuntimeNetworkKpiProvenanceItemV2[];
}

export interface RuntimeNetworkKpiProvenanceItemV2 {
  metric: string;
  runtime_summary_key: string;
  current_value: string | number | boolean | null;
  status: string;
  display_name: string;
  layer: string;
  unit: string;
  formula_summary: string;
  interpretation: string;
  zero_value_semantics: string;
  packet_level_metric: boolean;
  observed_source: RuntimeNetworkKpiObservedSourceV2;
  zero_reason?: RuntimeNetworkKpiZeroReasonV2 | null;
  source_fields: readonly RuntimeNetworkKpiSourceFieldV2[];
}

export interface RuntimeNetworkKpiObservedSourceV2 {
  source: string;
  label: string;
}

export interface RuntimeNetworkKpiZeroReasonV2 {
  reason: string;
  label: string;
}

export interface RuntimeNetworkKpiSourceFieldV2 {
  field: string;
  current_value: string | number | boolean | null;
  value_source: string;
}

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
  network_offered_route_capacity_mbps?: number;
  network_available_route_demand_mbps?: number;
  network_demand_pressure_proxy?: number;
  network_throughput_pressure_proxy?: number;
  network_effective_latency_s: number;
  network_route_latency_avg_s?: number;
  network_effective_loss_proxy_rate: number;
  network_route_loss_proxy_rate?: number;
  network_route_blocking_ratio?: number;
  network_failed_flow_ratio?: number;
  network_congestion_proxy?: number;
  network_congestion_loss_proxy_rate?: number;
  network_demand_loss_proxy_rate?: number;
  network_pressure_loss_proxy_rate?: number;
  network_effective_delay_variation_s: number;
  network_route_delay_variation_s?: number;
  network_flow_delay_variation_s?: number;
  network_pressure_delay_variation_s?: number;
  network_effective_available_throughput_mbps?: number;
  network_flow_delivered_capacity_mbps?: number;
  network_recent_window_s?: number;
  network_recent_flow_count?: number;
  network_recent_delivered_throughput_mbps?: number;
  network_recent_latency_s?: number;
  network_recent_loss_proxy_rate?: number;
  network_recent_loss_zero_reason?: string;
  network_recent_loss_zero_reason_label?: string;
  network_recent_delay_variation_s?: number;
  network_recent_delay_variation_zero_reason?: string;
  network_recent_delay_variation_zero_reason_label?: string;
  compute_resource_used_gflops_fp32: number;
  compute_resource_used_gflops_fp64?: number;
  compute_resource_used_gpu_tflops_fp32?: number;
  compute_resource_used_gpu_tflops_fp16?: number;
  compute_resource_used_npu_tops_int8?: number;
  compute_resource_used_memory_gb?: number;
  compute_resource_used_storage_gb?: number;
}

export interface RuntimeUserRequestSummaryV1 {
  version: "v1" | string;
  source: string;
  summary_scope?: string;
  cursor?: number;
  limit?: number;
  next_cursor?: number;
  has_more?: boolean;
  user_count: number;
  item_count: number;
  active_user_count: number;
  compute_service_user_count: number;
  waiting_user_count: number;
  window_user_count?: number;
  window_active_user_count?: number;
  window_compute_service_user_count?: number;
  window_waiting_user_count?: number;
  hidden_user_count: number;
  items: readonly RuntimeUserRequestItemV1[];
}

export interface RuntimeUserRequestItemV1 {
  user_id: string;
  platform_type: string;
  platform_type_label?: string;
  cell_id?: string;
  communication_route_count: number;
  available_route_count: number;
  compute_service_count: number;
  network_queue_count: number;
  network_queue_reason?: string;
  network_queue_reason_label?: string;
  selected_satellite_id?: string;
  destination_id?: string;
  status: string;
  primary_route_id?: string;
  primary_flow_id?: string;
  primary_next_hop_id?: string;
  route_hop_count?: number;
  route_path_label?: string;
  latency_s?: number | null;
  capacity_mbps?: number | null;
  loss_proxy_rate?: number | null;
  service_state?: string;
  service_task_id?: string;
  service_complete?: boolean;
  service_total_latency_s?: number | null;
  input_network_latency_s?: number | null;
  compute_queue_delay_s?: number | null;
  compute_execution_delay_s?: number | null;
  output_network_latency_s?: number | null;
  input_route_id?: string;
  output_route_id?: string;
  compute_node_id?: string;
  service_placement_status?: string;
  service_placement_policy?: string;
  service_placement_bottleneck_resource?: string;
  service_placement_candidate_count?: number | null;
  service_placement_capable_candidate_count?: number | null;
  active_business_type?: string;
  active_business_label?: string;
  request_state?: string;
  request_state_label?: string;
  path: readonly string[];
}

export interface RuntimeUserRequestHistoryV1 {
  version: "v1" | string;
  mode: string;
  source?: string;
  history_scope?: string;
  sample_policy?: string;
  sample_limit?: number;
  user_count?: number;
  summary_item_count?: number;
  hidden_user_count?: number;
  history_user_count?: number;
  series_count?: number;
  series: readonly RuntimeUserRequestHistorySeriesV1[];
}

export interface RuntimeUserRequestHistorySeriesV1 {
  user_id: string;
  sample_count?: number;
  samples: readonly RuntimeUserRequestHistorySampleV1[];
}

export interface RuntimeUserRequestHistorySampleV1 {
  sim_time: number;
  communication_route_count: number;
  available_route_count: number;
  compute_service_count: number;
  network_queue_count: number;
  selected_satellite_id?: string;
  destination_id?: string;
  status: string;
  primary_route_id?: string;
  primary_flow_id?: string;
  latency_s?: number | null;
  capacity_mbps?: number | null;
  loss_proxy_rate?: number | null;
  service_state?: string;
  active_business_type?: string;
  active_business_label?: string;
  request_state?: string;
}

export interface RuntimeSatelliteServiceSummaryV1 {
  version: "v1" | string;
  source: string;
  summary_scope?: string;
  cursor?: number;
  limit?: number;
  next_cursor?: number;
  has_more?: boolean;
  satellite_count: number;
  item_count: number;
  window_satellite_count?: number;
  hidden_satellite_count: number;
  items: readonly RuntimeSatelliteServiceItemV1[];
}

export interface RuntimeDetailPageEnvelope {
  type: "RUNTIME_DETAIL_PAGE" | string;
  kind: "users" | "satellites" | "nodes" | string;
  summary:
    | RuntimeUserRequestSummaryV1
    | RuntimeSatelliteServiceSummaryV1
    | RuntimeNodeDetailPageV1;
}

export interface RuntimeNodeDetailPageV1 {
  version: "v1" | string;
  source: string;
  summary_scope?: string;
  cursor: number;
  limit: number;
  next_cursor: number;
  has_more: boolean;
  node_count: number;
  user_count: number;
  satellite_count: number;
  item_count: number;
  hidden_node_count: number;
  window_user_detail_count: number;
  window_satellite_detail_count: number;
  items: readonly RuntimeNodeDetailCardV1[];
}

export interface RuntimeNodeDetailSummaryV1 {
  version: "v1" | string;
  source: string;
  summary_scope?: string;
  user_detail_count: number;
  satellite_detail_count: number;
  users: readonly RuntimeNodeDetailCardV1[];
  satellites: readonly RuntimeNodeDetailCardV1[];
}

export interface RuntimeNodeDetailCardV1 {
  entity_type: "USER" | "SATELLITE" | string;
  entity_id: string;
  title: string;
  subtitle: string;
  sections?: readonly RuntimeNodeDetailSectionV1[];
  fields: readonly RuntimeNodeDetailFieldV1[];
}

export interface RuntimeNodeDetailSectionV1 {
  section_id: string;
  title: string;
  fields: readonly RuntimeNodeDetailFieldV1[];
}

export interface RuntimeNodeDetailFieldV1 {
  label: string;
  value: string;
  tone?: "normal" | "warning" | "resource" | string;
}

export interface RuntimeSatelliteServiceItemV1 {
  satellite_id: string;
  status: string;
  resource_role?: string;
  resource_role_label?: string;
  service_user_ids: readonly string[];
  service_user_count?: number;
  primary_service_user_id?: string;
  next_hop_ids: readonly string[];
  next_hop_count?: number;
  primary_next_hop_id?: string;
  primary_route_id?: string;
  primary_flow_id?: string;
  route_count: number;
  available_route_count: number;
  network_queue_route_count?: number;
  compute_service_route_count?: number;
  network_service_route_count?: number;
  route_mix_label?: string;
  route_capacity_mbps?: number;
  route_demand_mbps?: number;
  route_latency_avg_s?: number;
  route_delay_variation_proxy_s?: number;
  route_loss_proxy_rate?: number;
  active_link_count: number;
  active_access_link_count: number;
  active_space_link_count: number;
  compute_load_ratio: number;
  compute_capacity_gflops_fp32: number;
  compute_used_gflops_fp32: number;
  compute_capacity_gflops_fp64: number;
  compute_used_gflops_fp64: number;
  compute_capacity_gpu_tflops_fp32: number;
  compute_used_gpu_tflops_fp32: number;
  compute_capacity_gpu_tflops_fp16: number;
  compute_used_gpu_tflops_fp16: number;
  compute_capacity_npu_tops_int8: number;
  compute_used_npu_tops_int8: number;
  compute_capacity_memory_gb: number;
  compute_used_memory_gb: number;
  compute_capacity_storage_gb: number;
  compute_used_storage_gb: number;
  running_task_count: number;
  finished_task_count: number;
}

export interface RuntimeSatelliteKpiSlicesV1 {
  version: "v1" | string;
  mode: string;
  slice_limit?: number;
  satellite_count?: number;
  slice_count?: number;
  slices: readonly RuntimeSatelliteKpiSliceV1[];
}

export interface RuntimeSatelliteKpiSliceV1 {
  satellite_id: string;
  active_link_count: number;
  active_access_link_count: number;
  active_space_link_count: number;
  route_count: number;
  available_route_count: number;
  route_capacity_mbps: number;
  route_demand_mbps: number;
  route_latency_avg_s: number;
  route_delay_variation_proxy_s: number;
  route_loss_proxy_rate: number;
  compute_capacity_gflops_fp32: number;
  compute_used_gflops_fp32: number;
  compute_capacity_gflops_fp64?: number;
  compute_used_gflops_fp64?: number;
  compute_capacity_gpu_tflops_fp32?: number;
  compute_used_gpu_tflops_fp32?: number;
  compute_capacity_gpu_tflops_fp16?: number;
  compute_used_gpu_tflops_fp16?: number;
  compute_capacity_npu_tops_int8?: number;
  compute_used_npu_tops_int8?: number;
  compute_capacity_memory_gb?: number;
  compute_used_memory_gb?: number;
  compute_capacity_storage_gb?: number;
  compute_used_storage_gb?: number;
  compute_load_ratio: number;
  running_task_count: number;
  finished_task_count: number;
}

export interface RuntimeSatelliteKpiHistoryV1 {
  version: "v1" | string;
  mode: string;
  slice_limit?: number;
  sample_limit?: number;
  satellite_count?: number;
  series_count?: number;
  series: readonly RuntimeSatelliteKpiHistorySeriesV1[];
}

export interface RuntimeSatelliteKpiHistorySeriesV1 {
  satellite_id: string;
  sample_count?: number;
  samples: readonly RuntimeSatelliteKpiHistorySampleV1[];
}

export interface RuntimeSatelliteKpiHistorySampleV1 {
  sim_time: number;
  compute_load_ratio: number;
  compute_capacity_gflops_fp32?: number;
  compute_used_gflops_fp32?: number;
  compute_capacity_gflops_fp64?: number;
  compute_used_gflops_fp64?: number;
  compute_capacity_gpu_tflops_fp32?: number;
  compute_used_gpu_tflops_fp32?: number;
  compute_capacity_gpu_tflops_fp16?: number;
  compute_used_gpu_tflops_fp16?: number;
  compute_capacity_npu_tops_int8?: number;
  compute_used_npu_tops_int8?: number;
  compute_capacity_memory_gb?: number;
  compute_used_memory_gb?: number;
  compute_capacity_storage_gb?: number;
  compute_used_storage_gb?: number;
}

export interface RuntimeServiceLatencyHistoryV1 {
  version: "v1" | string;
  mode: string;
  service_count?: number;
  service_limit?: number;
  item_count?: number;
  items: readonly RuntimeServiceLatencyHistoryItemV1[];
}

export interface RuntimeServiceLatencyHistoryItemV1 {
  task_id: string;
  input_flow_id?: string;
  output_flow_id?: string;
  input_route_id?: string;
  output_route_id?: string;
  compute_node_id?: string;
  service_placement_status?: string;
  service_placement_policy?: string;
  service_placement_bottleneck_resource?: string;
  service_placement_candidate_count?: number;
  service_placement_capable_candidate_count?: number;
  first_sample_sim_time?: number;
  last_sample_sim_time?: number;
  component_timeline?: readonly RuntimeServiceLatencyComponentSampleV1[];
  complete: boolean;
  input_network_latency_s: number;
  compute_queue_delay_s: number;
  compute_execution_delay_s: number;
  output_network_latency_s: number;
  total_latency_s: number;
}

export interface RuntimeServiceLatencyComponentSampleV1 {
  component: string;
  metric_name?: string;
  sample_sim_time?: number;
  duration_s: number;
  input_flow_id?: string;
  output_flow_id?: string;
  route_id?: string;
}

export interface RuntimeStreamDiagnosticsV1 {
  version: "v1" | string;
  advance_loop_state: string;
  tick_count: number;
  event_stream: RuntimeStreamBufferDiagnosticsV1;
  state_stream: RuntimeStreamBufferDiagnosticsV1;
}

export interface RuntimeStreamBufferDiagnosticsV1 {
  name: string;
  next_cursor: number;
  oldest_cursor: number;
  retained_count: number;
  total_dropped_count: number;
  max_items: number;
  max_batch_size: number;
  overflow_risk: boolean;
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
