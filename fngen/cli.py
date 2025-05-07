import typer
from typer.main import get_command
from click import Context
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import sys
from art import text2art

app = typer.Typer(add_help_option=False, add_completion=False)
console = Console()


# def show_help_default():
#     click_command = get_command(app)
#     ctx = Context(click_command)
#     ctx.info_name = 'fngen'
#     console.print(ctx.get_help())
#     raise typer.Exit()


def show_help_default(ctx: typer.Context, value: bool):
    if not value or ctx.resilient_parsing:
        return
    art_text = text2art('fngen', font='Rammstein')
    rprint(f"[bold blue]{art_text}[/bold blue]")
    console.print(ctx.get_help())
    raise typer.Exit()


def show_custom_help():
    click_command = get_command(app)
    ctx = Context(click_command)

    # Print ASCII art
    try:
        art_text = text2art('fngen', font='Rammstein')
        rprint(f"[bold blue]{art_text}[/bold blue]")
    except Exception:
        rprint("[bold blue]fngen[/bold blue]")

    # Default usage format, similar to Typer's default behavior
    rprint("\n[bold]Usage:[/bold] fngen [OPTIONS] COMMAND [ARGS]...\n")

    # Commands table
    commands_table = Table(
        title="[bold green]Available Commands[/bold green]",
        expand=True  # 👈 makes the table use the full terminal width
    )
    commands_table.add_column("Command", style="cyan", no_wrap=True)
    commands_table.add_column(
        "Description", style="white", no_wrap=False, overflow="fold")

    for name, cmd in click_command.commands.items():
        commands_table.add_row(name, cmd.help or "")

    console.print(commands_table)

    # Options table
    rprint("\n[bold]Global Options:[/bold]")
    options_table = Table(show_header=True)
    options_table.add_column("Option", style="magenta", no_wrap=True)
    options_table.add_column("Description", style="white")

    for param in click_command.params:
        if param.help:
            opts = ", ".join(param.opts)
            options_table.add_row(opts, param.help)

    console.print(options_table)

    rprint("\n[yellow]Run[/yellow] [bold]fngen [command] --help[/bold] [yellow]for more information on a command.[/yellow]")

    raise typer.Exit()


show_help = show_help_default


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    help: bool = typer.Option(
        None,
        "--help",
        "-h",
        is_eager=True,
        expose_value=False,
        callback=show_help,
        help="Show this message and exit.",
    )
):
    if ctx.invoked_subcommand is None:
        show_help(ctx, True)


@app.command(name="connect", help="Connect via FNGEN_API_KEY or ~/.fngen/credentials")
def connect():
    pass


@app.command(name="push", help="Push a deployment package. See docs.md for example structure.")
def push():
    pass


@app.command(name="set_env", help="Securely set a .env file for your project")
def set_env(project_name: str, path_to_env_file: str):
    pass


@app.command(name="version", help="Prints the package version.")
def version():
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            __version__ = version("fngen")
        except PackageNotFoundError:
            __version__ = "unknown (package not installed)"
    except ImportError:
        __version__ = "unknown (importlib.metadata not available)"

    rprint(f"[bold]fngen[/bold] version: [yellow]{__version__}[/yellow]")


# Main entry
if __name__ == "__main__":
    app()
