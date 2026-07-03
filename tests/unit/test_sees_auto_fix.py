from leo_twin.reviewer.reviewer_engine import review_path
from leo_twin.sees.auto_fix import AutoFixEngine


def test_auto_fix_replaces_unseeded_randomness(valid_review_workspace):
    target = valid_review_workspace / "src/leo_twin/services/random_use.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "import random\n\n"
        "def value():\n"
        "    return random.random()\n",
        encoding="utf-8",
    )
    before = review_path(valid_review_workspace, repository_root=valid_review_workspace)

    result = AutoFixEngine().fix_until_passes(valid_review_workspace)

    assert "Unseeded randomness detected." in before["violations"]
    assert result.final_report["decision"] == "PASS"
    assert "random.Random(0).random()" in target.read_text(encoding="utf-8")
    assert result.iterations == 1


def test_auto_fix_removes_forbidden_import(valid_review_workspace):
    target = valid_review_workspace / "src/leo_twin/services/bad_import.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "import threading\n\n"
        "def value():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = AutoFixEngine().fix_until_passes(valid_review_workspace)

    assert result.final_report["decision"] == "PASS"
    assert "import threading" not in target.read_text(encoding="utf-8")
