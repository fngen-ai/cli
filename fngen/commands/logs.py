import typer
from rich.console import Console
from typing import Optional

from fngen.network import STREAM_SSE
from fngen.cli_util import profile_option

API_BASE_URL = "https://fngen.ai/api"

console = Console()


def logs(
    project_name: str = typer.Argument(...,
                                       help="The name of the project to fetch logs for."),

    follow: bool = typer.Option(
        False,
        "--follow", "-f",
        help="Follow log output in real-time."
    ),
    tail: Optional[int] = typer.Option(
        None,
        "--tail", "-n",
        help="Show the last N lines. Defaults to 200 if no other filters are used."
    ),
    since: Optional[str] = typer.Option(
        None,
        "--since",
        help="Show logs since a specific time (e.g., '1h', '10m', '2024-05-18')."
    ),
    search: Optional[str] = typer.Option(
        None,
        "--search", "-s",
        help="Filter logs for messages containing this text (case-insensitive)."
    ),

    profile: str = profile_option
):
    """
    Fetch and display logs for a project. Supports real-time streaming, tailing,
    time-based filtering, and text search.
    """

    params = {"project_name": project_name}
    if follow:
        params["follow"] = True
    if tail is not None:
        params["tail"] = tail
    if since:
        params["since"] = since
    if search:
        params["search"] = search

    if follow:
        console.print(
            f"[cyan]--->[/cyan] Connecting to log stream for [bold]{project_name}[/bold]. Press Ctrl+C to exit.")
    else:
        console.print(
            f"[cyan]--->[/cyan] Fetching logs for [bold]{project_name}[/bold]...")

    # def print_log_line(line: str):
    #     """A simple callback to print each line received from the stream."""
    #     print(line.rstrip())

    def print_log_line(line: str):
        """
        Callback to process and print each line from the SSE stream.
        It only prints the payload of "data:" messages.
        """
        clean_line = line.rstrip()

        if clean_line.startswith('data:'):
            print(clean_line[6:])

    try:
        STREAM_SSE(
            route="/api/logs/stream",
            params=params,
            profile=profile,
            stdout_callback=print_log_line
        )
        if not follow:
            console.print(f"[cyan]<---[/cyan] Log request complete.")

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        # Ctrl+C.
        console.print(f"\n[cyan]<---[/cyan] Disconnected from log stream.")
        raise typer.Exit()
