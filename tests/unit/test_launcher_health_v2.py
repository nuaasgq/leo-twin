from __future__ import annotations

import json

from leo_twin.services.launcher_health import (
    LAUNCHER_HEALTH_V2_ID,
    LauncherServiceProbe,
    build_launcher_health_summary_v2,
)


def test_launcher_health_summary_reports_healthy_services() -> None:
    summary = build_launcher_health_summary_v2(
        repo_root="D:/code/leo_twin",
        backend=LauncherServiceProbe(
            service="backend",
            role="SEES demo backend",
            port=8765,
            url="http://127.0.0.1:8765",
            health_url="http://127.0.0.1:8765/runtime/status",
            listening=True,
            http_healthy=True,
            process_ids=(101,),
            process_names=("python",),
            stdout_log="artifacts/launcher/backend.out.log",
            stderr_log="artifacts/launcher/backend.err.log",
        ),
        frontend=LauncherServiceProbe(
            service="frontend",
            role="React observability frontend",
            port=5173,
            url="http://127.0.0.1:5173",
            health_url="http://127.0.0.1:5173/",
            listening=True,
            http_healthy=True,
            process_ids=(202,),
            process_names=("node",),
            stdout_log="artifacts/launcher/frontend.out.log",
            stderr_log="artifacts/launcher/frontend.err.log",
        ),
        launcher_log_dir="artifacts/launcher",
        config_path="configs/integration_demo.yaml",
        control_config_path="configs/sees_control.yaml",
        generated_config_path="configs/generated_full_system_demo.json",
    )

    assert summary["type"] == "LAUNCHER_HEALTH"
    assert summary["health_id"] == LAUNCHER_HEALTH_V2_ID
    assert summary["overall_status"] == "HEALTHY"
    assert summary["ready_service_count"] == 2
    assert [service["readiness"] for service in summary["services"]] == [
        "READY",
        "READY",
    ]
    assert summary["recommended_actions"] == (
        "Open frontend URL or run smoke_runtime_health.ps1.",
    )
    assert json.loads(json.dumps(summary, sort_keys=True))["health_id"] == (
        LAUNCHER_HEALTH_V2_ID
    )


def test_launcher_health_summary_reports_degraded_port_only_service() -> None:
    summary = build_launcher_health_summary_v2(
        repo_root="D:/code/leo_twin",
        backend=LauncherServiceProbe(
            service="backend",
            role="SEES demo backend",
            port=8765,
            url="http://127.0.0.1:8765",
            health_url="http://127.0.0.1:8765/runtime/status",
            listening=True,
            http_healthy=False,
        ),
        frontend=LauncherServiceProbe(
            service="frontend",
            role="React observability frontend",
            port=5173,
            url="http://127.0.0.1:5173",
            health_url="http://127.0.0.1:5173/",
            listening=False,
            http_healthy=False,
        ),
        launcher_log_dir="artifacts/launcher",
        config_path="configs/integration_demo.yaml",
        control_config_path="configs/sees_control.yaml",
        generated_config_path="configs/generated_full_system_demo.json",
    )

    assert summary["overall_status"] == "DEGRADED"
    assert [service["readiness"] for service in summary["services"]] == [
        "PORT_ONLY",
        "STOPPED",
    ]
    assert "backend port is open but HTTP health failed." in summary[
        "recommended_actions"
    ]
    assert "frontend is not listening on its configured port." in summary[
        "recommended_actions"
    ]


def test_launcher_health_summary_reports_all_services_stopped() -> None:
    summary = build_launcher_health_summary_v2(
        repo_root="D:/code/leo_twin",
        backend=LauncherServiceProbe(
            service="backend",
            role="SEES demo backend",
            port=8765,
            url="http://127.0.0.1:8765",
            health_url="http://127.0.0.1:8765/runtime/status",
            listening=False,
            http_healthy=False,
        ),
        frontend=LauncherServiceProbe(
            service="frontend",
            role="React observability frontend",
            port=5173,
            url="http://127.0.0.1:5173",
            health_url="http://127.0.0.1:5173/",
            listening=False,
            http_healthy=False,
        ),
        launcher_log_dir="artifacts/launcher",
        config_path="configs/integration_demo.yaml",
        control_config_path="configs/sees_control.yaml",
        generated_config_path="configs/generated_full_system_demo.json",
    )

    assert summary["overall_status"] == "STOPPED"
    assert summary["recommended_actions"] == (
        "Run scripts\\sees_launcher.ps1 start.",
    )
    assert summary["paths"]["control_config_path"] == "configs\\sees_control.yaml"
    assert summary["constraints"]["forbidden_integrations"] == (
        "STK",
        "EXATA",
        "AFSIM",
        "DDS",
    )
