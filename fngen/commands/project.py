import time
import typer
from rich.console import Console
from rich import print as rprint
import sys
from art import text2art
import typer.models

from fngen.cli_util import help_option, print_custom_help

from fngen.network import GET, POST


project_app = typer.Typer(name="project", help="Manage projects (list / create / delete / set_env)",
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
    res = GET('/api/projects')
    print(res)


@project_app.command(name="create", help="Create a new project")
def create_project(
    project_name: str = typer.Argument(...,
                                       help="The name of the new project."),
    help: bool = help_option
):
    """Creates a new project with the given name."""
    res = POST('/api/project', {
        'name': project_name
    })
    print(res)
    # rprint(f"[green]Running 'project create' command (placeholder)...[/green]")
    # rprint(f"  Creating project: [bold]{project_name}[/bold]")


@project_app.command(name="delete", help="Delete an existing project")
def delete_project(
    project_name: str = typer.Argument(...,
                                       help="The name of the project to delete."),
    help: bool = help_option
):
    """Deletes the specified project."""
    rprint(f"[red]Running 'project delete' command (placeholder)...[/red]")
    rprint(f"  Deleting project: [bold]{project_name}[/bold]")


@project_app.command(name="set_env", help="Securely set a .env file for your project")
def set_env(
    project_name: str = typer.Argument(..., help="The name of the project"),
    path_to_env_file: str = typer.Argument(..., help="Path to the .env file"),
    help: bool = help_option
):
    """Placeholder for the set_env command."""
    rprint(f"[yellow]Running 'set_env' command (placeholder)...[/yellow]")
    rprint(f"  Project Name: [bold]{project_name}[/bold]")
    rprint(f"  Env File Path: [bold]{path_to_env_file}[/bold]")
