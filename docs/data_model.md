# Data Model

This document defines data entities only. It does not define behavior, algorithms, validation rules, event processing, orbital mechanics, network routing, compute scheduling, or simulation logic.

All fields listed below are conceptual placeholders for future schema work. Actual implementation must be introduced only by a scoped future issue and test-driven development.

## SatelliteState

Represents the state of a satellite at a simulation time.

- `satellite_id`: Stable satellite identifier.
- `time`: Simulation timestamp.
- `position`: Placeholder position representation.
- `velocity`: Placeholder velocity representation.
- `status`: Operational state label.

## GroundUserState

Represents the state of a ground user or terminal.

- `user_id`: Stable user identifier.
- `time`: Simulation timestamp.
- `location`: Placeholder location representation.
- `demand_profile`: Reference to configuration-defined demand information.
- `status`: User state label.

## BeamState

Represents the state of a satellite beam.

- `beam_id`: Stable beam identifier.
- `satellite_id`: Owning satellite identifier.
- `time`: Simulation timestamp.
- `coverage_area`: Placeholder coverage representation.
- `capacity`: Configuration-defined capacity placeholder.
- `status`: Beam state label.

## LinkState

Represents the state of a logical communication link.

- `link_id`: Stable link identifier.
- `time`: Simulation timestamp.
- `source_id`: Source node identifier.
- `target_id`: Target node identifier.
- `link_type`: Link category label.
- `capacity`: Configuration-defined capacity placeholder.
- `status`: Link state label.

## FlowRequest

Represents a requested communication flow.

- `flow_id`: Stable flow identifier.
- `source_id`: Source endpoint identifier.
- `target_id`: Target endpoint identifier.
- `start_time`: Requested start timestamp.
- `duration`: Requested duration placeholder.
- `demand`: Configuration-defined demand placeholder.

## FlowState

Represents the state of a communication flow.

- `flow_id`: Stable flow identifier.
- `time`: Simulation timestamp.
- `assigned_path`: Placeholder path representation.
- `allocated_capacity`: Placeholder allocated capacity.
- `status`: Flow state label.

## ComputeNodeState

Represents the state of a compute-capable node.

- `node_id`: Stable compute node identifier.
- `time`: Simulation timestamp.
- `node_type`: Node category label.
- `compute_capacity`: Configuration-defined compute capacity placeholder.
- `available_capacity`: Placeholder available capacity.
- `status`: Compute node state label.

## TaskRequest

Represents a requested compute task.

- `task_id`: Stable task identifier.
- `source_id`: Originating endpoint identifier.
- `submit_time`: Requested submission timestamp.
- `compute_demand`: Configuration-defined compute demand placeholder.
- `data_size`: Configuration-defined data size placeholder.
- `deadline`: Optional deadline placeholder.

## TaskState

Represents the state of a compute task.

- `task_id`: Stable task identifier.
- `time`: Simulation timestamp.
- `assigned_node_id`: Assigned compute node identifier placeholder.
- `progress`: Placeholder progress value.
- `status`: Task state label.

## SimEvent

Represents a discrete simulation event.

- `event_id`: Stable event identifier.
- `time`: Scheduled simulation timestamp.
- `event_type`: Event category label.
- `payload_ref`: Reference to configuration or state payload.
- `priority`: Deterministic ordering placeholder.

## MetricRecord

Represents one recorded metric sample.

- `metric_id`: Stable metric identifier.
- `time`: Simulation timestamp.
- `metric_name`: Metric name.
- `entity_id`: Related entity identifier.
- `value`: Recorded value placeholder.
- `tags`: Configuration-defined labels.
