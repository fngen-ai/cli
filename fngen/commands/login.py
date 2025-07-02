from getpass import getpass
import time
from typing import Annotated
from fngen.cli_util import help_option, print_custom_help, console, print_error

from fngen.api_key_manager import NoAPIKeyError, get_api_key, save_api_key
import typer

from fngen.network import GET, POST


def get_login_input():
    email = typer.prompt("Enter your email")
    password = getpass("Enter your password: ")
    return email, password


def login(regenerate: Annotated[
        bool,
        typer.Option(
            "--regenerate", help="Generate a new API key, invalidating any existing one.")
    ] = False,
        help: bool = help_option):
    """
    Log in to FNGEN and configure your local API key.

    This command will guide you through setting up the credentials needed
    to interact with the FNGEN platform via the CLI.
    """
    try:
        if regenerate:
            email, password = get_login_input()
            res = POST('/cli/login_regen_key', {
                'email': email,
                'password': password
            }, send_api_key=False)
            console.print(f"{res}")
            save_api_key(res['secret_key'], profile='default')
        else:
            try:
                api_key = get_api_key()

                res = GET('/cli/connect')
                console.print(f"{res}")
            except NoAPIKeyError:
                email, password = get_login_input()

                res = POST('/cli/login', {
                    'email': email,
                    'password': password
                }, send_api_key=False)
                console.print(f"{res}")
                save_api_key(res['secret_key'], profile='default')
    except Exception as e:
        print_error(e)
        # raise e
