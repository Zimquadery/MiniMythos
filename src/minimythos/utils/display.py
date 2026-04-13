from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_step_header(step_name: str, description: str) -> None:
    console.rule(f"[bold blue]{step_name}[/bold blue]")
    if description:
        console.print(f"  {description}")


def print_step_result(step_name: str, success: bool, detail: str = "") -> None:
    status = "[bold green]✓[/bold green]" if success else "[bold red]✗[/bold red]"
    msg = f"{status} {step_name}"
    if detail:
        msg += f" — {detail}"
    console.print(msg)


def print_score_table(scores: list) -> None:
    table = Table(title="Vulnerability Scores")
    table.add_column("File", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Reason")
    for s in scores:
        table.add_row(s.path, str(s.score), s.reason)
    console.print(table)


def print_error(message: str) -> None:
    console.print(Panel(f"[red]{message}[/red]", title="Error", border_style="red"))
