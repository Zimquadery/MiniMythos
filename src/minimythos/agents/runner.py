import asyncio
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentResult:
    stdout: str
    stderr: str
    return_code: int
    success: bool


class AgentRunner:
    def __init__(self, command: str | list[str], max_parallel: int = 4):
        if isinstance(command, str):
            self._command_prefix = [command]
        else:
            self._command_prefix = list(command)
        self.semaphore = asyncio.Semaphore(max_parallel)

    async def run(self, prompt: str, workdir: Path | None = None) -> AgentResult:
        try:
            cmd = [*self._command_prefix, "--prompt", prompt]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(workdir) if workdir else None,
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
