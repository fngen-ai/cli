import typer
from rich.console import Console
from rich import print as rprint
from art import text2art
import typer.models

console = Console()


def print_custom_help(ctx: typer.Context):
    try:
        art_text = text2art('fngen', font='Rammstein')
        rprint(f"[bold blue]{art_text}[/bold blue]")
    except Exception:
        rprint("[bold blue]fngen[/bold blue]")

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


def print_error(message: str):
    console.print(f"[bold red]ERR:[/] {str(message)}")
