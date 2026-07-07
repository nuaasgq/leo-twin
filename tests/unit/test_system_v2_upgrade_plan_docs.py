from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_system_v2_workstream_tasks_all_record_status() -> None:
    plan = (PROJECT_ROOT / "docs/system_v2_upgrade_plan.md").read_text(
        encoding="utf-8"
    )
    workstreams = plan.split("## 3. V2 Workstreams", maxsplit=1)[1].split(
        "## 4. Sequencing", maxsplit=1
    )[0]

    task_blocks: list[tuple[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    for line in workstreams.splitlines():
        if line.startswith("- V2-"):
            if current_title is not None:
                task_blocks.append((current_title, "\n".join(current_lines)))
            current_title = line
            current_lines = [line]
            continue
        if current_title is not None:
            current_lines.append(line)
    if current_title is not None:
        task_blocks.append((current_title, "\n".join(current_lines)))

    assert len(task_blocks) == 38
    missing_status = [title for title, block in task_blocks if "Status:" not in block]
    assert missing_status == []


def test_system_v2_completion_audit_records_next_hardening_tasks() -> None:
    audit = (PROJECT_ROOT / "docs/system_v2_completion_audit_v1.md").read_text(
        encoding="utf-8"
    )

    for required_text in (
        "Baseline-complete does not mean industrial-complete.",
        "V2-020: Document layered network model contract",
        "T359: Add user-service request evidence cross-links",
        "T360: Add browser-rendered Playwright smoke",
        "T361: Add acceptance YAML disposable-run harness",
        "T362: Add KPI calibration report v2.1",
        "T363: Add 3D visual verification smoke",
    ):
        assert required_text in audit
