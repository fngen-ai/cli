import logging
import os
import shlex
import subprocess
import threading
from typing import Callable, Optional, Set, Tuple


def run_bash(command: str,
             cwd: Optional[str] = None,
             env: Optional[dict] = None,
             shell: bool = False,
             expected_exit_codes: Optional[Set[int]] = None,
             include_parent_env: bool = False,
             stdout_callback: Optional[Callable[[str], None]] = None,
             stderr_callback: Optional[Callable[[str], None]] = None
             ) -> Tuple[int, str, str, Optional[Exception]]:
    """
    Run a shell command and return (exit_code, stdout, stderr, runtime_error).

    - Supports live streaming via stdout_callback and stderr_callback.
    """
    logger = logging.getLogger(__name__)
    if expected_exit_codes is None:
        expected_exit_codes = {0}

    logger.info(f">>> {command}")

    cmd = command if shell else shlex.split(command)

    # Prepare environment
    if include_parent_env:
        base_env = os.environ.copy()
        if env:
            base_env.update(env)
        run_env = base_env
    else:
        run_env = env

    stdout = []
    stderr = []
    runtime_error = None
    exit_code = -1

    def read_stream(stream, buffer, callback):
        for line in iter(stream.readline, b''):
            decoded = line.decode('utf-8', errors='replace')
            buffer.append(decoded)
            if callback:
                callback(decoded)
        stream.close()

    def serialize_exception(exception):
        return {
            'type': type(exception).__name__,
            'message': str(exception),
            # 'args': exception.args,
            'traceback': ''.join(traceback.format_exception(None, exception, exception.__traceback__))
        }

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=run_env,
            shell=shell,
            bufsize=1,
        )

        stdout_thread = threading.Thread(target=read_stream, args=(
            process.stdout, stdout, stdout_callback))
        stderr_thread = threading.Thread(target=read_stream, args=(
            process.stderr, stderr, stderr_callback))

        stdout_thread.start()
        stderr_thread.start()

        process.wait()
        stdout_thread.join()
        stderr_thread.join()

        exit_code = process.returncode

    except Exception as e:
        runtime_error = e
        exit_code = 127  # Convention for execution failure

    full_stdout = ''.join(stdout)
    full_stderr = ''.join(stderr)

    if runtime_error:
        logger.error(
            f"❌ [runtime error] code:{exit_code} command: {command}\n{serialize_exception(runtime_error)}")
    elif exit_code in expected_exit_codes:
        logger.info(f"✅ [success]\n{full_stdout}")
    else:
        logger.error(
            f"❌ [error] code:{exit_code} command: {command}\n{full_stderr}")

    if runtime_error:
        raise runtime_error

    return exit_code, full_stdout, full_stderr, runtime_error


def print_command(cmd, exit_code, stdout=None, stderr=None, runtime_error=None):
    print(f'\n>>> {cmd}')
    print(f'exit_code: {exit_code}')
    if stdout:
        print(f'--------stdout--------')
        print(stdout)
    if stderr:
        print(f'--------stderr--------')
        print(stderr)
    if runtime_error:
        print(f'--------runtime_error--------')
        print(runtime_error)
