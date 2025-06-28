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
