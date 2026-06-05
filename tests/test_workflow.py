from pathlib import Path


def test_pr_unit_test_workflow_triggers_on_pull_request():
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "pr-unit-tests.yml"
    content = workflow_path.read_text(encoding="utf-8")

    assert "on:\n  pull_request:" in content
    assert "run: pytest" in content
    assert "name: Run unit tests" in content
