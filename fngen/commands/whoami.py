from fngen.cli_util import help_option, print_error, rprint, console

from fngen.api_key_manager import NoAPIKeyError, get_api_key

from fngen.network import GET


def whoami(help: bool = help_option):
    try:
        try:
            api_key = get_api_key()

            res = GET('/cli/connect')
            console.print(f"{res}")
        except NoAPIKeyError:
            console.print(
                "No API key found. Please run `fngen login` to set up your API key.")
    except Exception as e:
        print_error(e)
        # raise e
