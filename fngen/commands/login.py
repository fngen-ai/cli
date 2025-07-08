from getpass import getpass
import time
from typing import Annotated
from fngen.cli_util import help_option, print_custom_help, console, print_error

from fngen.api_key_manager import NoAPIKeyError, get_api_key, save_api_key
import typer

from fngen.network import GET, POST

from fngen.cli_util import profile_option


def get_login_input():
    email = typer.prompt("Enter your email")
    password = getpass("Enter your password: ")
    return email, password


def login(regenerate: Annotated[
        bool,
        typer.Option(
            "--regenerate", help="Generate a new API key, invalidating any existing one.")
    ] = False,
        help: bool = help_option,
        profile: str = profile_option):
    """
    Log in to FNGEN and configure your local API key.

    This command will guide you through setting up the credentials needed
    to interact with the FNGEN platform via the CLI.
    """
    # print(f'log in: --profile={profile}')

    def prompt_login_flow(route):
        try:
            email, password = get_login_input()
            res = POST(route, {
                'email': email,
                'password': password
            }, send_api_key=False, profile=profile)
            console.print(f"{res}")
            save_api_key(res['secret_key'], profile=profile)
        except Exception as e:
            print_error(e)

    # --regenerate = delete old api key, create + install new one
    if regenerate:
        # always do the hard regen with
        prompt_login_flow('/cli/login_regen_key')
        return

    try:
        api_key = get_api_key(profile=profile)

        # api key already saved = confirm overwrite
        confirm = typer.confirm(
            f"You've already saved an api key for profile `{profile}`. Would you like to overwrite?")
        if not confirm:
            typer.echo("Aborted.")
            raise typer.Abort()
        # do the regen flow
        prompt_login_flow('/cli/login_regen_key')
    except NoAPIKeyError:
        # no api key saved for this profile = normal login
        prompt_login_flow('/cli/login')
