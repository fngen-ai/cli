from rich.console import Console, Group
from rich.text import Text
import random
import time
from rich.live import Live
from rich.table import Table
from fngen.cli_util import print_error, help_option, profile_option, console

from fngen.api_key_manager import NoAPIKeyError, get_api_key

from fngen.network import GET, POST

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
                           'name': project_name,
                           'archive_type': 'zip'
                       }, profile=profile)

            console.print(f"{res}")

            url = res['presigned_url']
            fields = res['presigned_fields']
            package_id = res['package_id']

            print(f'package_id: {package_id}')

            archive_path = packaging.package_source(
                source_root_path, archive_format='zip')

            print(f'archive_path: {archive_path}')

            __upload_file_with_redirect_handling(url, fields, archive_path)

            res = POST('/api/project/deploy_package', {
                'package_id': package_id
            }, profile=profile)

            console.print(f"{res}")
        except NoAPIKeyError:
            console.print(
                "No API key found. Please run `fngen login` to set up your API key.")
    except Exception as e:
        print_error(e)


def __upload_file_with_redirect_handling(url, fields, file_path):
    max_retries = 3  # Number of retries
    for attempt in range(max_retries):
        try:
            # Open the file to upload
            with open(file_path, 'rb') as file:
                logger.debug(f'[start] POST: {url}')
                response = requests.post(
                    url,
                    data=fields,
                    files={'file': (fields['key'], file)},
                    allow_redirects=False,  # Disable automatic redirect handling
                )
                logger.debug(f'[response] POST: {url} | {response}')

            # Check if a redirect is needed
            if response.status_code in [301, 302]:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    logger.debug(f"Redirecting to: {redirect_url}")

                    # Retry the upload at the new endpoint
                    url = redirect_url
                    continue
                else:
                    raise ValueError(
                        'Redirect location not provided in response')
            else:
                # If no redirect is needed or request is successful, break the loop
                response.raise_for_status()
                return response

        except requests.RequestException as e:
            logger.debug(f"Error during upload: {str(e)}")

            if attempt < max_retries - 1:
                logger.debug("Retrying...")
            else:
                logger.debug("Max retries exceeded")
                raise  # Re-raise the exception if max retries exceeded


# --- The UI State Management and Rendering Logic ---

def update_view_state(state: dict, event: dict):
    """
    Processes an event and MUTATES the state dictionary in place.
    This is a common pattern in functional-style UI updates.
    """
    event_type = event.get("type")
    data = event.get("data", {})
    stage = data.get("stage")

    if event_type == "pipeline.initialized":
        state["pipeline_stages"] = data.get("stages", [])
        state["stage_statuses"] = {s: ("pending", "")
                                   for s in state["pipeline_stages"]}
    elif event_type == "stage.started":
        if stage in state["stage_statuses"]:
            state["stage_statuses"][stage] = ("running", "")
    elif event_type == "stage.success":
        if stage in state["stage_statuses"]:
            state["stage_statuses"][stage] = ("success", "")
    elif event_type == "stage.failed":
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


def run_push_live_view(_event_stream):
    """Simulates a deployment with a live-updating status view (functional approach)."""
    view_state = {"pipeline_stages": [],
                  "stage_statuses": {}, "global_logs": []}
    final_event = {}

    with Live(render_view(view_state), console=console, auto_refresh=False, vertical_overflow="visible") as live:
        for event in _event_stream():
            # The update function now mutates the state dict directly.
            update_view_state(view_state, event)
            live.update(render_view(view_state), refresh=True)

            if event.get("type") in ("pipeline.succeeded", "pipeline.failed"):
                final_event = event
                break

    final_data = final_event.get("data", {})
    console.print(
        f"\n[bold]{final_data.get('message', 'Deployment finished.')}[/bold]")
    if url := final_data.get("details", {}).get("url"):
        console.print(f"🚀 Your app is live at: [link={url}]{url}[/link]")


def simulate_push(project_name: str = typer.Argument("my-cool-project")):
    """Simulates a deployment with a live-updating status view (functional approach)."""
    STAGES_FOR_THIS_RUN = ["Parsing Project", "Provisioning Infrastructure",
                           "Deploying Application", "Confirming Health", ]

    def simulate_stateful_event_stream():
        yield {"type": "pipeline.initialized", "data": {"stages": STAGES_FOR_THIS_RUN}}
        time.sleep(0.5)
        for stage_name in STAGES_FOR_THIS_RUN:
            yield {"type": "stage.started", "data": {"stage": stage_name}}
            time.sleep(0.5)
            for i in range(random.randint(1, 3)):
                if random.random() > 0.3:
                    yield {"type": "log.info", "data": {"stage": stage_name, "message": f"Detail {i+1} for {stage_name.lower()}..."}}
                else:
                    yield {"type": "log.info", "data": {"stage": None, "message": f"Global info: System load is {random.randint(20, 50)}%"}}
                time.sleep(random.uniform(0.5, 1.0))
            if stage_name == "Deploying Application" and random.random() < 0.2:
                yield {"type": "stage.failed", "data": {"stage": stage_name, "message": "Ansible connection timed out."}}
                yield {"type": "pipeline.failed", "data": {"message": "❌ Deployment failed."}}
                return
            yield {"type": "stage.success", "data": {"stage": stage_name}}
            time.sleep(0.5)
        yield {"type": "pipeline.succeeded", "data": {"message": "✅ Deployment successful!", "details": {"url": "https://my-app.fngen.run"}}}

    if False:
        # hack for dynamic call graph building
        simulate_stateful_event_stream()

    run_push_live_view(simulate_stateful_event_stream)
