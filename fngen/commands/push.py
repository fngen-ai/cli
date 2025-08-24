from functools import partial
import json
from queue import Queue
import threading
from typing import Dict, Generator, Optional
from rich.console import Console, Group
from rich.text import Text
import random
import time
from rich.live import Live
from rich.table import Table
from fngen.cli_util import print_error, help_option, profile_option, console

from fngen.api_key_manager import NoAPIKeyError, get_api_key

from fngen.network import GET, POST, STREAM_SSE, UPLOAD_PRESIGNED_URL

import logging

import requests

from fngen import packaging
import typer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def push(project_name: str, source_root_path: str, help: bool = help_option, profile: str = profile_option):
    try:
        try:
            api_key = get_api_key(profile=profile)

            res = POST('/api/project/create_package',
                       {
                           'project_name': project_name,
                           'format_type': 'zip'
                       }, profile=profile)

            # console.print(f"{res}")

            url = res['presigned_url']
            fields = res['presigned_fields']
            package_id = res['package_id']

            # print(f'package_id: {package_id}')

            archive_path = packaging.package_source(
                source_root_path, format_type='zip')

            # print(f'archive_path: {archive_path}')

            UPLOAD_PRESIGNED_URL(url, fields, archive_path)

            res = POST('/api/push', {
                'project_key': project_name,
                'package_id': package_id
            }, profile=profile)

            console.print(f"{res}")

            pipeline_id = res['pipeline_id']

            run_push_live_view_for_pipeline(
                pipeline_id=pipeline_id, profile=profile)

        except NoAPIKeyError:
            console.print(
                "No API key found. Please run `fngen login` to set up your API key.")
    except Exception as e:
        print_error(e)


def get_real_event_stream(pipeline_id: str, profile: str) -> Generator[Dict, None, None]:
    """
    Connects to the live SSE stream and yields parsed event dictionaries.
    Includes detailed debugging print statements.
    """
    event_queue: Queue[Optional[Dict]] = Queue()

    def sse_callback(line: str):
        """Callback for stdout from the SSE stream."""
        clean_line = line.rstrip()
        if clean_line.startswith('data:'):
            message_payload = clean_line[6:]
            try:
                event_dict = json.loads(message_payload)
                event_queue.put(event_dict)
            except json.JSONDecodeError:
                event_queue.put({
                    "name": "log.info",
                    "data": {"stage": None, "message": message_payload}
                })

    def stderr_callback(line: str):
        """Callback for stderr from the curl command."""
        # You can also put stderr messages on the queue as global logs
        event_queue.put({
            "name": "log.info",
            "data": {"stage": None, "message": f"[CURL STDERR] {line.strip()}"}
        })

    def stream_target():
        """The target function for the background thread."""
        try:
            STREAM_SSE(
                route=f"/api/deployments/{pipeline_id}/stream",
                profile=profile,
                stdout_callback=sse_callback,
                stderr_callback=stderr_callback  # <-- Make sure to pass stderr callback
            )
        except Exception as e:
            event_queue.put({
                "name": "pipeline.failed",
                "data": {"message": f"❌ Stream connection failed: {e}"}
            })
        finally:
            event_queue.put(None)

    # --- Main Generator Logic ---
    stream_thread = threading.Thread(target=stream_target, daemon=True)
    stream_thread.start()

    while True:
        event = event_queue.get()
        if event is None:
            break
        yield event

    stream_thread.join()


# --- The UI State Management and Rendering Logic ---

def update_view_state(state: dict, event: dict):
    """
    Processes an event and MUTATES the state dictionary in place.
    This is a common pattern in functional-style UI updates.
    """
    event_type = event.get("name")
    data = event.get("data", {})
    stage = data.get("stage")

    if event_type == "pipeline.init":
        state["pipeline_stages"] = data.get("stages", [])
        state["stage_statuses"] = {s: ("pending", "")
                                   for s in state["pipeline_stages"]}
    elif event_type == "stage.started":
        if stage in state["stage_statuses"]:
            state["stage_statuses"][stage] = ("running", "")
    elif event_type == "stage.success":
        if stage in state["stage_statuses"]:
            state["stage_statuses"][stage] = ("success", "")
    elif event_type == "stage.error":
        if stage in state["stage_statuses"]:
            state["stage_statuses"][stage] = (
                "failed", f"[italic red]{data.get('message')}[/italic red]")
    elif event_type == "log.info":
        if stage and stage in state["stage_statuses"]:
            state["stage_statuses"][stage] = (
                "running", f"[dim]- {data.get('message')}[/dim]")
        else:
            state["global_logs"].append(f"[dim] > {data.get('message')}[/dim]")


