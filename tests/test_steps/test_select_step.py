import json
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest
from minimythos.agents.runner import AgentRunner
from minimythos.steps.select_step import SelectStep
from minimythos.exceptions import PipelineAbort


@pytest.mark.asyncio
async def test_select_step_no_score_file(default_settings):
    runner = AgentRunner(command="echo", max_parallel=1)
    step = SelectStep(default_settings, runner)
    with pytest.raises(PipelineAbort):
        await step.run()


@pytest.mark.asyncio
async def test_select_step_filters_by_threshold(default_settings):
    output_dir = default_settings.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "target_path": str(default_settings.target_path),
        "batches": [
            {
                "batch_id": 0,
                "files": ["src/main.py", "src/auth.py"],
                "scores": [
                    {"path": "src/main.py", "score": 5, "reason": "ok"},
                    {"path": "src/auth.py", "score": 9, "reason": "dangerous"},
                ],
            }
        ],
    }
    (output_dir / "vulnerability_score.json").write_text(json.dumps(data))

    with patch("minimythos.steps.select_step.create_worktree", return_value=True):
        runner = AsyncMock(spec=AgentRunner)
        step = SelectStep(default_settings, runner)
        await step.run()

    selected = json.loads((output_dir / "selected_files.json").read_text())
    assert len(selected) == 1
    assert selected[0]["file_path"] == "src/auth.py"
    assert selected[0]["score"] == 9


@pytest.mark.asyncio
async def test_select_step_sorted_descending(default_settings):
    output_dir = default_settings.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "target_path": str(default_settings.target_path),
        "batches": [
            {
                "batch_id": 0,
                "files": ["a.py", "b.py", "c.py"],
                "scores": [
                    {"path": "a.py", "score": 7, "reason": "r"},
                    {"path": "b.py", "score": 9, "reason": "r"},
                    {"path": "c.py", "score": 8, "reason": "r"},
                ],
            }
        ],
    }
    (output_dir / "vulnerability_score.json").write_text(json.dumps(data))

    with patch("minimythos.steps.select_step.create_worktree", return_value=True):
        runner = AsyncMock(spec=AgentRunner)
        step = SelectStep(default_settings, runner)
        await step.run()

    selected = json.loads((output_dir / "selected_files.json").read_text())
    scores = [s["score"] for s in selected]
    assert scores == [9, 8, 7]


@pytest.mark.asyncio
async def test_select_step_worktree_failure_skips_file(default_settings):
    output_dir = default_settings.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "target_path": str(default_settings.target_path),
        "batches": [
            {
                "batch_id": 0,
                "files": ["a.py", "b.py"],
                "scores": [
                    {"path": "a.py", "score": 8, "reason": "r"},
                    {"path": "b.py", "score": 9, "reason": "r"},
                ],
            }
        ],
    }
    (output_dir / "vulnerability_score.json").write_text(json.dumps(data))

    call_count = 0

    def mock_create(target_repo, worktree_path):
        nonlocal call_count
        call_count += 1
        return call_count == 1

    with patch("minimythos.steps.select_step.create_worktree", side_effect=mock_create):
        runner = AsyncMock(spec=AgentRunner)
        step = SelectStep(default_settings, runner)
        await step.run()

    selected = json.loads((output_dir / "selected_files.json").read_text())
    assert len(selected) == 1
    assert selected[0]["score"] == 9
