import {
  EVENT_TYPES,
  EventType,
  LinkState,
  MetricRecord,
  Route,
  SatelliteState,
  SimEvent,
  StateSnapshot,
  TaskState
} from "../event_types";

const EVENT_TYPE_SET = new Set<string>(EVENT_TYPES);

export function decodeSimEvent(value: unknown): SimEvent {
  const record = requireRecord(value, "SimEvent");
  const eventType = requireEventType(record.event_type);
  return {
    event_id: requireEventId(record.event_id),
    sim_time: requireFiniteNumber(record.sim_time, "sim_time"),
    priority: requireInteger(record.priority, "priority"),
    source: requireString(record.source, "source"),
    target: requireString(record.target, "target"),
    event_type: eventType,
    payload: decodePayload(eventType, record.payload)
  };
}

export function decodeSimEventBatch(value: unknown): readonly SimEvent[] {
  if (!Array.isArray(value)) {
    return [decodeSimEvent(value)];
  }
  return value.map((item) => decodeSimEvent(item));
}

export function decodeStateSnapshot(value: unknown): StateSnapshot {
  const record = requireRecord(value, "StateSnapshot");
  return {
    satellites: optionalArray(record.satellites, decodeSatelliteState),
    ground_users: optionalArray(record.ground_users, (item) => {
      const user = requireRecord(item, "GroundUserState");
      return {
        user_id: requireString(user.user_id, "user_id"),
        position:
          user.position === undefined ? undefined : requireGeoPosition(user.position),
        cell_id: user.cell_id === undefined ? undefined : requireString(user.cell_id, "cell_id"),
        status: user.status === undefined ? undefined : requireString(user.status, "status")
      };
    }),
    links: optionalArray(record.links, decodeLinkState),
    routes: optionalArray(record.routes, decodeRoute),
    tasks: optionalArray(record.tasks, decodeTaskState),
    metrics: optionalArray(record.metrics, decodeMetricRecord)
  };
}

function decodePayload(eventType: EventType, payload: unknown): unknown {
  if (eventType === "ORBIT_UPDATE") {
    return decodeSatelliteState(payload);
  }
  if (eventType === "LINK_UPDATE" || eventType === "ACCESS_START" || eventType === "ACCESS_END") {
    return decodeLinkState(payload);
  }
  if (eventType === "ROUTE_UPDATE") {
    return decodeRoute(payload);
  }
  if (eventType === "TASK_START" || eventType === "TASK_FINISH") {
    return decodeTaskState(payload);
  }
  return decodeMetricRecord(payload);
}

function decodeSatelliteState(value: unknown): SatelliteState {
  const record = requireRecord(value, "SatelliteState");
  return {
    satellite_id: requireString(record.satellite_id, "satellite_id"),
    sim_time: requireFiniteNumber(record.sim_time, "sim_time"),
    position: requireVector3(record.position, "position"),
    velocity: record.velocity === undefined ? undefined : requireVector3(record.velocity, "velocity"),
    status: requireString(record.status, "status")
  };
}

function decodeLinkState(value: unknown): LinkState {
  const record = requireRecord(value, "LinkState");
  return {
    source_id: requireString(record.source_id, "source_id"),
    target_id: requireString(record.target_id, "target_id"),
    latency: requireFiniteNumber(record.latency, "latency"),
    capacity: requireFiniteNumber(record.capacity, "capacity"),
    availability: requireBoolean(record.availability, "availability"),
    utilization:
      record.utilization === undefined
        ? undefined
        : requireFiniteNumber(record.utilization, "utilization")
  };
}

function decodeRoute(value: unknown): Route {
  const record = requireRecord(value, "Route");
  if (!Array.isArray(record.path) || !record.path.every((item) => typeof item === "string")) {
    throw new TypeError("path must be a string array");
  }
  return {
    route_id: requireString(record.route_id, "route_id"),
    flow_id: requireString(record.flow_id, "flow_id"),
    path: record.path,
    latency: requireFiniteNumber(record.latency, "latency"),
    capacity: requireFiniteNumber(record.capacity, "capacity"),
    available: requireBoolean(record.available, "available")
  };
}

