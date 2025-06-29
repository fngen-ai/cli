from fngen.api_key_manager import get_api_key


def test_parse_credentials():
    api_key = get_api_key(profile='default',
                          creds_path='tests/test_credentials.yml')

    assert api_key == 'fng_sk_live_xxxxxxxxxxxxxxxxxxxxxxxx'
