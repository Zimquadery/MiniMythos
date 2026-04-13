import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from minimythos.config import Settings
from minimythos.agents.runner import AgentRunner, AgentResult
from minimythos.orchestrator import Orchestrator
from minimythos.exceptions import PipelineAbort


def test_orchestrator_creation(tmp_codebase, tmp_path):
    settings = Settings(
        target_path=tmp_codebase,
        agent_command="echo",
        output_dir=tmp_path / "output",
    )
    orch = Orchestrator(settings)
    assert orch.settings.target_path == tmp_codebase


@pytest.mark.asyncio
async def test_orchestrator_runs_all_steps(tmp_codebase, tmp_path):
    output_dir = tmp_path / "output"
    settings = Settings(
        target_path=tmp_codebase,
        agent_command=[
            sys.executable,
            str(Path(__file__).parent / "helpers" / "fake_agent.py"),
        ],
        batch_size=10,
        max_parallel_agents=1,
        score_threshold=3,
        output_dir=output_dir,
    )
    orch = Orchestrator(settings)

    with (
        patch("minimythos.steps.select_step.create_worktree", return_value=True),
        patch("minimythos.steps.attack_step.remove_worktree", return_value=True),
    ):
        await orch.run()

    assert (output_dir / "codebase_map.txt").exists()
    assert (output_dir / "vulnerability_score.json").exists()
    assert (output_dir / "selected_files.json").exists()
    assert (output_dir / "security_report.json").exists()
    assert (output_dir / "security_report.md").exists()


@pytest.mark.asyncio
async def test_orchestrator_halts_on_pipeline_abort(tmp_codebase, tmp_path):
    settings = Settings(
        target_path=tmp_codebase,
        agent_command="echo",
        output_dir=tmp_path / "output",
    )
    orch = Orchestrator(settings)

    mock_runner = AsyncMock(spec=AgentRunner)
    mock_runner.run = AsyncMock(
        return_value=AgentResult(stdout="", stderr="fail", return_code=1, success=False)
    )
    mock_runner.run_parallel = AsyncMock(
        return_value=[
            AgentResult(stdout="", stderr="fail", return_code=1, success=False)
        ]
    )
    mock_runner._command_prefix = ["echo"]
    mock_runner.semaphore = MagicMock()
    orch.runner = mock_runner

    await orch.run()
