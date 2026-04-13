from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from minimythos.config import Settings
from minimythos.orchestrator import Orchestrator

console = Console()

PROG = "minimythos"
DESCRIPTION = (
    "AI Security Boss — orchestrates headless agents to find proven security bugs."
)
USAGE = f"%(prog)s [target] [options]"


class _RichHelpFormatter(argparse.HelpFormatter):
    def _format_usage(self, usage, actions, groups, prefix):
        return ""

    def format_help(self):
        console.rule(f"[bold red]{PROG}[/bold red]")
        console.print(f"  {DESCRIPTION}\n")
        console.print(f"[bold]Usage:[/bold]  {PROG} [[bold]TARGET[/bold]] [options]\n")

        table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
        table.add_column("Argument", style="bold cyan", min_width=22)
        table.add_column("Description", style="")
        table.add_column("Default", style="dim")

        table.add_row(
            "TARGET", "Path to the codebase to scan for vulnerabilities.", ". (cwd)"
        )
        table.add_row(
            "-a, --agent AGENT",
            "Agent CLI command to use (e.g. 'opencode', 'claude').",
            "opencode",
        )
        table.add_row(
            "-b, --batch-size N", "Number of files per scoring agent batch.", "10"
        )
        table.add_row(
            "-t, --threshold N",
            "Minimum vulnerability score (1-10) to select a file for attack.",
            "7",
        )
        table.add_row(
            "-p, --max-parallel N", "Maximum number of concurrent agents.", "4"
        )
        table.add_row(
            "-o, --output DIR",
            "Directory to write reports to (defaults to target path).",
            "target path",
        )
        table.add_row("-h, --help", "Show this help message and exit.", "")

        console.print(table)
        return ""


def _validate_target(value: str) -> Path:
    p = Path(value).resolve()
    if not p.exists():
        console.print(f"[red]Error:[/red] target path does not exist: {p}")
        sys.exit(1)
    return p


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        usage=USAGE,
        formatter_class=_RichHelpFormatter,
        add_help=False,
    )
    parser.add_argument("target", nargs="?", default=".", help=argparse.SUPPRESS)
    parser.add_argument("-a", "--agent", default="opencode", help=argparse.SUPPRESS)
    parser.add_argument(
        "-b", "--batch-size", type=int, default=10, help=argparse.SUPPRESS
    )
    parser.add_argument(
        "-t", "--threshold", type=int, default=7, help=argparse.SUPPRESS
    )
    parser.add_argument(
        "-p", "--max-parallel", type=int, default=4, help=argparse.SUPPRESS
    )
    parser.add_argument("-o", "--output", default=None, help=argparse.SUPPRESS)
    parser.add_argument(
        "-h", "--help", action="store_true", default=False, help=argparse.SUPPRESS
    )
    return parser


def scan(
    target: Path,
    agent: str = "opencode",
    batch_size: int = 10,
    threshold: int = 7,
    max_parallel: int = 5,
    output: Path | None = None,
) -> None:
    settings = Settings(
        target_path=target,
        agent_command=agent,
        batch_size=batch_size,
        score_threshold=threshold,
        max_parallel_agents=max_parallel,
        output_dir=output.resolve() if output else target,
    )

    console.rule("[bold red]MiniMythos — AI Security Boss[/bold red]")
    console.print(f"Target: {settings.target_path}")
    console.print(f"Agent:  {settings.agent_command}")
    console.print(f"Output: {settings.output_dir}")
    console.print()

    orchestrator = Orchestrator(settings)
    asyncio.run(orchestrator.run())

    console.rule("[bold green]Scan Complete[/bold green]")


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.help:
        parser.print_help()
        sys.exit(0)

    target = _validate_target(args.target)
    output = Path(args.output) if args.output else None

    scan(
        target=target,
        agent=args.agent,
        batch_size=args.batch_size,
        threshold=args.threshold,
        max_parallel=args.max_parallel,
        output=output,
    )


if __name__ == "__main__":
    main()
