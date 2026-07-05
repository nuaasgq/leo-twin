# Version Info Endpoint v1

Date: 2026-07-06
Branch: `feature/T221-version-build-info-endpoint-v1`

The integration demo backend exposes version and build diagnostics through:

```text
GET /runtime/version
GET /version
```

Both routes return the same backend-owned payload:

```text
leo_twin.version_info.v1
```

## Payload Sections

- project name, backend version, and description from `pyproject.toml`;
- frontend package name and version from `frontend/package.json`;
- git commit, short commit, branch, and dirty flag;
- Python runtime and platform summary;
- diagnostic endpoint list;
- hard product constraints.

## Constraints Reported

The payload explicitly reports:

- Event Kernel frozen: `true`;
- packet-level simulation: `false`;
- forbidden integrations: `STK`, `EXATA`, `AFSIM`, `DDS`.

## Usage

```powershell
Invoke-RestMethod http://127.0.0.1:8765/runtime/version
```

This endpoint is read-only and does not mutate runtime state.
