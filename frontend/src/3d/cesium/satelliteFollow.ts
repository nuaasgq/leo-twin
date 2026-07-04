import { ComputeResourceSummary, SatelliteState } from "../../core/event_types";

const EARTH_RADIUS_M = 6_371_000;

export type GlobeCameraMode = "EARTH" | "SATELLITE";

export interface SatelliteInsetPoint {
  satelliteId: string;
  simTime: number;
  x: number;
  y: number;
}

export interface SatelliteResourceBreakdownItem {
  label: string;
  capacityLabel: string;
  usedLabel: string;
  utilizationPercent: number;
}

export interface SatelliteComputeSummary {
  resourceModelLabel: string;
  resourceRoleLabel: string;
  capacityLabel: string;
  availableLabel: string;
  utilizationLabel: string;
  utilizationPercent: number;
  availablePercent: number;
  statusLabel: string;
  cpuVectorLabel: string;
  gpuVectorLabel: string;
  npuVectorLabel: string;
  memoryStorageLabel: string;
  resourceBreakdown: readonly SatelliteResourceBreakdownItem[];
  processingUsageLabel: string;
  memoryUsageLabel: string;
  compatibilityNote: string;
}

export function selectedDisplaySatellite(
  satellites: readonly SatelliteState[],
  selectedSatelliteId: string
): SatelliteState | null {
  if (satellites.length === 0) {
    return null;
  }
  return (
    satellites.find((satellite) => satellite.satellite_id === selectedSatelliteId) ??
    satellites[0]
  );
}

export function appendSatelliteInsetTrail(
  currentTrail: readonly SatelliteInsetPoint[],
  satellite: SatelliteState | null,
  maxPoints = 28
): readonly SatelliteInsetPoint[] {
  if (!satellite) {
    return [];
  }
  const nextPoint = satelliteInsetPoint(satellite);
  const previousPoint = currentTrail[currentTrail.length - 1];
  const retainedTrail =
    previousPoint?.satelliteId === satellite.satellite_id ? currentTrail : [];
  if (
    previousPoint?.satelliteId === satellite.satellite_id &&
    previousPoint.simTime === nextPoint.simTime &&
    previousPoint.x === nextPoint.x &&
    previousPoint.y === nextPoint.y
  ) {
    return currentTrail;
  }
  return [...retainedTrail, nextPoint].slice(-Math.max(2, maxPoints));
}

export function satelliteInsetPoint(satellite: SatelliteState): SatelliteInsetPoint {
  const [x, y, z] = satellite.position;
  const radius = Math.hypot(x, y, z);
  if (!Number.isFinite(radius) || radius <= 0) {
    return {
      satelliteId: satellite.satellite_id,
      simTime: satellite.sim_time,
      x: 50,
      y: 50
    };
  }
  const velocityMagnitude = satellite.velocity
    ? Math.hypot(satellite.velocity[0], satellite.velocity[1], satellite.velocity[2])
    : 0;
  const phaseDrift =
    Number.isFinite(velocityMagnitude) && velocityMagnitude > 0
      ? satellite.sim_time * (velocityMagnitude / radius)
      : 0;
  const phase = Math.atan2(y, x) + phaseDrift;
  const inclinationOffset = clamp(z / radius, -1, 1) * 8;
  return {
    satelliteId: satellite.satellite_id,
    simTime: satellite.sim_time,
    x: clamp(50 + Math.cos(phase) * 34, 8, 92),
    y: clamp(50 + Math.sin(phase) * 24 - inclinationOffset, 8, 92)
  };
}

export function satelliteAltitudeKm(satellite: SatelliteState): number {
  const radius = Math.hypot(
    satellite.position[0],
    satellite.position[1],
    satellite.position[2]
  );
  if (!Number.isFinite(radius)) {
    return 0;
  }
  return Math.max(0, (radius - EARTH_RADIUS_M) / 1000);
}

