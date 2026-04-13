import json
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
from minimythos.agents.runner import AgentRunner, AgentResult
from minimythos.steps.map_step import MapStep
from minimythos.exceptions import PipelineAbort


@pytest.mark.asyncio
async def test_map_step_writes_file(default_settings):
    runner = AgentRunner(command=default_settings.agent_command, max_parallel=1)
    step = MapStep(default_settings, runner)
    await step.run()
    output_dir = default_settings.output_dir
    assert (output_dir / "codebase_map.txt").exists()


@pytest.mark.asyncio
async def test_map_step_aborts_on_failure(default_settings):
    runner = AsyncMock(spec=AgentRunner)
    runner.run = AsyncMock(
        return_value=AgentResult(
            stdout="", stderr="crashed", return_code=1, success=False
        )
    )
    step = MapStep(default_settings, runner)
    with pytest.raises(PipelineAbort, match="Map step failed"):
        await step.run()


@pytest.mark.asyncio
async def test_map_step_prompt_includes_target_path(default_settings):
    runner = AsyncMock(spec=AgentRunner)
    runner.run = AsyncMock(
        return_value=AgentResult(
            stdout="map output", stderr="", return_code=0, success=True
        )
    )
    step = MapStep(default_settings, runner)
    await step.run()
    call_args = runner.run.call_args
    prompt = call_args[0][0]
    assert str(default_settings.target_path) in prompt
