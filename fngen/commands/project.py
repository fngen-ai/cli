from pathlib import Path
import time
import typer
from rich.console import Console
from rich import print as rprint
import sys
from art import text2art
import typer.models

from fngen.api_key_manager import NoAPIKeyError
from fngen.cli_util import help_option, print_custom_help, print_error
from fngen.cli_util import profile_option

from fngen.network import DELETE, GET, POST, SERVICE_ENDPOINT, UPLOAD_PRESIGNED_URL
from rich.table import Table
from rich import box


console = Console()

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
def list_projects(help: bool = help_option, profile: str = profile_option):
    """Lists projects associated with the current user/account."""
    res = GET('/api/projects', profile=profile)
    table = Table(
        title=f"\n[bold cyan]Projects[/bold cyan]",
        title_justify='left',
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )

    table.add_column("Name", style="dim", width=20)
    table.add_column("Status", justify="center")
    table.add_column("Web Dashboard", style="blue")

    for project in res:
        slug = project['slug']
        dashboard_url = f'{SERVICE_ENDPOINT}/p/{slug}'
        table.add_row(project["name"], project['status'], dashboard_url)

    console.print(table)


@project_app.command(name="create", help="Create a new project")
def create_project(
    project_name: str = typer.Argument(...,
                                       help="The name of the new project."),
    help: bool = help_option,
    profile: str = profile_option
):
    """Creates a new project with the given name."""
    res = POST('/api/project', {
        'name': project_name
    }, profile=profile)
    print(res)
    # rprint(f"[green]Running 'project create' command (placeholder)...[/green]")
    # rprint(f"  Creating project: [bold]{project_name}[/bold]")


@project_app.command(name="delete", help="Delete an existing project")
def delete_project(
    project_name: str = typer.Argument(...,
                                       help="The name of the project to delete."),
    help: bool = help_option,
    profile: str = profile_option
):
    """Deletes the specified project."""
    res = DELETE('/api/project', {
        'project_name': project_name
    }, profile=profile)
    print(res)


@project_app.command(name="set_env", help="Securely set a .env file for your project")
def set_env(project_name: str, path_to_env_file: str, help: bool = help_option, profile: str = profile_option):
    try:
        if Path(path_to_env_file).suffix != '.env':
            raise ValueError(f'Your env file should have a .env extension')

        res = POST(f'/api/project/{project_name}/set_env',
                   {}, profile=profile)

        url = res['presigned_url']
        fields = res['presigned_fields']

        UPLOAD_PRESIGNED_URL(url, fields, path_to_env_file)

    except NoAPIKeyError:
        console.print(
            "No API key found. Please run `fngen login` to set up your API key.")
    except Exception as e:
        print_error(e)
