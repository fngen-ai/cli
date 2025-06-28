import time
from fngen.cli_util import help_option, print_custom_help, console

from fngen.read_api_key import NoAPIKeyError, get_api_key


def login(help: bool = help_option):
    """"""
    with console.status("[bold green]Processing...", spinner="dots"):
        try:
            api_key = get_api_key()
            console.log("Found API Key. Testing connection.")
        except NoAPIKeyError as err:
            console.log("No API Key found.")
            pass
        time.sleep(3)
        console.log("Step 1 complete")
        time.sleep(2)
        console.log("Step 2 complete")
        time.sleep(1)
        console.log("All done!")
    # 1. get api key
    # 2. if api key exists, connect + display good / bad result
    # 3. if api key DNE, prompt for email + password
    # 5. if account DNE, err out
    # 4. if account already exists + api key DNE, create, download + place api key on machine
    pass
