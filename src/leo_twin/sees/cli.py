"""Command-line entry points for SEES."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from leo_twin.reviewer.reviewer_engine import review_path, summary, to_json
from leo_twin.sees.auto_fix import AutoFixEngine
from leo_twin.sees.ci_gate import CIGate
from leo_twin.sees.evolution_controller import EvolutionController
from leo_twin.sees.runner import SEESRunner
from leo_twin.sees.task_dag import EngineeringTask


def main_review(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sees-review")
    parser.add_argument("--diff", required=True, help="Path to a diff file or snapshot directory.")
    args = parser.parse_args(argv)
    report = review_path(Path(args.diff), repository_root=Path.cwd())
    print(to_json(report))
    print(summary(report), file=sys.stderr)
    return 0 if report["decision"] == "PASS" else 1


def main_fix(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sees-fix")
    parser.add_argument("--workspace", required=True, help="Workspace to repair and review.")
    args = parser.parse_args(argv)
    result = AutoFixEngine().fix_until_passes(Path(args.workspace))
    payload = {
        "iterations": result.iterations,
        "applied_actions": [
            {"path": action.path, "description": action.description}
            for action in result.applied_actions
        ],
        "final_report": result.final_report,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.final_report["decision"] == "PASS" else 1


def main_evolve(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sees-evolve")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--report", required=True, help="Path to a reviewer JSON report.")
    args = parser.parse_args(argv)
    report = json.loads(Path(args.report).read_text(encoding="utf-8-sig"))
    task = EngineeringTask(
        task_id=args.task_id,
        title=args.task_id,
        description="Failed task imported from CLI.",
        issue_id=args.task_id,
    )
    subtasks = EvolutionController().split_failed_task(task, report)
    print(
        json.dumps(
            [
                {
                    "task_id": subtask.task_id,
                    "title": subtask.title,
                    "description": subtask.description,
                    "dependencies": list(subtask.dependencies),
                }
                for subtask in subtasks
            ],
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def main_run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sees-run")
    parser.add_argument("--workspace", required=True, help="Workspace to process.")
    args = parser.parse_args(argv)
    result = SEESRunner().run_generated_task(Path(args.workspace))
    payload = {
        "task_id": result.task_id,
        "execution": {
            "status": result.execution.status,
            "changed_files": list(result.execution.changed_files),
        },
        "ci_exit_code": result.ci_exit_code,
        "generated_tasks": [task.task_id for task in result.generated_tasks],
        "final_report": result.final_report,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return result.ci_exit_code


def main_ci(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sees-ci")
    parser.add_argument("--workspace", required=True, help="Workspace to gate.")
    args = parser.parse_args(argv)
    exit_code, report = CIGate().review_workspace(Path(args.workspace))
    print(to_json(report))
    return exit_code
