from fngen.cli_util import print_error, help_option, profile_option, console

from fngen.api_key_manager import NoAPIKeyError, get_api_key

from fngen.network import GET, POST

import logging

import requests

from fngen import packaging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def push(project_name: str, source_root_path: str, help: bool = help_option, profile: str = profile_option):
    try:
        try:
            api_key = get_api_key(profile=profile)

            res = POST('/api/project/create_package',
                       {
                           'name': project_name,
                           'archive_type': 'zip'
                       }, profile=profile)

            console.print(f"{res}")

            url = res['presigned_url']
            fields = res['presigned_fields']
            package_id = res['package_id']

            print(f'package_id: {package_id}')

            archive_path = packaging.package_source(
                source_root_path, archive_format='zip')

            print(f'archive_path: {archive_path}')

            __upload_file_with_redirect_handling(url, fields, archive_path)

            res = POST('/api/project/deploy_package', {
                'package_id': package_id
            }, profile=profile)

            console.print(f"{res}")
        except NoAPIKeyError:
            console.print(
                "No API key found. Please run `fngen login` to set up your API key.")
    except Exception as e:
        print_error(e)


def __upload_file_with_redirect_handling(url, fields, file_path):
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