def render_view(state: dict) -> Group:
    """Generates a Rich Group of renderables from the current state dictionary."""
    stages_table = Table(box=None, show_header=False, padding=(0, 1, 0, 1))
    stages_table.add_column("Status", width=4)
    stages_table.add_column("Stage")
    stages_table.add_column("Details")

    pipeline_stages = state.get("pipeline_stages", [])
    stage_statuses = state.get("stage_statuses", {})

    if not pipeline_stages:
        stages_table.add_row("[yellow]⧖[/yellow]",
                             "Initializing deployment...")
    else:
        for stage_name in pipeline_stages:
            status, details = stage_statuses.get(stage_name, ("pending", ""))
            icon = {"pending": "[dim]●[/dim]", "running": "[yellow]⧖[/yellow]",
                    "success": "[green]✅[/green]", "failed": "[red]❌[/red]"}.get(status)

            stage_text = stage_name
            if status == "running":
                stage_text = f"[bold]{stage_name}[/bold]"
            elif status == "pending":
                stage_text = f"[dim]{stage_name}[/dim]"
            elif status == "failed":
                stage_text = f"[bold red]{stage_name}[/bold red]"

            stages_table.add_row(icon, stage_text, details)

    global_logs = [Text(log) for log in state.get("global_logs", [])]
    return Group(stages_table, *global_logs)


def run_push_live_view(_event_stream_provider: callable):
    view_state = {"pipeline_stages": [],
                  "stage_statuses": {}, "global_logs": []}
    final_event = {}
    initialized = False
    initialization_timeout = time.time() + 30

    with Live(render_view(view_state), console=console, auto_refresh=False, vertical_overflow="visible") as live:
        for event in _event_stream_provider():
            # Let's print the event we are about to process

            update_view_state(view_state, event)

            event_type = event.get("name")
            if not initialized and event_type == "pipeline.init":
                initialized = True

            if not initialized and time.time() > initialization_timeout:
                console.print(
                    "\n[bold red]Error:[/bold red] Timed out waiting for deployment to initialize.")
                raise typer.Exit(code=1)

            live.update(render_view(view_state), refresh=True)

            if event_type in ("pipeline.succeeded", "pipeline.failed"):
                final_event = event
                break

    # This part remains the same
    final_data = final_event.get("data", {})
    console.print(
        f"\n[bold]{final_data.get('message', 'Deployment finished.')}[/bold]")
    if url := final_data.get("details", {}).get("url"):
        console.print(f"🚀 Your app is live at: [link={url}]{url}[/link]")


def run_push_live_view_for_pipeline(pipeline_id, profile):
    try:
        # STREAM_SSE(
        #     route=f"/api/deployments/{pipeline_id}/stream",
        #     # params=params,
        #     profile=profile,
        #     stdout_callback=print_log_line
        # )
        if False:
            # hack for dynamic call graph building
            get_real_event_stream()

        event_stream_provider = partial(
            get_real_event_stream, pipeline_id=pipeline_id, profile=profile)

        # 2. We pass this new, callable function (the "provider") to the UI renderer.
        run_push_live_view(event_stream_provider)

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        # Ctrl+C.
        console.print(f"\n[cyan]<---[/cyan] Disconnected from log stream.")
        raise typer.Exit()


def watch_pipeline(pipeline_id, help: bool = help_option, profile: str = profile_option):
    run_push_live_view_for_pipeline(pipeline_id, profile)


def simulate_push(project_name: str = typer.Argument("my-cool-project")):
    """Simulates a deployment with a live-updating status view (functional approach)."""
    STAGES_FOR_THIS_RUN = ["Parsing Project", "Provisioning Infrastructure",
                           "Deploying Application", "Confirming Health", ]

    def simulate_stateful_event_stream():
        yield {"name": "pipeline.init", "data": {"stages": STAGES_FOR_THIS_RUN}}
        time.sleep(0.5)
        for stage_name in STAGES_FOR_THIS_RUN:
            yield {"name": "stage.started", "data": {"stage": stage_name}}
            time.sleep(0.5)
            for i in range(random.randint(1, 3)):
                if random.random() > 0.3:
                    yield {"name": "log.info", "data": {"stage": stage_name, "message": f"Detail {i+1} for {stage_name.lower()}..."}}
                else:
                    yield {"name": "log.info", "data": {"stage": None, "message": f"Global info: System load is {random.randint(20, 50)}%"}}
                time.sleep(random.uniform(0.5, 1.0))
            if stage_name == "Deploying Application" and random.random() < 0.2:
                yield {"name": "stage.error", "data": {"stage": stage_name, "message": "Ansible connection timed out."}}
                yield {"name": "pipeline.failed", "data": {"message": "❌ Deployment failed."}}
                return
            yield {"name": "stage.success", "data": {"stage": stage_name}}
            time.sleep(0.5)
        yield {"name": "pipeline.succeeded", "data": {"message": "✅ Deployment successful!", "details": {"url": "https://my-app.fngen.run"}}}

    if False:
        # hack for dynamic call graph building
        simulate_stateful_event_stream()

    run_push_live_view(simulate_stateful_event_stream)
