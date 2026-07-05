import { RuntimeMode, RuntimeStatusPayload } from "./core/event_types";

export function runtimeEffectiveSpeedFactor(
  mode: RuntimeMode | undefined,
  speedFactor: number | undefined
): number {
  if (mode !== "ACCELERATED") {
    return 1;
  }
  return speedFactor !== undefined && Number.isFinite(speedFactor) && speedFactor > 0
    ? speedFactor
    : 1;
}

export function runtimeStatusEffectiveSpeedFactor(runtime: RuntimeStatusPayload): number {
  return runtimeEffectiveSpeedFactor(runtime.mode, runtime.speed_factor);
}

export function runtimeSpeedFactorLabel(runtime: RuntimeStatusPayload): string {
  return `${formatSpeedFactor(runtimeStatusEffectiveSpeedFactor(runtime))}x`;
}

function formatSpeedFactor(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0
  });
}
