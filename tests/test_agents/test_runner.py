import sys
from pathlib import Path
import pytest
from minimythos.agents.runner import AgentRunner, AgentResult

FAKE_AGENT = str(Path(__file__).parent.parent / "helpers" / "fake_agent.py")


@pytest.mark.asyncio
async def test_run_success(tmp_path: Path):
    runner = AgentRunner(command=[sys.executable, FAKE_AGENT], max_parallel=2)
    result = await runner.run("hello world", workdir=tmp_path)
    assert result.success
    assert "hello world" in result.stdout


@pytest.mark.asyncio
async def test_run_failure():
    runner = AgentRunner(command="nonexistent_command_xyz")
    result = await runner.run("test")
    assert not result.success
    assert result.return_code == -1


@pytest.mark.asyncio
async def test_run_parallel(tmp_path: Path):
    runner = AgentRunner(command=[sys.executable, FAKE_AGENT], max_parallel=2)
    tasks = [("task1", tmp_path), ("task2", tmp_path), ("task3", tmp_path)]
    results = await runner.run_parallel(tasks)
    assert len(results) == 3
    assert all(r.success for r in results)


@pytest.mark.asyncio
async def test_run_crashing_script(tmp_path: Path):
    crash_script = tmp_path / "crash.py"
    crash_script.write_text("import sys; sys.exit(1)")
    runner = AgentRunner(command=[sys.executable, str(crash_script)], max_parallel=1)
    result = await runner.run("test", workdir=tmp_path)
    assert result.success is False
    assert result.return_code == 1


@pytest.mark.asyncio
async def test_run_parallel_respects_max_parallel(tmp_path: Path):
    runner = AgentRunner(command=[sys.executable, FAKE_AGENT], max_parallel=1)
    tasks = [("t1", tmp_path), ("t2", tmp_path)]
    results = await runner.run_parallel(tasks)
    assert len(results) == 2
    assert all(r.success for r in results)
