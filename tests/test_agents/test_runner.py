import asyncio
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from minimythos.agents.runner import AgentRunner, AgentResult, _shell_quote_arg

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
    assert result.return_code != 0


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


@pytest.mark.asyncio
async def test_shell_fallback_on_oserror(tmp_path: Path):
    runner = AgentRunner(command=[sys.executable, FAKE_AGENT], max_parallel=1)

    fake_proc = AsyncMock()
    fake_proc.communicate = AsyncMock(return_value=(b"fallback output", b""))
    fake_proc.returncode = 0

    with (
        patch(
            "minimythos.agents.runner.asyncio.create_subprocess_exec",
            side_effect=OSError("not found"),
        ) as mock_exec,
        patch(
            "minimythos.agents.runner.asyncio.create_subprocess_shell",
            return_value=fake_proc,
        ) as mock_shell,
    ):
        result = await runner.run("test", workdir=tmp_path)

    mock_exec.assert_called_once()
    mock_shell.assert_called_once()
    assert result.success
    assert result.stdout == "fallback output"


def test_shell_quote_arg_empty_string():
    assert _shell_quote_arg("") == "''"


def test_shell_quote_arg_safe_string():
    assert _shell_quote_arg("hello") == "hello"


def test_shell_quote_arg_spaces():
    assert _shell_quote_arg("hello world") == "'hello world'"
