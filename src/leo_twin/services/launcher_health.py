"""Launcher health summary contract for local operator diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


LAUNCHER_HEALTH_V2_ID = "leo_twin.launcher_health.v2"
LAUNCHER_ONE_CLICK_ACCEPTANCE_V1_ID = (
    "leo_twin.launcher_one_click_acceptance.v1"
)


@dataclass(frozen=True)
class LauncherServiceProbe:
    """Observed health for one launcher-managed local service."""

    service: str
    role: str
    port: int
    url: str
    health_url: str
    listening: bool
    http_healthy: bool
    process_ids: tuple[int, ...] = ()
    process_names: tuple[str, ...] = ()
    stdout_log: str = ""
    stderr_log: str = ""

    def __post_init__(self) -> None:
        _require_non_empty_string(self.service, "service")
        _require_non_empty_string(self.role, "role")
        _require_positive_int(self.port, "port")
        _require_non_empty_string(self.url, "url")
        _require_non_empty_string(self.health_url, "health_url")
        if not isinstance(self.listening, bool):
            raise TypeError("listening must be a bool")
        if not isinstance(self.http_healthy, bool):
            raise TypeError("http_healthy must be a bool")
        object.__setattr__(
            self,
            "process_ids",
            tuple(_normalize_process_id(value) for value in self.process_ids),
        )
        object.__setattr__(
            self,
            "process_names",
            tuple(str(value) for value in self.process_names),
        )

    @property
    def readiness(self) -> str:
        if self.listening and self.http_healthy:
            return "READY"
        if self.listening:
            return "PORT_ONLY"
        return "STOPPED"

    def to_dict(self) -> dict[str, object]:
        return {
            "service": self.service,
            "role": self.role,
            "port": self.port,
            "url": self.url,
            "health_url": self.health_url,
            "listening": self.listening,
            "http_healthy": self.http_healthy,
            "readiness": self.readiness,
            "process_ids": self.process_ids,
            "process_names": self.process_names,
            "process_count": len(self.process_ids),
            "stdout_log": self.stdout_log,
            "stderr_log": self.stderr_log,
        }


def build_launcher_health_summary_v2(
    *,
    repo_root: str | Path,
    backend: LauncherServiceProbe,
    frontend: LauncherServiceProbe,
    launcher_log_dir: str | Path,
    config_path: str | Path,
    control_config_path: str | Path,
    generated_config_path: str | Path,
) -> dict[str, object]:
    """Return deterministic launcher health summary data."""

    if not isinstance(backend, LauncherServiceProbe):
        raise TypeError("backend must be LauncherServiceProbe")
    if not isinstance(frontend, LauncherServiceProbe):
        raise TypeError("frontend must be LauncherServiceProbe")
    services = (backend.to_dict(), frontend.to_dict())
    ready_count = sum(1 for service in services if service["readiness"] == "READY")
    stopped_count = sum(1 for service in services if service["readiness"] == "STOPPED")
    overall_status = _overall_status(ready_count, stopped_count, len(services))
    one_click_acceptance = _one_click_acceptance(
        overall_status=overall_status,
        ready_count=ready_count,
        services=services,
    )
    return {
        "type": "LAUNCHER_HEALTH",
        "health_id": LAUNCHER_HEALTH_V2_ID,
        "version": "v2",
        "overall_status": overall_status,
        "ready_service_count": ready_count,
        "service_count": len(services),
        "services": services,
        "paths": {
            "repo_root": str(Path(repo_root)),
            "launcher_log_dir": str(Path(launcher_log_dir)),
            "config_path": str(Path(config_path)),
            "control_config_path": str(Path(control_config_path)),
            "generated_config_path": str(Path(generated_config_path)),
        },
        "one_click_acceptance_v1": one_click_acceptance,
        "recommended_actions": _recommended_actions(overall_status, services),
        "diagnostic_commands": (
            "scripts\\sees_launcher.ps1 status",
            "scripts\\sees_launcher.ps1 status -JsonSummary",
            "scripts\\smoke_runtime_health.ps1",
            "scripts\\sees_launcher.ps1 restart",
        ),
        "constraints": {
            "event_kernel_frozen": True,
            "packet_level_simulation": False,
            "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        },
    }


def _overall_status(ready_count: int, stopped_count: int, service_count: int) -> str:
    if ready_count == service_count:
        return "HEALTHY"
    if stopped_count == service_count:
        return "STOPPED"
    return "DEGRADED"


def _recommended_actions(
    overall_status: str,
    services: tuple[dict[str, object], ...],
) -> tuple[str, ...]:
    if overall_status == "HEALTHY":
        return ("Open frontend URL or run smoke_runtime_health.ps1.",)
    if overall_status == "STOPPED":
        return ("Run scripts\\sees_launcher.ps1 start.",)
    actions: list[str] = [
        "Inspect artifacts\\launcher logs for unhealthy services.",
        "Run scripts\\sees_launcher.ps1 restart if stale processes own the ports.",
    ]
    for service in services:
        if service["readiness"] == "PORT_ONLY":
            actions.append(f"{service['service']} port is open but HTTP health failed.")
        elif service["readiness"] == "STOPPED":
            actions.append(f"{service['service']} is not listening on its configured port.")
    return tuple(actions)


def _one_click_acceptance(
    *,
    overall_status: str,
    ready_count: int,
    services: tuple[dict[str, object], ...],
) -> dict[str, object]:
    blocked_services = tuple(
        str(service["service"])
        for service in services
        if service["readiness"] != "READY"
    )
    if not blocked_services:
        status = "PASS"
        next_action = "Open the console or dashboard and run the smoke check."
    elif overall_status == "STOPPED":
        status = "STOPPED"
        next_action = "Run scripts\\sees_launcher.ps1 start."
    else:
        status = "BLOCKED"
        next_action = "Inspect launcher logs and restart unhealthy services."
    return {
        "acceptance_id": LAUNCHER_ONE_CLICK_ACCEPTANCE_V1_ID,
        "status": status,
        "ready": status == "PASS",
        "required_service_count": len(services),
        "ready_service_count": ready_count,
        "blocked_service_count": len(blocked_services),
        "blocking_services": blocked_services,
        "smoke_command": "scripts\\smoke_runtime_health.ps1",
        "next_action": next_action,
        "criteria": (
            "backend HTTP health READY",
            "frontend HTTP health READY",
            "launcher logs captured",
            "read-only smoke command available",
        ),
    }


def _normalize_process_id(value: object) -> int:
    _require_positive_int(value, "process_id")
    return int(value)


def _require_non_empty_string(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty string")


def _require_positive_int(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")
