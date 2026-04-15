import json
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
from minimythos.agents.runner import AgentRunner, AgentResult
from minimythos.steps.score_step import ScoreStep
from minimythos.exceptions import PipelineAbort


@pytest.mark.asyncio
async def test_score_step_creates_json(default_settings):
    runner = AgentRunner(command=default_settings.agent_command, max_parallel=1)
    step = ScoreStep(default_settings, runner)
    await step.run()
    output_dir = default_settings.output_dir
    score_file = output_dir / "vulnerability_score.json"
    assert score_file.exists()
    data = json.loads(score_file.read_text())
    assert "batches" in data


@pytest.mark.asyncio
async def test_score_step_aborts_all_failed(default_settings):
    runner = AsyncMock(spec=AgentRunner)
    runner.run_parallel = AsyncMock(
        return_value=[
            AgentResult(stdout="", stderr="fail", return_code=1, success=False)
        ]
    )
    step = ScoreStep(default_settings, runner)
    with pytest.raises(PipelineAbort, match="All scoring agents failed"):
        await step.run()


@pytest.mark.asyncio
async def test_score_step_all_bad_json_uses_fallback(default_settings):
    runner = AsyncMock(spec=AgentRunner)
    runner.run_parallel = AsyncMock(
        return_value=[
            AgentResult(
                stdout="not json at all", stderr="", return_code=0, success=True
            )
        ]
    )
    step = ScoreStep(default_settings, runner)
    await step.run()
    data = json.loads(
        (default_settings.output_dir / "vulnerability_score.json").read_text()
    )
    assert data["batches"][0]["scores"][0]["score"] == 0
    assert data["batches"][0]["scores"][0]["reason"] == "Parsing failed"


@pytest.mark.asyncio
async def test_score_step_no_code_files(default_settings):
    empty_dir = default_settings.output_dir / "empty"
    empty_dir.mkdir(parents=True)
    settings = default_settings.model_copy(update={"target_path": empty_dir})
    runner = AgentRunner(command=default_settings.agent_command, max_parallel=1)
    step = ScoreStep(settings, runner)
    with pytest.raises(PipelineAbort, match="No code files discovered"):
        await step.run()


@pytest.mark.asyncio
async def test_score_step_parses_markdown_fenced_json(default_settings):
    fenced = (
        "```json\n"
        '[{"path": "src/main.py", "score": 8, "reason": "hardcoded secret"}]\n'
        "```"
    )
    runner = AsyncMock(spec=AgentRunner)
    runner.run_parallel = AsyncMock(
        return_value=[
            AgentResult(stdout=fenced, stderr="", return_code=0, success=True)
        ]
    )
    step = ScoreStep(default_settings, runner)
    await step.run()
    data = json.loads(
        (default_settings.output_dir / "vulnerability_score.json").read_text()
    )
    assert data["batches"][0]["scores"][0]["score"] == 8
    assert data["batches"][0]["scores"][0]["reason"] == "hardcoded secret"
