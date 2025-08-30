from contextlib import closing
import logging
import os
from urllib.parse import urlencode
from fngen.api_key_manager import get_api_key
import orjson
import requests

from fngen.shell_util import run_bash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SERVICE_ENDPOINT = os.getenv("FNGEN_SERVICE_ENDPOINT", 'https://fngen.ai')
TIMEOUT_SECONDS = 3 * 60


def get_auth_headers(profile):
    api_key = get_api_key(profile=profile)

    headers = {
        "Authorization": f"{api_key}",
        "Content-Type": "application/json"
    }
    return headers


def GET(route: str, params: dict = None, send_api_key=True, profile=None) -> dict:
    headers = {}
    if send_api_key:
        headers = get_auth_headers(profile=profile)
    response = requests.get(f'{SERVICE_ENDPOINT}{route}',
                            headers=headers,
                            timeout=TIMEOUT_SECONDS,
                            params=params)
    json = response.json()
    if not response.status_code == 200:
        error_msg = json['detail']
        raise ValueError(error_msg)
    return json


def POST(route: str, body: dict, send_api_key=True, profile=None) -> dict:
    headers = {}
    if send_api_key:
        headers = get_auth_headers(profile=profile)
    response = requests.post(f'{SERVICE_ENDPOINT}{route}',
                             headers=headers,
                             timeout=TIMEOUT_SECONDS,
                             data=orjson.dumps(body))
    json = response.json()
    if not response.status_code == 200:
        error_msg = json['detail']
        raise ValueError(error_msg)
    return json


def DELETE(route: str, body: dict, send_api_key=True, profile=None) -> dict:
    headers = {}
    if send_api_key:
        headers = get_auth_headers(profile=profile)
    response = requests.delete(f'{SERVICE_ENDPOINT}{route}',
                               headers=headers,
                               timeout=TIMEOUT_SECONDS,
                               data=orjson.dumps(body))
    json = response.json()
    if not response.status_code == 200:
        error_msg = json['detail']
        raise ValueError(error_msg)
    return json


def STREAM_SSE(
    route: str,
    params: dict = None,
    send_api_key: bool = True,
    profile: str = None,
    stdout_callback: callable = None,
    stderr_callback: callable = None
):
    """
    Establishes a connection to an SSE stream using curl via the run_bash utility.

    This function blocks and streams output via the provided callbacks.
    Designed for direct use in a CLI command for streaming logs or events.

    Args:
        route: The API route for the SSE stream.
        params: A dictionary of query parameters.
        send_api_key: Whether to include the authentication header.
        profile: The fngen profile to use for getting the API key.
        stdout_callback: A function to call for each line from stdout.
        stderr_callback: A function to call for each line from stderr.

    Returns:
        The final (exit_code, full_stdout, full_stderr, runtime_error) tuple
        from the run_bash command.

    Raises:
        ValueError: If required arguments are missing or API key is not found.
        RuntimeError: Propagated from run_bash if the process can't start.
    """
    if not stdout_callback:
        raise ValueError(
            "A stdout_callback must be provided to process the stream.")

    headers = {}
    if send_api_key:
        api_key = get_api_key(profile=profile)
        if not api_key:
            raise ValueError("API key not found. Please run 'fngen connect'.")
        headers['Authorization'] = api_key

    # Build the full URL with query parameters
    full_url = f"{SERVICE_ENDPOINT}{route}"
    if params:
        full_url += f"?{urlencode(params)}"

    # Build the header arguments for curl
    header_args = ""
    for key, value in headers.items():
        header_args += f"-H '{key}: {value}' "

    # Construct the final curl command.
    # -s: silent (no progress meter)
    # -N: no buffering (essential for streaming)
    command = f"curl -s -N {header_args}'{full_url}'"

    # Define a default stderr_callback if none is provided, to avoid None check inside run_bash
    effective_stderr_callback = stderr_callback or (lambda line: None)

    # Use the run_bash utility to execute the command.
    # Allow exit code 130 for graceful Ctrl+C exit.
    exit_code, full_stdout, full_stderr, runtime_error = run_bash(
        command,
        shell=True,
        stdout_callback=stdout_callback,
        stderr_callback=effective_stderr_callback,
        expected_exit_codes={0, 130}  # Allow success (0) or Ctrl+C (SIGINT)
    )

    return exit_code, full_stdout, full_stderr, runtime_error


def UPLOAD_PRESIGNED_URL(url, fields, file_path):
    max_retries = 3  # Number of retries
    for attempt in range(max_retries):
        try:
            # Open the file to upload
            with open(file_path, 'rb') as file:
                logger.debug(f'[start] POST: {url}')
                response = requests.post(
                    url,
                    data=fields,
                    files={'file': (fields['key'], file)},
                    allow_redirects=False,  # Disable automatic redirect handling
                )
                logger.debug(f'[response] POST: {url} | {response}')

            # Check if a redirect is needed
            if response.status_code in [301, 302]:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    logger.debug(f"Redirecting to: {redirect_url}")

                    # Retry the upload at the new endpoint
                    url = redirect_url
                    continue
                else:
                    raise ValueError(
                        'Redirect location not provided in response')
            else:
                # If no redirect is needed or request is successful, break the loop
                response.raise_for_status()
                return response

        except requests.RequestException as e:
            logger.debug(f"Error during upload: {str(e)}")

            if attempt < max_retries - 1:
                logger.debug("Retrying...")
            else:
                logger.debug("Max retries exceeded")
                raise  # Re-raise the exception if max retries exceeded
