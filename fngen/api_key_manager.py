import os
from typing import Optional
import yaml


class NoAPIKeyError(Exception):
    pass


LOCAL_CREDS_PATH = "~/.fngen/credentials.yml"


def get_api_key(profile: Optional[str] = None, creds_path: Optional[str] = None) -> str:
    # 1. use the env var if it exists
    FNGEN_API_KEY = os.getenv("FNGEN_API_KEY", None)
    if FNGEN_API_KEY:
        return FNGEN_API_KEY

    # 2. otherwise, look for ~/.fngen/credentials.yml
    if not creds_path:
        creds_path = LOCAL_CREDS_PATH
    path = os.path.expanduser(creds_path)

    try:
        # Using a 'with' statement is standard practice for file handling
        with open(path, 'r') as f:
            creds = yaml.safe_load(f)
    except FileNotFoundError:
        raise NoAPIKeyError(
            f'No api key detected. Please set (1) FNGEN_API_KEY or (2) {path}')

    if not isinstance(creds, dict):
        raise NoAPIKeyError(f"Credential file at '{path}' is malformed.")

    if not profile:
        profile = 'default'

    if profile not in creds:
        raise NoAPIKeyError(f"No profile named '{profile}' in {path}")

    profile_data = creds.get(profile)
    if not isinstance(profile_data, dict) or 'api_key' not in profile_data:
        raise NoAPIKeyError(
            f"No 'api_key' found in profile '{profile}' in {path}")

    return profile_data['api_key']


def save_api_key(
    api_key: str,
    profile: str = 'default',
    creds_path: Optional[str] = None
):
    """
    Saves or updates an API key for a specific profile in the credentials file.

    This function will create the directory and file if they do not exist.
    It safely reads the existing YAML, updates the specified profile,
    and writes the entire structure back.

    Args:
        api_key: The full, raw API key string to save.
        profile: The name of the profile to save the key under. Defaults to 'default'.
        creds_path: The path to the credentials file. Defaults to LOCAL_CREDS_PATH.
    """
    if not profile:
        raise ValueError("Profile name cannot be empty.")

    if not api_key:
        raise ValueError("API key cannot be empty.")

    # Determine the full, expanded path for the credentials file
    creds_path = creds_path or LOCAL_CREDS_PATH
    path = os.path.expanduser(creds_path)
    dir_path = os.path.dirname(path)

    # 1. Ensure the directory exists (e.g., ~/.fngen)
    try:
        os.makedirs(dir_path, exist_ok=True)
    except OSError as e:
        raise ValueError(
            f"Failed to create credentials directory at '{dir_path}': {e}")

    # 2. Safely read existing credentials, or start with an empty dict
    creds = {}
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                # Use yaml.safe_load and handle case where file is empty or malformed
                loaded_creds = yaml.safe_load(f)
                if isinstance(loaded_creds, dict):
                    creds = loaded_creds
        except (yaml.YAMLError, IOError) as e:
            # If file is corrupt, raise an error to prevent overwriting it accidentally
            raise ValueError(
                f"Could not read or parse existing credentials file at '{path}': {e}")

    # 3. Update or create the profile with the new key
    # Ensure the profile itself is a dictionary to hold the key
    if profile not in creds or not isinstance(creds.get(profile), dict):
        creds[profile] = {}

    creds[profile]['api_key'] = api_key

    # 4. Write the updated credentials back to the file
    try:
        with open(path, 'w') as f:
            # dump_all is not needed for a single doc, Dumper can be specified for formatting
            yaml.dump(creds, f, default_flow_style=False)

        # Optional: Set secure file permissions (recommended)
        os.chmod(path, 0o600)  # Read/write for owner only
    except (IOError, OSError) as e:
        raise ValueError(
            f"Failed to write credentials to '{path}': {e}")
