from fngen.api_key_manager import get_api_key
import orjson
import requests


SERVICE_ENDPOINT = 'https://fngen.ai'
TIMEOUT_SECONDS = 3 * 60


def get_auth_headers():
    api_key = get_api_key()

    headers = {
        "Authorization": f"{api_key}",
        "Content-Type": "application/json"
    }
    return headers


def GET(route: str, params: dict = None, send_api_key=True) -> dict:
    headers = {}
    if send_api_key:
        headers = get_auth_headers()
    response = requests.get(f'{SERVICE_ENDPOINT}{route}',
                            headers=headers,
                            timeout=TIMEOUT_SECONDS,
                            params=params)
    json = response.json()
    if not response.status_code == 200:
        error_msg = json['detail']
        raise ValueError(error_msg)
    return json


def POST(route: str, body: dict, send_api_key=True) -> dict:
    headers = {}
    if send_api_key:
        headers = get_auth_headers()
    response = requests.post(f'{SERVICE_ENDPOINT}{route}',
                             headers=headers,
                             timeout=TIMEOUT_SECONDS,
                             data=orjson.dumps(body))
    json = response.json()
    if not response.status_code == 200:
        error_msg = json['detail']
        raise ValueError(error_msg)
    return json
