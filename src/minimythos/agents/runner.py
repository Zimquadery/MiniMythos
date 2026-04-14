import asyncio
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from minimythos.agents.registry import resolve_command


@dataclass
class AgentResult:
    stdout: str
    stderr: str
    return_code: int
    success: bool


class AgentRunner:
    def __init__(self, command: str | list[str], max_parallel: int = 5):
        self._raw_command = command
        self.semaphore = asyncio.Semaphore(max_parallel)

    async def run(self, prompt: str, workdir: Path | None = None) -> AgentResult:
        try:
            cmd = resolve_command(self._raw_command, prompt)
            cwd = str(workdir) if workdir else None

            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                )
            except OSError:
                shell_cmd = (
                    subprocess.list2cmdline(cmd)
                    if sys.platform == "win32"
                    else " ".join(_shell_quote_arg(a) for a in cmd)
                )
                process = await asyncio.create_subprocess_shell(
                    shell_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                )

            stdout_bytes, stderr_bytes = await process.communicate()
            return AgentResult(
                stdout=stdout_bytes.decode("utf-8", errors="replace"),
                stderr=stderr_bytes.decode("utf-8", errors="replace"),
                return_code=process.returncode or 0,
                success=process.returncode == 0,
            )
        except Exception as e:
            return AgentResult(
                stdout="",
                stderr=str(e),
                return_code=-1,
                success=False,
            )

    async def run_parallel(
        self, tasks: list[tuple[str, Path | None]]
    ) -> list[AgentResult]:
        async def bounded_run(prompt: str, workdir: Path | None) -> AgentResult:
            async with self.semaphore:
                return await self.run(prompt, workdir)

        coros = [bounded_run(prompt, wd) for prompt, wd in tasks]
        return await asyncio.gather(*coros)


def _shell_quote_arg(arg: str) -> str:
    if not arg:
        return "''"
    if any(c in arg for c in " \t\n\"'\\$`!#&|;(){}<>?*[]"):
        return "'" + arg.replace("'", "'\\''") + "'"
    return arg
