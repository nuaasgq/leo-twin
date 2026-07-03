# LEO-Twin Codex Skill (Phased Controlled Execution)

## 1. System Mission

This repository implements a Low Earth Orbit (LEO) satellite internet digital twin and communication-computing network simulation framework.

The system is based on a deterministic discrete-event simulation (DES) kernel.

Current phase: FULL-SYSTEM PLANNING, after MVP-0 foundation.

MVP-0 remains a historical baseline. MVP-0 restrictions apply only when a task
explicitly declares `Current phase: MVP-0`.

Full-system tasks must still preserve the frozen deterministic event kernel and
must introduce higher-fidelity behavior only through documented contracts,
configuration, tests, and event-driven module boundaries.

MVP-0 goal:
- Build a correct, deterministic, modular simulation foundation
- NOT build a full-fidelity simulator
- NOT integrate external tools

---

## 2. Core Principle (DES Model)

The system follows a discrete-event formulation:

S(t+1) = δ(S(t), E)

Where:
- S = system state
- E = event
- δ = deterministic transition function

All system behavior MUST be event-driven.

---

## 3. HARD CONSTRAINTS (ABSOLUTE)

The following are strictly forbidden:

### External systems
- STK
- EXATA / GloMoSim
- AFSIM
- DDS runtime

### Simulation fidelity violations
- packet-level simulation (MVP-0 forbidden)
- RF propagation modeling
- antenna pattern modeling
- high-fidelity orbital mechanics (SGP4, etc.)

### System design violations
- multithreading or distributed execution
- global mutable state in core logic
- circular module dependencies
- cross-layer logic leakage

### Engineering violations
- implementing multiple issues in one task
- modifying unrelated modules
- adding undocumented abstractions
- premature optimization

---

## 4. Architecture Rules

Strict layered architecture:

core        -> simulation kernel (ONLY event + time control)
schema      -> data definitions (pure, serializable)
models      -> simplified domain models
services    -> metrics / scenario / replay
adapters    -> mock only (MVP-0)
examples    -> runnable demos

### Dependency rules:

core → schema only
models → core + schema
services → models + schema
adapters → must NOT affect core
examples → read-only dependency allowed

---

## 5. Simulation Kernel Rules (CRITICAL)

The SimulationKernel is the ONLY authority for simulation time.

It MUST:
- control simulation time
- manage event queue
- dispatch events deterministically
- guarantee reproducibility

It MUST NOT:
- contain domain logic (orbit/network/compute)
- depend on external simulators
- directly modify domain states

---

## 6. Event System Rules

All behavior is event-driven.

### Event ordering MUST follow:

1. sim_time (ascending)
2. priority (descending)
3. event_id (deterministic tie-break)

### Minimum event set:

- ORBIT_UPDATE
- COVERAGE_UPDATE
- ACCESS_START / ACCESS_END
- LINK_UPDATE
- ROUTE_UPDATE
- FLOW_ARRIVAL / FLOW_COMPLETE
- TASK_ARRIVAL / TASK_START / TASK_FINISH
- METRIC_SAMPLE

---

## 7. Determinism Rules (CRITICAL)

All outputs MUST be deterministic.

Given:
- identical configuration
- identical random seed

Outputs MUST be identical:
- event sequence
- system states
- metrics

FORBIDDEN:
- non-seeded randomness
- unordered iteration over sets/dicts
- real-time dependencies

---

## 8. Configuration Rules

All scenarios MUST be configuration-driven (YAML).

No hardcoded parameters allowed.

Config includes:
- satellite count
- orbit parameters (simplified)
- user count
- traffic model
- compute nodes
- routing policy
- scheduling policy
- simulation duration
- random seed

---

## 9. MVP-0 Model Fidelity Rules

All models MUST be simplified:

### Orbit model
- circular or periodic motion only
- no SGP4

### Coverage model
- geometric distance + angle threshold
- no RF propagation

### Network model
- flow-level abstraction (NOT packet-level)
- delay/capacity/loss abstraction

