from pathlib import Path
from typing import Annotated, Optional
import asyncio
import typer
from rich.console import Console

from minimythos.config import Settings
from minimythos.orchestrator import Orchestrator

app = typer.Typer(
    name="minimythos",
    help="AI Security Boss — orchestrates headless agents to find proven security bugs.",
)

console = Console()


@app.command()
def scan(
    target: Annotated[
        Path,
        typer.Argument(
            help="Path to the codebase to scan for vulnerabilities.",
            exists=True,
            readable=True,
        ),
    ],
    agent: Annotated[
        str,
        typer.Option(
            "--agent",
            "-a",
            help="Agent CLI command to use (e.g. 'opencode', 'claude').",
        ),
    ] = "opencode",
    batch_size: Annotated[
        int,
        typer.Option(
            "--batch-size",
            "-b",
            help="Number of files per scoring agent batch.",
        ),
    ] = 10,
    threshold: Annotated[
        int,
        typer.Option(
            "--threshold",
            "-t",
            help="Minimum vulnerability score (1-10) to select a file for attack.",
        ),
    ] = 7,
    max_parallel: Annotated[
        int,
        typer.Option(
            "--max-parallel",
            "-p",
            help="Maximum number of concurrent agents.",
        ),
    ] = 4,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Directory to write reports to (defaults to target path).",
        ),
    ] = None,
):
    settings = Settings(
        target_path=target.resolve(),
        agent_command=agent,
        batch_size=batch_size,
        score_threshold=threshold,
        max_parallel_agents=max_parallel,
        output_dir=output.resolve() if output else target.resolve(),
    )

    console.rule("[bold red]MiniMythos — AI Security Boss[/bold red]")
    console.print(f"Target: {settings.target_path}")
    console.print(f"Agent:  {settings.agent_command}")
    console.print(f"Output: {settings.output_dir}")
    console.print()

    orchestrator = Orchestrator(settings)
    asyncio.run(orchestrator.run())

    console.rule("[bold green]Scan Complete[/bold green]")
