import os
from pathlib import Path
from typing import Callable, NamedTuple, Optional
from uuid import uuid4
from fngen.shell_util import run_bash
import pytest


class CLIResult(NamedTuple):
    exit_code: int
    stdout: str
    stderr: str
    runtime_error: Optional[Exception]

class Sandbox(NamedTuple):
    path: Path
    run: Callable[[str], CLIResult]


ACCEPTANCE_TEST_SERVICE_URL = 'https://staging.fngen.ai'


@pytest.fixture(scope="function")
def sandbox(tmp_path: Path) -> Sandbox:
    sandbox_path = tmp_path
    venv_path = sandbox_path / ".venv"
    
    print(f"\n--- Fixture SETUP: Creating sandbox in '{sandbox_path}' ---")

    def run_bash_sandbox(command: str) -> CLIResult:
        run_env = os.environ.copy()
        run_env["PATH"] = f"{venv_path / 'bin'}:{os.environ.get('PATH')}"
        run_env["FNGEN_SERVICE_ENDPOINT"] = ACCEPTANCE_TEST_SERVICE_URL

        def stream_stdout(line):
            print(f"[sandbox stdout] {line.strip()}")

        def stream_stderr(line):
            print(f"[sandbox stderr] {line.strip()}")
            
        exit_code, stdout, stderr, runtime_error = run_bash(
            command=command,
            cwd=str(sandbox_path),
            env=run_env,
            include_parent_env=False,
            stdout_callback=stream_stdout,
            stderr_callback=stream_stderr,
            shell=True
        )
        return CLIResult(exit_code, stdout, stderr, runtime_error)

    run_bash_sandbox(f"python -m venv {venv_path}")
    project_root = Path(__file__).parent.parent
    install_cmd = (
        f"{venv_path / 'bin' / 'pip'} install -e '{project_root}[test]'"
    )
    run_bash_sandbox(install_cmd)

    yield Sandbox(path=sandbox_path, run=run_bash_sandbox)

    print(f"\n--- Fixture TEARDOWN: Sandbox '{sandbox_path}' will be auto-cleaned. ---")



@pytest.fixture(scope="function")
def project_up_down(sandbox: Sandbox):
    sandbox = sandbox

    rando = str(uuid4())[:8]
    proj_name = f'e2e_project_{rando}'

    print(f"\n--- Fixture SETUP: Creating project '{proj_name}' ---")

    o = sandbox.run(f'fngen project create {proj_name} --profile=e2e')

    yield proj_name

    print(f"\n--- Fixture TEARDOWN: Deleting project '{proj_name}' ---")

    o = sandbox.run(f'fngen project delete {proj_name} --profile=e2e')