### Routing model
- shortest path
- min delay
- max capacity

### Compute model
- queue + service time abstraction
- no real execution

---

## 10. Testing Rules (STRICT)

Every feature MUST include tests.

### Required test types:

1. Unit tests
2. Determinism tests (CRITICAL)
3. Integration tests
4. Scale tests (lightweight)

### Mandatory deterministic test:
Same seed → identical output

### Forbidden in tests:
- time-based assertions
- uncontrolled randomness
- external dependencies

---

## 11. Git Workflow Rules (MANDATORY)

Each task MUST follow:

1. Create feature branch:
   feature/<issue-id>-<name>

2. One issue = one branch = one commit scope

3. No cross-module modifications

4. No refactoring outside scope

5. Must include:
   - tests
   - minimal runnable example (if required)

---

## 12. Multi-Agent Execution Model (CRITICAL)

Codex MUST behave as a multi-agent system.

### Agent A: Kernel Agent
- event queue
- simulation time
- scheduling

FORBIDDEN:
- domain logic

---

### Agent B: Orbit Agent
- satellite motion
- simplified orbit model

FORBIDDEN:
- routing / compute logic

---

### Agent C: Network Agent
- link state
- coverage
- routing

FORBIDDEN:
- orbit logic
- compute logic

---

### Agent D: Compute Agent
- task scheduling
- compute simulation

FORBIDDEN:
- network / orbit logic

---

### Agent E: Metrics Agent
- KPI calculation
- logging
- output generation

FORBIDDEN:
- modifying simulation state

---

## 13. Parallel Development Rule

Independent modules SHOULD be developed in parallel:

- Orbit module (independent)
- Compute module (independent)
- Metrics module (independent)

ONLY Kernel is sequential dependency.

---

## 14. Output Requirements

All simulation runs MUST output:

- events.jsonl
- metrics.csv
- summary.json

No binary or opaque outputs allowed.

---

## 15. Definition of Done

A task is complete ONLY if:

- implementation is within scope
- tests are added
- tests pass
- deterministic behavior verified
- no architecture violations
- no external dependencies introduced
- example runs successfully (if applicable)

---

## 16. If Requirements Are Unclear

- choose simplest correct implementation
- do NOT expand architecture
- document assumptions explicitly
- proceed without blocking

---

## 17. Final Principle

This system prioritizes:

1. determinism
2. modularity
3. reproducibility
4. event-driven correctness

over:

- realism
- performance
- feature richness

---

## 18. Full-System Phase Rules

The full-system phase is allowed to evolve LEO-Twin toward a detailed Chinese
industrial digital twin product, provided the evolution is controlled and
test-driven.

### Allowed full-system work

- detailed orbit model contracts and later implementations
- layered network architecture: application, transport, network, data link,
  physical, and channel layers
- transport protocol profiles such as TCP and UDP
- routing protocol profiles and deterministic routing implementations
- space-ground and space-space channel abstractions
- antenna configuration contracts and later deterministic antenna calculations
- compute resource, task scheduling, and network-compute coupling models
- split frontend surfaces:
  - 3D simulation/control surface
  - separate data dashboard surface
- Chinese product UI text

### Still forbidden in full-system work

- modifying the Event Kernel for domain behavior
- direct module-to-module calls between Orbit, Network, Compute, and Metrics
- hidden global mutable state
- uncontrolled randomness
- undocumented external simulator dependency
- distributed execution unless a later explicit architecture task approves it
- mixing unrelated modules in one implementation task

### Full-system communication rule

Orbit, Network, Compute, Metrics, and Frontend surfaces must communicate through:

- `SimEvent`
- `SimulationKernel.schedule_event()`
- documented control-plane or observation-plane messages

Direct imports across domain module implementations remain forbidden.

### Full-system quality gate

Every full-system task must include:

- deterministic tests
- contract or interface documentation when changing boundaries
- scale-risk review for any topology, channel, routing, or scheduling logic
- Chinese UI text for frontend user-facing changes
