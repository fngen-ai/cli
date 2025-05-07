import typer
from rich.console import Console
from rich import print as rprint
import sys
from art import text2art
import typer.models


app = typer.Typer(add_help_option=False, add_completion=False)
console = Console()


def print_custom_help(ctx: typer.Context):
    """Prints the custom art and the context's help."""
    art_text = text2art('fngen', font='Rammstein')
    rprint(f"[bold blue]{art_text}[/bold blue]")
    console.print(ctx.get_help())


def show_help_callback(ctx: typer.Context, param: typer.models.OptionInfo, value: bool):
    """Callback for the --help option, prints custom help and exits."""
    if not value or ctx.resilient_parsing:
        return

    print_custom_help(ctx)
    raise typer.Exit()


help_option = typer.Option(
    None,
    "--help",
    "-h",
    help="Show this message and exit.",
    is_eager=True,
    expose_value=False,
    callback=show_help_callback,
    show_default=False
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    help: bool = help_option
):
    if ctx.invoked_subcommand is None:
        print_custom_help(ctx)
        raise typer.Exit()


@app.command(name="connect", help="Connect via FNGEN_API_KEY or ~/.fngen/credentials")
def connect(help: bool = help_option):
    pass


@app.command(name="push", help="Push a deployment package. See docs.md for example structure.")
def push(project_name: str,
         path_to_package: str,
         help: bool = help_option):
    pass


@app.command(name="set_env", help="Securely set a .env file for your project")
def set_env(
    project_name: str,
    path_to_env_file: str,
    help: bool = help_option
):
    pass


@app.command(name="version", help="Prints the package version.")
def version(help: bool = help_option):
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            __version__ = version("fngen")
        except PackageNotFoundError:
            __version__ = "unknown (package not installed)"
    except ImportError:
        __version__ = "unknown (importlib.metadata not available)"

    rprint(f"[bold]fngen[/bold] version: [yellow]{__version__}[/yellow]")


if __name__ == "__main__":
    app()
