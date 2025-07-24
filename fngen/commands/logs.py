import typer
from rich.console import Console

from fngen.network import STREAM_SSE
from fngen.cli_util import profile_option

API_BASE_URL = "https://fngen.ai/api"


console = Console()


def logs(
    project_name: str = typer.Argument(..., help="The name of the project"),
    follow: bool = typer.Option(
        True, "--follow", "-f", help="Follow the log output."),
    profile: str = profile_option
):
    """Fetch and display logs for a project."""

    if not follow:
        console.print(
            "[yellow]Non-streaming logs not yet implemented. Use --follow.[/yellow]")
        raise typer.Exit()

    console.print(
        f"[cyan]--->[/cyan] Connecting to log stream for [bold]{project_name}[/bold]. Press Ctrl+C to exit.")

    def print_log_line(line: str):
        """A simple callback to print each line received from the stream."""
        # Here you could add parsing logic if the line is JSON, etc.
        # For now, we just print it. The `end=''` prevents extra newlines.
        print(line, end='')

    try:
        STREAM_SSE(
            route="/api/logs/stream",
            params={"project_name": project_name},
            profile=profile,
            stdout_callback=print_log_line
        )
        console.print(f"\n[cyan]<---[/cyan] Stream finished.")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        # This is the graceful exit path for the user.
        console.print(f"\n[cyan]<---[/cyan] Disconnected from log stream.")
        raise typer.Exit()
