import pytest
from fngen.cli_util import get_cli_version
from tests.assets.asset_manager import copy_example_package
from tests.fixtures import ACCEPTANCE_TEST_SERVICE_URL, Sandbox, sandbox, project_up_down


def test_sandbox(sandbox: Sandbox):
    pass
    

def test_cli_index(sandbox: Sandbox):
    o = sandbox.run('fngen')
    assert ACCEPTANCE_TEST_SERVICE_URL in o.stdout
    assert get_cli_version() in o.stdout


def test_cli_project_list(sandbox: Sandbox):
    o = sandbox.run('fngen project list --profile=e2e')
    assert 'staging' in o.stdout


def test_cli_whoami(sandbox: Sandbox):
    o = sandbox.run('fngen whoami --profile=e2e')
    assert 'e2e@fngen.ai' in o.stdout


def test_cli_version(sandbox: Sandbox):
    o = sandbox.run('fngen version')
    assert get_cli_version() in o.stdout


def test_project_up_down(sandbox: Sandbox, project_up_down: str):
    proj_name = project_up_down
    o = sandbox.run('fngen project list --profile=e2e')
    assert proj_name in o.stdout


@pytest.mark.skip(reason="Run when desired")
def test_push_directory(sandbox: Sandbox, project_up_down: str):
    package_path = copy_example_package('hello_fastapi', sandbox.path)
    o = sandbox.run(f'fngen push {project_up_down} {package_path} --profile=e2e')
    x = 0

# def test_push_single_module():
#     pass

