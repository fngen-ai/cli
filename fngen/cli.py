from fngen.commands.project import project_app
import time
import typer
from rich.console import Console
from rich import print as rprint
import sys
from art import text2art
import typer.models
from importlib.metadata import version, PackageNotFoundError

from fngen.api_key_manager import NoAPIKeyError, get_api_key
from fngen.cli_util import help_option, print_custom_help

from fngen.commands.login import login

from fngen.commands.whoami import whoami

app = typer.Typer(add_help_option=False, add_completion=False)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    help: bool = help_option
):
    if ctx.invoked_subcommand is None:
        print_custom_help(ctx)
        raise typer.Exit()


app.command(name="login", help="Log in + set up your API key")(login)

app.command(name="whoami", help="Test your API key")(whoami)

app.add_typer(project_app, name="project")


@app.command(name="push", help="Push a deployment package")
def push(project_name: str = typer.Argument(..., help="The name of the project"),
         path_to_package: str = typer.Argument(
             ..., help="Path to the deployment package (zip, tar.gz, etc.)"),
         help: bool = help_option):
    """Placeholder for the push command."""
    rprint(f"[yellow]Running 'push' command (placeholder)...[/yellow]")
    rprint(f"  Project Name: [bold]{project_name}[/bold]")
    rprint(f"  Package Path: [bold]{path_to_package}[/bold]")


@app.command(name="version", help="Print fngen version")
def _version(help: bool = help_option):
    """Prints the package version."""
    try:
        try:
            __version__ = version("fngen")
        except PackageNotFoundError:
            __version__ = "unknown (package not installed)"
    except ImportError:
        __version__ = "unknown (importlib.metadata not available)"

    rprint(f"[bold]fngen[/bold] version: [yellow]{__version__}[/yellow]")


if __name__ == "__main__":
    app()
