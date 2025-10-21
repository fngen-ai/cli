from importlib.metadata import PackageNotFoundError, version
from fngen.network import SERVICE_ENDPOINT
import typer
from rich.console import Console
from rich import print as rprint
from art import text2art
import typer.models

console = Console()


def get_cli_version():
    try:
        try:
            __version__ = version("fngen")
        except PackageNotFoundError:
            __version__ = "unknown (package not installed)"
    except ImportError:
        __version__ = "unknown (importlib.metadata not available)"
    return __version__


def print_custom_help(ctx: typer.Context):
    try:
        art_text = text2art('fngen', font='Rammstein')
        rprint(f"[bold blue]{art_text}[/bold blue]")
    except Exception:
        rprint("[bold blue]fngen[/bold blue]")

    rprint(f"CLI Version: [yellow]{get_cli_version()}[/yellow]")
    rprint(f"Service URL: [yellow]{SERVICE_ENDPOINT}[/yellow]")

    console.print(ctx.get_help())


def show_help_callback(ctx: typer.Context, param: typer.models.OptionInfo, value: bool):
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

profile_option = typer.Option(
    "default",
    "--profile",
    "-p",
    help="Set the FNGEN profile to use",
    is_eager=True,
    expose_value=True,
    # callback=show_help_callback,
    show_default=False
)


def print_error(message: str):
    console.print(f"[bold red]ERR:[/] {str(message)}")
