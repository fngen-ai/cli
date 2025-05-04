import typer

app = typer.Typer()


@app.command()
def main(name: str = "World"):
    """
    A simple command that greets someone.
    """
    typer.echo(f"Hello {name} from fngen CLI!")


if __name__ == "__main__":
    app()
