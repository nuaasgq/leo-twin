import json

from leo_twin.reviewer.reviewer_engine import review_path, to_json


def test_reviewer_passes_valid_workspace_deterministically(valid_review_workspace):
    first = review_path(valid_review_workspace, repository_root=valid_review_workspace)
    second = review_path(valid_review_workspace, repository_root=valid_review_workspace)

    assert first == second
    assert first["decision"] == "PASS"
    assert first["total_score"] == 100
    assert set(first["scores"]) == {
        "kernel_integrity",
        "architecture",
        "simulation_semantics",
        "scalability",
        "test_quality",
    }
    assert json.loads(to_json(first)) == first


def test_reviewer_rejects_hard_stop_import(valid_review_workspace):
    bad_file = valid_review_workspace / "src/leo_twin/core/bad_import.py"
    bad_file.write_text("import stk\n", encoding="utf-8")

    report = review_path(valid_review_workspace, repository_root=valid_review_workspace)

    assert report["decision"] == "REJECT"
    assert any("Hard-stop violation" in item for item in report["violations"])


def test_reviewer_penalizes_unseeded_randomness(valid_review_workspace):
    random_file = valid_review_workspace / "src/leo_twin/services/random_use.py"
    random_file.parent.mkdir(parents=True, exist_ok=True)
    random_file.write_text(
        "import random\n\n"
        "def value():\n"
        "    return random.random()\n",
        encoding="utf-8",
    )

    report = review_path(valid_review_workspace, repository_root=valid_review_workspace)

    assert report["decision"] != "PASS"
    assert "Unseeded randomness detected." in report["violations"]
