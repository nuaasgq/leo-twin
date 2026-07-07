# Data Dashboard Information Architecture v3

## Purpose

Dashboard information architecture v3 defines the backend-owned product
structure for the standalone data dashboard. Its goal is to stop the frontend
from inventing business or model semantics locally and to give future UI work a
stable ordering for overview, network, business, compute, node detail, model
assumptions, and diagnostics.

The contract is exposed through:

- `backend_summary.dashboard_information_architecture_v3`
- source id: `leo_twin.dashboard_information_architecture.v3`
- source owner: `BACKEND_DERIVED_SUMMARY`

## Sections

The deterministic section order is:

1. `OVERVIEW` - simulation time, run state, scale, event volume, fidelity mode,
   export status, and high-level health.
2. `NETWORK` - throughput, latency, jitter, loss, route explanation, link
   protocol state, KPI credibility, and provenance.
3. `BUSINESS` - user business requests, service classes, lifecycle stage,
   target satellite, and service latency components.
4. `COMPUTE` - satellite-hosted resource vectors, task queue state, bottleneck
   lanes, and task timelines.
5. `NODE_DETAIL` - paged or virtualized drill-down for user and satellite
   nodes, including detail coverage status for backend detail families, cursor
   windows, hidden rows, selected exact-detail evidence, service-trace
   closed-loop correlation evidence, exact node cards, and active pagination
   contract.
6. `MODEL_ASSUMPTIONS` - backend model boundaries, fidelity degradation,
   forbidden integrations, and KPI caveats.
7. `DIAGNOSTICS` - reproducibility manifest, result packages, launcher health,
   warnings, and operator diagnostics.

## Frontend Rules

- The backend is the source of truth for section semantics.
- The frontend may sort by backend priority, paginate, virtualize, and format
  values.
- The frontend must not invent business, network, compute, fidelity, or model
  assumption semantics when the backend provides them.
- Large-scale scenarios must use bounded windows, pagination, or virtualization
  before rendering detail rows.
- The dashboard page remains scrollable; individual sections should be
  scan-friendly and avoid nested cards.

## Follow-Up Tasks

- V2-051: user detail drawer.
- V2-052: satellite detail drawer.
- V2-053: virtualized large tables.
- V2-054: model assumptions panel.
- T364: dashboard detail coverage card.
- T365: selected detail evidence card.
- T366: service trace closed-loop correlation evidence card.
