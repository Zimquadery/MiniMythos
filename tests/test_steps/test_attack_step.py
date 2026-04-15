import json
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest
from minimythos.agents.runner import AgentRunner, AgentResult
from minimythos.steps.attack_step import AttackStep


@pytest.mark.asyncio
async def test_attack_step_no_selected_files(default_settings):
    runner = AgentRunner(command="echo", max_parallel=1)
    step = AttackStep(default_settings, runner)
    reports = await step.run()
    assert reports == []


@pytest.mark.asyncio
async def test_attack_step_parses_results(default_settings):
    output_dir = default_settings.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    selected = [
        {
            "file_path": "src/main.py",
            "score": 8,
            "worktree_path": str(default_settings.output_dir / "wt0"),
        }
    ]
    (output_dir / "selected_files.json").write_text(json.dumps(selected))

    agent_output = json.dumps(
        {
            "vulnerabilities": [
                {
                    "title": "SQL Injection",
                    "description": "Unsanitized input",
                    "file_path": "src/main.py",
                    "line_range": "10-20",
                    "severity": "critical",
                    "cwe_id": "CWE-89",
                    "proof": "evidence",
                }
            ]
        }
    )

    runner = AsyncMock(spec=AgentRunner)
    runner.run_parallel = AsyncMock(
        return_value=[
            AgentResult(stdout=agent_output, stderr="", return_code=0, success=True)
        ]
    )

    with patch("minimythos.steps.attack_step.remove_worktree", return_value=True):
        step = AttackStep(default_settings, runner)
        reports = await step.run()

    assert len(reports) == 1
    assert reports[0].success is True
    assert len(reports[0].vulnerabilities) == 1
    assert reports[0].vulnerabilities[0].title == "SQL Injection"


@pytest.mark.asyncio
async def test_attack_step_handles_bad_json(default_settings):
    output_dir = default_settings.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    selected = [
        {
            "file_path": "src/main.py",
            "score": 8,
            "worktree_path": str(default_settings.output_dir / "wt0"),
        }
    ]
    (output_dir / "selected_files.json").write_text(json.dumps(selected))

    runner = AsyncMock(spec=AgentRunner)
    runner.run_parallel = AsyncMock(
        return_value=[
            AgentResult(stdout="not json", stderr="", return_code=0, success=True)
        ]
    )

    with patch("minimythos.steps.attack_step.remove_worktree", return_value=True):
        step = AttackStep(default_settings, runner)
        reports = await step.run()

    assert len(reports) == 1
    assert reports[0].success is False


@pytest.mark.asyncio
async def test_attack_step_cleans_up_worktrees(default_settings):
    output_dir = default_settings.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    selected = [
        {
            "file_path": "src/main.py",
            "score": 8,
            "worktree_path": str(default_settings.output_dir / "wt0"),
        }
    ]
    (output_dir / "selected_files.json").write_text(json.dumps(selected))

    runner = AsyncMock(spec=AgentRunner)
    runner.run_parallel = AsyncMock(
        return_value=[
            AgentResult(
                stdout='{"vulnerabilities":[]}', stderr="", return_code=0, success=True
            )
        ]
    )

    with patch(
        "minimythos.steps.attack_step.remove_worktree", return_value=True
    ) as mock_rm:
        step = AttackStep(default_settings, runner)
        await step.run()
        mock_rm.assert_called()


@pytest.mark.asyncio
async def test_attack_step_parses_markdown_fenced_json(default_settings):
    output_dir = default_settings.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    selected = [
        {
            "file_path": "src/main.py",
            "score": 8,
            "worktree_path": str(default_settings.output_dir / "wt0"),
        }
    ]
    (output_dir / "selected_files.json").write_text(json.dumps(selected))

    fenced = (
        "```json\n"
        '{"vulnerabilities": [{"title": "XSS", "description": "reflected", '
        '"file_path": "src/main.py", "line_range": "5-10", '
        '"severity": "high", "proof": "alert(1)"}], "evidence": "test"}\n'
        "```"
    )

    runner = AsyncMock(spec=AgentRunner)
    runner.run_parallel = AsyncMock(
        return_value=[
            AgentResult(stdout=fenced, stderr="", return_code=0, success=True)
        ]
    )

    with patch("minimythos.steps.attack_step.remove_worktree", return_value=True):
        step = AttackStep(default_settings, runner)
        reports = await step.run()

    assert len(reports) == 1
    assert reports[0].success is True
    assert reports[0].vulnerabilities[0].title == "XSS"
