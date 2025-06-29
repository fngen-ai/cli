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


@app.command(name="connect", help="Connect via FNGEN_API_KEY or ~/.fngen/credentials")
def connect(help: bool = help_option):
    """Placeholder for the connect command."""
    rprint("[yellow]Running 'connect' command (placeholder)...[/yellow]")


@app.command(name="push", help="Push a deployment package. See docs.md for example structure.")
def push(project_name: str = typer.Argument(..., help="The name of the project"),
         path_to_package: str = typer.Argument(
             ..., help="Path to the deployment package (zip, tar.gz, etc.)"),
         help: bool = help_option):
    """Placeholder for the push command."""
    rprint(f"[yellow]Running 'push' command (placeholder)...[/yellow]")
    rprint(f"  Project Name: [bold]{project_name}[/bold]")
    rprint(f"  Package Path: [bold]{path_to_package}[/bold]")


@app.command(name="set_env", help="Securely set a .env file for your project")
def set_env(
    project_name: str = typer.Argument(..., help="The name of the project"),
    path_to_env_file: str = typer.Argument(..., help="Path to the .env file"),
    help: bool = help_option
):
    """Placeholder for the set_env command."""
    rprint(f"[yellow]Running 'set_env' command (placeholder)...[/yellow]")
    rprint(f"  Project Name: [bold]{project_name}[/bold]")
    rprint(f"  Env File Path: [bold]{path_to_env_file}[/bold]")


@app.command(name="version", help="Prints the package version.")
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


project_app = typer.Typer(name="project", help="List / create / delete projects",
                          add_help_option=False, add_completion=False)


@project_app.callback(invoke_without_command=True)
def project_main(
    ctx: typer.Context,
    help: bool = help_option
):
    if ctx.invoked_subcommand is None:
        print_custom_help(ctx)
        raise typer.Exit()


@project_app.command(name="list", help="List existing projects")
def list_projects(help: bool = help_option):
    """Lists projects associated with the current user/account."""
    rprint("[yellow]Running 'project list' command (placeholder)...[/yellow]")
    rprint("  Listing projects...")


@project_app.command(name="create", help="Create a new project")
def create_project(
    project_name: str = typer.Argument(...,
                                       help="The name of the new project."),
    help: bool = help_option
):
    """Creates a new project with the given name."""
    rprint(f"[green]Running 'project create' command (placeholder)...[/green]")
    rprint(f"  Creating project: [bold]{project_name}[/bold]")


@project_app.command(name="delete", help="Delete an existing project")
def delete_project(
    project_name: str = typer.Argument(...,
                                       help="The name of the project to delete."),
    help: bool = help_option
):
    """Deletes the specified project."""
    rprint(f"[red]Running 'project delete' command (placeholder)...[/red]")
    rprint(f"  Deleting project: [bold]{project_name}[/bold]")


app.add_typer(project_app, name="project")


if __name__ == "__main__":
    app()
