import logging
import os
import shlex
import subprocess
import threading
import traceback
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

    logger = logging.getLogger(__name__)
    if expected_exit_codes is None:
        expected_exit_codes = {0}

    logger.debug(f">>> {command}")

    cmd = command if shell else shlex.split(command)

    run_env = os.environ.copy() if include_parent_env else {}
    if env:
        run_env.update(env)

    stdout = []
    stderr = []
    runtime_error = None
    exit_code = -1

    def read_stream(stream, buffer, callback):
        for line in iter(stream.readline, ''):
            buffer.append(line)
            if callback:
                callback(line)
        stream.close()

    def serialize_exception(exception):
        return {
            'type': type(exception).__name__,
            'message': str(exception),
            'traceback': ''.join(traceback.format_exception(None, exception, exception.__traceback__))
        }

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=run_env if run_env else None,
            shell=shell,
            bufsize=1,
            text=True
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
        raise runtime_error
    elif exit_code in expected_exit_codes:
        logger.debug(f"✅ [success]\n{full_stdout}")
    else:
        logger.error(
            f"❌ [error] code:{exit_code} command: {command}\n{full_stderr}")

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
