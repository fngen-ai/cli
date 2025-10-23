from fngen.cli_util import get_cli_version
from tests.fixtures import ACCEPTANCE_TEST_SERVICE_URL, Sandbox, e2e_sandbox


def test_sandbox(e2e_sandbox: Sandbox):
    sandbox = e2e_sandbox
    

def test_cli_index(e2e_sandbox: Sandbox):
    sandbox = e2e_sandbox
    o = sandbox.run('fngen')
    assert ACCEPTANCE_TEST_SERVICE_URL in o.stdout
    assert get_cli_version() in o.stdout


def test_cli_project_list(e2e_sandbox: Sandbox):
    sandbox = e2e_sandbox
    o = sandbox.run('fngen project list --profile=e2e')
    assert 'staging' in o.stdout


def test_cli_whoami(e2e_sandbox: Sandbox):
    sandbox = e2e_sandbox
    o = sandbox.run('fngen whoami --profile=e2e')
    assert 'e2e@fngen.ai' in o.stdout


def test_cli_version(e2e_sandbox: Sandbox):
    sandbox = e2e_sandbox
    o = sandbox.run('fngen version')
    assert get_cli_version() in o.stdout