export function satelliteComputeSummary(
  node:
    | {
        capacity: number;
        available_capacity: number;
        load_ratio?: number;
        status: string;
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
    | null
    | undefined,
  resourceSummary?: ComputeResourceSummary | null
): SatelliteComputeSummary | null {
  if (!node) {
    return null;
  }
  const capacity = Math.max(0, finiteNumber(node.capacity));
  const available = Math.max(0, Math.min(capacity, finiteNumber(node.available_capacity)));
  const hasLiveResourceVector = hasNodeResourceVector(node);
  const cpuFp32 = capacity;
  const cpuFp64 = finiteOptionalNumber(
    node.cpu_gflops_fp64,
    finiteOptionalNumber(resourceSummary?.cpu_gflops_fp64_per_node, 0)
  );
  const gpuFp32 = finiteOptionalNumber(
    node.gpu_tflops_fp32,
    finiteOptionalNumber(resourceSummary?.gpu_tflops_fp32_per_node, 0)
  );
  const gpuFp16 = finiteOptionalNumber(
    node.gpu_tflops_fp16,
    finiteOptionalNumber(resourceSummary?.gpu_tflops_fp16_per_node, 0)
  );
  const npuInt8 = finiteOptionalNumber(
    node.npu_tops_int8,
    finiteOptionalNumber(resourceSummary?.npu_tops_int8_per_node, 0)
  );
  const memoryGb = finiteOptionalNumber(
    node.memory_gb,
    finiteOptionalNumber(resourceSummary?.memory_gb_per_node, 0)
  );
  const storageGb = finiteOptionalNumber(
    node.storage_gb,
    finiteOptionalNumber(resourceSummary?.storage_gb_per_node, 0)
  );
  const usedCpuFp32 = finiteOptionalNumber(node.used_cpu_gflops_fp32, 0);
  const usedCpuFp64 = finiteOptionalNumber(node.used_cpu_gflops_fp64, 0);
  const usedGpuFp32 = finiteOptionalNumber(node.used_gpu_tflops_fp32, 0);
  const usedGpuFp16 = finiteOptionalNumber(node.used_gpu_tflops_fp16, 0);
  const usedNpuInt8 = finiteOptionalNumber(node.used_npu_tops_int8, 0);
  const usedMemoryGb = finiteOptionalNumber(node.used_memory_gb, 0);
  const usedStorageGb = finiteOptionalNumber(node.used_storage_gb, 0);
  const resourceBreakdown = [
    resourceBreakdownItem(
      "CPU FP32",
      cpuFp32,
      usedOrAvailableUsed(node.used_cpu_gflops_fp32, node.available_cpu_gflops_fp32, cpuFp32),
      "GFLOPS"
    ),
    resourceBreakdownItem(
      "CPU FP64",
      cpuFp64,
      usedOrAvailableUsed(node.used_cpu_gflops_fp64, node.available_cpu_gflops_fp64, cpuFp64),
      "GFLOPS"
    ),
    resourceBreakdownItem(
      "GPU FP32",
      gpuFp32,
      usedOrAvailableUsed(node.used_gpu_tflops_fp32, node.available_gpu_tflops_fp32, gpuFp32),
      "TFLOPS"
    ),
    resourceBreakdownItem(
      "GPU FP16",
      gpuFp16,
      usedOrAvailableUsed(node.used_gpu_tflops_fp16, node.available_gpu_tflops_fp16, gpuFp16),
      "TFLOPS"
    ),
    resourceBreakdownItem(
      "NPU INT8",
      npuInt8,
      usedOrAvailableUsed(node.used_npu_tops_int8, node.available_npu_tops_int8, npuInt8),
      "TOPS"
    ),
    resourceBreakdownItem(
      "内存",
      memoryGb,
      usedOrAvailableUsed(node.used_memory_gb, node.available_memory_gb, memoryGb),
      "GB"
    ),
    resourceBreakdownItem(
      "存储",
      storageGb,
      usedOrAvailableUsed(node.used_storage_gb, node.available_storage_gb, storageGb),
      "GB"
    )
  ];
  const utilization =
    node.load_ratio !== undefined
      ? clamp(finiteNumber(node.load_ratio), 0, 1)
      : capacity <= 0
        ? 0
        : clamp((capacity - available) / capacity, 0, 1);
  return {
    resourceModelLabel:
      resourceSummary?.resource_model ??
      (hasLiveResourceVector ? "ComputeResourceVector" : "LegacyScalarCapacity"),
    resourceRoleLabel: formatNodeRole(resourceSummary?.node_role),
    capacityLabel: `${formatNumber(capacity)} GFLOPS FP32`,
    availableLabel: `${formatNumber(available)} GFLOPS`,
    utilizationLabel: `${formatNumber(utilization * 100)}%`,
    utilizationPercent: utilization * 100,
    availablePercent: capacity <= 0 ? 0 : (available / capacity) * 100,
    statusLabel: node.status,
    cpuVectorLabel: `CPU FP32 ${formatNumber(cpuFp32)} GFLOPS / FP64 ${formatNumber(
      cpuFp64
    )} GFLOPS`,
    gpuVectorLabel: `GPU FP32 ${formatNumber(gpuFp32)} TFLOPS / FP16 ${formatNumber(
      gpuFp16
    )} TFLOPS`,
    npuVectorLabel: `NPU INT8 ${formatNumber(npuInt8)} TOPS`,
    memoryStorageLabel: `内存 ${formatNumber(memoryGb)} GB / 存储 ${formatNumber(
      storageGb
    )} GB`,
    resourceBreakdown,
    processingUsageLabel: `使用 CPU FP32 ${formatNumber(
      usedCpuFp32
    )} GFLOPS / FP64 ${formatNumber(usedCpuFp64)} GFLOPS / GPU FP32 ${formatNumber(
      usedGpuFp32
    )} TFLOPS / FP16 ${formatNumber(usedGpuFp16)} TFLOPS / NPU ${formatNumber(
      usedNpuInt8
    )} TOPS`,
    memoryUsageLabel: `使用 内存 ${formatNumber(usedMemoryGb)} GB / 存储 ${formatNumber(
      usedStorageGb
    )} GB`,
    compatibilityNote:
      resourceSummary?.compatibility_note ?? "实时节点状态仍使用标量 capacity。"
  };
}

function hasNodeResourceVector(node: {
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
}): boolean {
  return (
    node.cpu_gflops_fp64 !== undefined ||
    node.gpu_tflops_fp32 !== undefined ||
    node.gpu_tflops_fp16 !== undefined ||
    node.npu_tops_int8 !== undefined ||
    node.memory_gb !== undefined ||
    node.storage_gb !== undefined ||
    node.resource_usage_mode !== undefined ||
    node.available_cpu_gflops_fp32 !== undefined ||
    node.used_cpu_gflops_fp32 !== undefined ||
    node.available_cpu_gflops_fp64 !== undefined ||
    node.used_cpu_gflops_fp64 !== undefined ||
    node.available_gpu_tflops_fp32 !== undefined ||
    node.used_gpu_tflops_fp32 !== undefined ||
    node.available_gpu_tflops_fp16 !== undefined ||
    node.used_gpu_tflops_fp16 !== undefined ||
    node.available_npu_tops_int8 !== undefined ||
    node.used_npu_tops_int8 !== undefined ||
    node.available_memory_gb !== undefined ||
    node.used_memory_gb !== undefined ||
    node.available_storage_gb !== undefined ||
    node.used_storage_gb !== undefined
  );
}

function usedOrAvailableUsed(
  usedValue: number | undefined,
  availableValue: number | undefined,
  capacity: number
): number {
  if (usedValue !== undefined) {
    return finiteOptionalNumber(usedValue, 0);
  }
  if (availableValue !== undefined) {
    return Math.max(0, capacity - finiteOptionalNumber(availableValue, 0));
  }
  return 0;
}

function resourceBreakdownItem(
  label: string,
  capacity: number,
  used: number,
  unit: string
): SatelliteResourceBreakdownItem {
  const safeCapacity = Math.max(0, finiteNumber(capacity));
  const safeUsed = clamp(finiteNumber(used), 0, safeCapacity);
  return {
    label,
    capacityLabel: `${formatNumber(safeCapacity)} ${unit}`,
    usedLabel: `${formatNumber(safeUsed)} ${unit}`,
    utilizationPercent: safeCapacity <= 0 ? 0 : (safeUsed / safeCapacity) * 100
  };
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function finiteNumber(value: number): number {
  return Number.isFinite(value) ? value : 0;
}

function finiteOptionalNumber(value: number | undefined, fallback: number): number {
  return value !== undefined && Number.isFinite(value) ? value : fallback;
}

function formatNumber(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  });
}

function formatNodeRole(value: string | undefined): string {
  if (value === "SATELLITE_HOSTED_COMPUTE") {
    return "卫星载荷算力节点";
  }
  return value ?? "卫星算力节点";
}