function decodeTaskState(value: unknown): TaskState {
  const record = requireRecord(value, "TaskState");
  return {
    task_id: requireString(record.task_id, "task_id"),
    node_id: requireString(record.node_id, "node_id"),
    sim_time: requireFiniteNumber(record.sim_time, "sim_time"),
    progress: requireFiniteNumber(record.progress, "progress"),
    status: requireString(record.status, "status")
  };
}

function decodeMetricRecord(value: unknown): MetricRecord {
  const record = requireRecord(value, "MetricRecord");
  return {
    metric_name: requireString(record.metric_name, "metric_name"),
    sim_time: requireFiniteNumber(record.sim_time, "sim_time"),
    entity_id: requireString(record.entity_id, "entity_id"),
    value: requireMetricValue(record.value),
    tags: record.tags === undefined ? undefined : requireTags(record.tags)
  };
}

function requireRecord(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError(`${label} must be an object`);
  }
  return value as Record<string, unknown>;
}

function requireEventType(value: unknown): EventType {
  if (typeof value !== "string" || !EVENT_TYPE_SET.has(value)) {
    throw new TypeError("event_type is not supported by the observability layer");
  }
  return value as EventType;
}

function requireEventId(value: unknown): string | number {
  if (typeof value !== "string" && typeof value !== "number") {
    throw new TypeError("event_id must be a string or number");
  }
  return value;
}

function requireString(value: unknown, label: string): string {
  if (typeof value !== "string" || value.length === 0) {
    throw new TypeError(`${label} must be a non-empty string`);
  }
  return value;
}

function requireInteger(value: unknown, label: string): number {
  const numberValue = requireFiniteNumber(value, label);
  if (!Number.isInteger(numberValue)) {
    throw new TypeError(`${label} must be an integer`);
  }
  return numberValue;
}

function requireFiniteNumber(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new TypeError(`${label} must be a finite number`);
  }
  return value;
}

function requireBoolean(value: unknown, label: string): boolean {
  if (typeof value !== "boolean") {
    throw new TypeError(`${label} must be a boolean`);
  }
  return value;
}

function requireMetricValue(value: unknown): string | number | boolean {
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return value;
  }
  throw new TypeError("metric value must be a scalar");
}

function requireVector3(value: unknown, label: string): readonly [number, number, number] {
  if (!Array.isArray(value) || value.length !== 3) {
    throw new TypeError(`${label} must contain exactly three numbers`);
  }
  return [
    requireFiniteNumber(value[0], `${label}[0]`),
    requireFiniteNumber(value[1], `${label}[1]`),
    requireFiniteNumber(value[2], `${label}[2]`)
  ];
}

function requireGeoPosition(value: unknown): readonly [number, number, number?] {
  if (!Array.isArray(value) || value.length < 2 || value.length > 3) {
    throw new TypeError("position must contain longitude, latitude, and optional height");
  }
  const longitude = requireFiniteNumber(value[0], "longitude");
  const latitude = requireFiniteNumber(value[1], "latitude");
  const height = value.length === 3 ? requireFiniteNumber(value[2], "height") : undefined;
  return height === undefined ? [longitude, latitude] : [longitude, latitude, height];
}

function requireTags(value: unknown): readonly [string, string][] {
  if (!Array.isArray(value)) {
    throw new TypeError("tags must be an array");
  }
  return value.map((item) => {
    if (!Array.isArray(item) || item.length !== 2) {
      throw new TypeError("each metric tag must be a pair");
    }
    return [requireString(item[0], "tag key"), requireString(item[1], "tag value")];
  });
}

function optionalArray<T>(value: unknown, decoder: (item: unknown) => T): readonly T[] | undefined {
  if (value === undefined) {
    return undefined;
  }
  if (!Array.isArray(value)) {
    throw new TypeError("snapshot fields must be arrays");
  }
  return value.map(decoder);
}
