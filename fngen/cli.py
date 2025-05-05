# fngen/cli.py

import typer
import sys
from art import text2art
from rich.console import Console
from rich.table import Table
from rich import print as rprint

app = typer.Typer()

# --- Function to show commands ---


def show_commands():
    """
    Prints the fngen ASCII art and available commands table.
    """
    # Print ASCII art
    try:
        art_text = text2art('fngen', font='Rammstein')
        rprint(f"[bold blue]{art_text}[/bold blue]")
    except Exception:
        # Fallback if art or font is missing/fails
        rprint("[bold blue]fngen[/bold blue]")

    console = Console()

    # Create a Rich table
    table = Table(title="[bold green]Available Commands[/bold green]")

    # Add columns
    table.add_column("[cyan]Command[/cyan]", style="dim", width=12)
    table.add_column("[cyan]Description[/cyan]")

    # Add a row for the default behavior (explicitly stating what happens with no args)
    table.add_row("", "Show this message and available commands.")

    # Iterate through all registered subcommands
    # Use app.registered_commands to get the list of commands
    for command in app.registered_commands:
        # --- Re-add the table row using command attributes ---
        command_name = command.name
        command_help = command.help or "No description available."  # Fallback if help is None

        # Add a row for each command
        table.add_row(command_name, command_help)
        # --- End re-added code ---

    # Print the table using the console
    console.print(table)  # <--- Re-instated table printing

    # Optional: print usage instructions
    rprint("\n[yellow]Run[/yellow] [bold]fngen [command] --help[/bold] [yellow] for more information on a command.[/yellow]")


@app.command(name="connect", help="Connect to the platform via FNGEN_API_KEY or ~/.fngen/credentials")
def connect():
    pass


@app.command(name="push", help="Push a deployment package. See docs.md for example package structure.")
def push():
    pass


@app.command(name="set_env", help="Securely set a .env file for your project")
def set_env(project_name: str, path_to_env_file: str):
    pass


@app.command(name="version", help="Prints the package version.")
def version():
    """
    Prints the installed version of the fngen package.
    """
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            __version__ = version("fngen")
        except PackageNotFoundError:
            __version__ = "unknown (package not installed)"
    except ImportError:
        __version__ = "unknown (importlib.metadata not available)"

    rprint(f"[bold]fngen[/bold] version: [yellow]{__version__}[/yellow]")


# --- Main execution block ---
if __name__ == "__main__":
    if len(sys.argv) == 1:
        show_commands()
    else:
        app()
# --- End Main execution block ---
