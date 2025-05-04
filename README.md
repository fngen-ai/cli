# fngen

`fngen` ("eff-en-jen") is a deployment and hosting solution for Python. It aims to be the highest leverage way to build and deploy powerful solutions with Python.

To achieve this, `fngen` has a very opinionated focus: Python *functions* are the fundamental unit, activated via **Powers**.

To use `fngen`, there are 2 steps:

1.  Annotate your Python functions with your choice(s) from an ever-growing selection of **Powers** (like deploying web apps, running background tasks, generating web forms, or packaging libraries).
2.  Run `fngen push ~/path/to/your/code` to activate your functions according to their designated **Powers**.

Of course, there are other details, configuration, and Power-specific benefits/constraints, but the above 1-2 punch stands true for all. `fngen` handles the underlying infrastructure, deployment, or build processes based on the Power you choose.

### Hello world

Let’s say you want to deploy a simple FastAPI web app.

Here’s the vanilla version:

```python
# my_website.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get('/')
def my_fastapi_page():
    return HTMLResponse('<h1>FastAPI on fngen</h1>')
```

Now, here’s how you empower it with `fngen`:

```python
# my_website.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fngen.powers import webapp

app = FastAPI()

@app.get('/')
def my_fastapi_page():
    return HTMLResponse('<h1>FastAPI on fngen</h1>')

# fngen-specific addition
@webapp(framework='fastapi', compute='server')
def live_app():
    return app
```

Then:

```bash
fngen push my_website.py
```

💥 Boom — `fngen` provisions infrastructure, deploys your app, handles HTTPS, and gives you a public URL.

---

# Table of Contents
* [fngen](#fngen)
    * [Hello world](#hello-world)
* [Table of Contents](#table-of-contents)
* [Powers](#powers)
    * [@webapp(framework='...', compute='...')](#webappframework-compute)
      * [FastAPI Example](#fastapi-example)
      * [Flask Example](#flask-example)
      * [Django Example](#django-example)
    * [@task_worker(compute='...')](#task_workercompute)
    * [Config Overview + Roadmap](#config-overview-roadmap)
      * [@webapp Configuration Options](#webapp-configuration-options)
      * [@task_worker Configuration Options](#task_worker-configuration-options)
* [Projects](#projects)
* [Defining Your Deployment](#defining-your-deployment)
  * [Code structure and packaging](#code-structure-and-packaging)
    * [Simple File Structure](#simple-file-structure)
    * [Structure with requirements.txt](#structure-with-requirementstxt)
    * [Structure with multiple modules](#structure-with-multiple-modules)
    * [Structure with an inner Python package](#structure-with-an-inner-python-package)
    * [Structure including git-ignored assets](#structure-including-git-ignored-assets)
  * [requirements.txt](#requirementstxt)
  * [fngen.yml](#fngenyml)
    * [Defining Your Server Fleet](#defining-your-server-fleet)
    * [How compute='server' Powers Use Your Fleet](#how-computeserver-powers-use-your-fleet)
  * [.fninclude](#fninclude)
  * [.fnignore](#fnignore)
  * [Environment Variables](#environment-variables)
    * [Purpose](#purpose)
    * [Setting Environment Variables](#setting-environment-variables)
    * [Accessing Environment Variables in Your Code](#accessing-environment-variables-in-your-code)
* [Authentication and API Keys](#authentication-and-api-keys)
  * [Obtaining Your API Key](#obtaining-your-api-key)
  * [Configuring Authentication](#configuring-authentication)
  * [Verifying Your Authentication](#verifying-your-authentication)
* [Logging and Monitoring](#logging-and-monitoring)
  * [What Gets Logged?](#what-gets-logged)
  * [Accessing Logs via the CLI](#accessing-logs-via-the-cli)
  * [Using Python's logging Module](#using-pythons-logging-module)
  * [Future Monitoring Features](#future-monitoring-features)
* [fngen CLI](#fngen-cli)
  * [Authentication](#authentication)
  * [Commands](#commands)
    * [fngen connect](#fngen-connect)
    * [fngen create [project]](#fngen-create-project)
    * [fngen projects](#fngen-projects)
    * [fngen push [project] [path/to/code_dir]](#fngen-push-project-pathtocode_dir)
    * [fngen run_task [project] 'function_name' 'payload_json'](#fngen-run_task-project-function_name-payload_json)
    * [fngen set_env [project] [path/to/.env]](#fngen-set_env-project-pathtoenv)
    * [fngen logs [project]](#fngen-logs-project)
    * [fngen destroy [project]](#fngen-destroy-project)
* [Pricing](#pricing)
    * [Server Pricing](#server-pricing)
    * [What's Included / No Extra Cost](#whats-included-no-extra-cost)
* [FAQ](#faq)
    * [Why Python?](#why-python)
    * [Why Python functions specifically?](#why-python-functions-specifically)
    * [Functional Infra: The Power of Purpose-Built Infrastructure](#functional-infra-the-power-of-purpose-built-infrastructure)
* [TL;DR](#tldr)
* [Roadmap](#roadmap)
  * [General Roadmap & Future Enhancements](#general-roadmap-future-enhancements)
    * [Planned Powers (Coming Soon)](#planned-powers-coming-soon)

---

# Powers

`fngen` activates your Python functions using **Powers**. Each Power tells `fngen` what to *do* with your function — deploy it as a web app, run it on a schedule, generate a UI for it, and more.

---

### `@webapp(framework='...', compute='...')`

*   **Purpose:** Deploys your Python web application using your framework of choice.
*   **Framework options:** `'fastapi'`, `'flask'`, `'django'`
*   **Compute options:** `'server'` (always-on server), `'serverless'` (event-driven, scale-to-zero, coming soon)
*   **How it Works:** `fngen` provisions appropriate infrastructure (server or serverless) depending on your choice. It expects the decorated function to return a web app instance appropriate for the framework (e.g., FastAPI, Flask, Django `ASGI/WSGI` app).

*   **Function Signature:** Must return an app instance appropriate to the framework.

---

#### FastAPI Example

```python
# fastapi_app.py
from fastapi import FastAPI
from fngen.powers import webapp

app = FastAPI()

@app.get("/ping")
def ping():
    return {"ping": "pong"}

@webapp(framework='fastapi', compute='server')
def serve_fastapi():
    return app

# Run: fngen push fastapi_app.py
```

---

#### Flask Example

```python
# flask_app.py
from flask import Flask
from fngen.powers import webapp

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Flask on fngen!"

@webapp(framework='flask', compute='server')
def serve_flask():
    return app

# Run: fngen push flask_app.py
```

---

#### Django Example

```python
# myproject/asgi.py
import os
from django.core.asgi import get_asgi_application
from fngen.powers import webapp

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
application = get_asgi_application()

@webapp(framework='django', compute='server')
def serve_django():
    return application

# Run: fngen push myproject/asgi.py
```

---

### `@task_worker(compute='...')`

**Purpose:**
Deploys a function to process background jobs or tasks asynchronously.

**Compute options:**
- `'server'` (always-on worker server)
- `'serverless'` (event-driven worker, scale-to-zero, coming soon)

**How it Works:**
`fngen` provisions the necessary infrastructure to receive and execute jobs. You can dispatch tasks to the worker by sending payloads, and the function processes them in the background.

**Function Signature:**
The function can accept **any number of parameters** with **any Python type annotations** (`str`, `int`, `dict`, `float`, custom classes, etc.).
`fngen` will **smartly route incoming task data to your function**, matching types and handling deserialization.

**Example:**

```python
from fngen.powers import task_worker

@task_worker(compute='server')
def process_order(order_id: int, customer_email: str, items: list[dict]):
    """
    Processes an order by ID, customer email, and a list of purchased items.
    """
    print(f"Processing order {order_id} for {customer_email}")
    print(f"Items: {items}")
```

Dispatch a task via the fngen SDK:

```python
from fngen import platform

platform.run_task('your_project', 'hello_world', {'name': 'Aang'})
```

or via the fngen CLI:
```bash
fngen run_task your_project hello_world '{"name": "Aang"}'
```

<!-- ---

### `@web_form()`

*   **Purpose:** Automatically generates a simple web form UI from your function.
*   **How it Works:** `fngen` inspects your function’s signature (arguments, type hints, docstrings) and generates an HTML form. Submissions call your function with the provided input.
*   **Function Signature:** Standard Python function.

*Example:*

```python
from fngen.powers import web_form

@web_form()
def add_user(name: str, age: int, is_active: bool = True):
    """
    Add a user. Active users will be immediately available.
    """
    print(f"Adding {name}, {age} years old, Active={is_active}")
    return {"status": "added"}
``` -->

<!-- ---

### `@scheduled_task()`

*   **Purpose:** Runs your function automatically on a recurring schedule (like a cron job).
*   **How it Works:** You configure the schedule via `fngen.yaml` (using cron syntax). `fngen` executes your function on schedule.
*   **Function Signature:** Standard Python function, typically taking no arguments.

*Example:*

```python
from fngen.powers import scheduled_task
import datetime

@scheduled_task()
def daily_job():
    print(f"Running job at {datetime.datetime.now()}!")
```

In `fngen.yaml`:

```yaml
schedule: "0 2 * * *"  # Runs daily at 2:00 AM UTC
``` -->

---

### Config Overview + Roadmap
#### `@webapp` Configuration Options

Deploys your Python web application.

| Option    | Value     | Status      | Description                                                                    |
| :-------- | :-------- | :---------- | :----------------------------------------------------------------------------- |
| `framework` | `'fastapi'` | Supported   | Deploy an application built with FastAPI.                                      |
| `framework` | `'flask'`   | Coming Soon   | Deploy an application built with Flask.                                        |
| `framework` | `'django'`  | Coming Soon   | Deploy an application built with Django (ASGI/WSGI).                           |
| `compute`   | `'server'`  | Supported   | Deploys to always-on server instance(s) defined in `fngen.yml`.              |
| `compute`   | `'serverless'`| Coming Soon | Deploys to event-driven infrastructure that scales to zero when idle.          |

---

#### `@task_worker` Configuration Options

Deploys a function to process background jobs or tasks asynchronously.

| Option    | Value       | Status      | Description                                                                    |
| :-------- | :---------- | :---------- | :----------------------------------------------------------------------------- |
| `compute`   | `'server'`    | Supported   | Deploys to always-on worker server instance(s) defined in `fngen.yml`.       |
| `compute`   | `'serverless'`| Coming Soon | Deploys to event-driven worker infrastructure that scales to zero when idle. |

---

# Projects

Your deployments, code, packages, etc. are organized into Projects.

You can create a project with the following command:

```bash
fngen create your_project
```

List all projects in your account:
```bash
fngen projects
```

---

# Defining Your Deployment

When you run `fngen push`, `fngen` packages your code and relevant configuration files. These files help define dependencies, infrastructure resources, and exactly which files are included or excluded.

## Code structure and packaging

When you run `fngen push [path/to/code_dir]`, the specified directory becomes your deployment package. `fngen` will package and upload the contents of this directory to the platform for building and deployment.

By default, `fngen` includes all files and subdirectories within the package directory, with specific rules for inclusion and exclusion defined by `.gitignore`, `.fnignore`, and `.fninclude` files (explained in detail below).

During the deployment process, `fngen` scans all `.py` files within your package to discover functions decorated with `fngen.powers` decorators.

The essential files for a basic deployment are your Python code and a `fngen.yml` file defining your project resources. Note: `fngen.yml` must be located at the root of your deployment package directory.

Below are some common example directory structures for a deployment package.

### Simple File Structure
Here's a minimal structure with a single Python file containing your code, and a `fngen.yml` file defining your resources.
```bash
.
├── hello.py
└── fngen.yml
```

### Structure with requirements.txt
In most cases, you'll need third-party Python packages. Simply include a `requirements.txt` file at the root of your package, and `fngen` will automatically install the dependencies during the deployment build process.
```bash
.
├── requirements.txt
├── hello.py
└── fngen.yml
```

### Structure with multiple modules
You are not confined to a single Python module. You can organize your code across as many `.py` files as needed. fngen will scan all of them for decorated functions.
```bash
.
├── requirements.txt
├── hello.py
├── llm.py
├── run_analysis.py
└── fngen.yml
```

### Structure with an inner Python package
It's common practice to organize larger codebases into Python packages using subdirectories with an `__init__.py` file. This standard structure is fully supported.
```bash
.
├── my_project
│   ├── __init__.py
│   ├── annotate_video.py
│   └── recommend_videos.py
├── requirements.txt
└── fngen.yml
```

### Structure including git-ignored assets
It's good practice to exclude large 'assets' (like data files, videos, images) from your version control (Git) repository using `.gitignore`. However, you will often want to include these in your deployment package. You can achieve this by adding entries to a `.fninclude` file at the root of your package. fngen respects `.gitignore` for exclusions but prioritizes `.fninclude` for inclusions. You can also use `.fnignore` for explicit exclusions (see [`.fnignore`](#.fnignore) and [`.fninclude`](#.fninclude) sections for details).
```bash
.
├── .gitignore
├── .fninclude
├── assets
│   ├── big_video.mp4
│   └── gorilla.png
├── my_project
│   ├── __init__.py
│   ├── annotate_video.py
│   └── recommend_videos.py
├── requirements.txt
└── fngen.yml
```

## requirements.txt

If your code includes a `requirements.txt` file, `fngen` will **automatically install dependencies** for each run mode.

Under the hood, it simply runs:

```bash
pip install -r requirements.txt
```

before setting up the deployment or runtime environment.

You don't need to do anything special — just make sure your dependencies are correctly listed in your `requirements.txt`.

> ✅ *Best practice:* Always commit your `requirements.txt` alongside your code.

---

## fngen.yml

Your `fngen.yml` file, placed at the root of your project directory, is where you define project-level configuration and the infrastructure **Resources** required by your `fngen` Powers.

Currently, `fngen.yml` is primarily used to define configurations for **server** compute resources. Support for configuring serverless resources will be added in the future.

### Defining Your Server Fleet

Powers that require persistent, always-on compute, such as `@webapp(compute='server')` or `@task_worker(compute='server')`, rely on server resources defined in your `fngen.yml` under the `servers:` key.

You define the composition of your server **fleet** by listing one or more server configurations using `name`, `size`, and `region`. `fngen` will provision a fleet of server instances based on these definitions. For detailed pricing information on server sizes, please refer to the [Pricing](#pricing) section.

**Example:**

```yaml
# fngen.yml
servers:
  - name: web-server-class # Required: A unique name for this server definition within your project. Used for identification in the config.
    size: s              # Required: The server type tier. Choose one from the table below (see Pricing section).
    region: us-west      # Required: The geographic region for deployment (e.g., us-west, us-east, eu-central).
# You can define multiple server types to include in your fleet:
  - name: worker-server-class
    size: xl
    region: us-west
```
*Explanation:* In this example, you are defining a server fleet that will include server instances of size `s` located in `us-west` and server instances of size `xl` also in `us-west`. The `name` field (`web-server-class`, `worker-server-class`) is purely for identifying these different definitions within your `fngen.yml`.

### How `compute='server'` Powers Use Your Fleet

When you deploy your project with `fngen push`, any function decorated with a Power using `compute='server'` (like `@webapp` or `@task_worker`) will be deployed to **every single server instance** within the fleet you defined in `fngen.yml`.

*   **Horizontal Scaling:** Your entire application code is replicated across all provisioned servers.
*   **Automatic Load Balancing:** For `@webapp` functions, `fngen` automatically sets up and manages a load balancer to distribute incoming web traffic across all web servers in your fleet.
*   **Shared Fleet:** `@webapp` and `@task_worker` functions using `compute='server'` share the *same* server fleet. Your web app runs on the same instances as your task workers.

By defining multiple server configurations (e.g., one `s` and one `xl`), you create a heterogeneous fleet, and your `compute='server'` workloads will run on instances of *both* types.

*(Future: This file may include configurations for `serverless` compute or other `fngen`-managed resources.)*


## .fninclude

Use .fninclude to include .gitignore'd files in your deployment package when you run `fngen push`.

Typically, you don't want to include certain resources in your git repo, but you do want to include them in your deployment package.

## .fnignore

Use .fnignore to ignore files from being included in your deployment package when you run `fngen push`.

Uses .gitignore syntax.

Note: `fngen push` also respects your .gitignore; .fnignore is used to ignore stuff that you may want to include in your git repo. (This is rare, but it can happen).

## Environment Variables

Managing application configuration, secrets, and credentials securely is essential. `fngen` provides a built-in mechanism for managing environment variables for your projects.

### Purpose

Environment variables are key-value pairs injected into the runtime environment where your functions are executed. They are commonly used for:

*   Database connection strings
*   API keys for third-party services
*   Configuration flags (e.g., `DEBUG=True`)
*   Sensitive information that should not be hardcoded or committed to version control.

### Setting Environment Variables

You can upload environment variables to your fngen project using the `fngen set_env` command. This command reads variables from a standard `.env` file.

1.  **Create a `.env` file:** In your project directory (or any location), create a file named `.env` (or any name you prefer). Add your variables using the `KEY=VALUE` format, one per line:

    ```dotenv
    DATABASE_URL=postgres://user:password@host:port/database
    STRIPE_SECRET_KEY=sk_live_...
    API_TIMEOUT_SECONDS=30
    ```

    > **Important:** Do **not** commit your `.env` file containing secrets to your version control system (like Git). Add it to your `.gitignore` file.

2.  **Upload with the CLI:** Use the `set_env` command, specifying your project name and the path to your `.env` file.

    ```bash
    fngen set_env my-project .env
    ```

This command securely uploads the variables to the fngen platform. They are encrypted at rest and injected into the runtime environment of your project's deployed functions. Uploading a variable with the same key will overwrite its existing value.

### Accessing Environment Variables in Your Code

Inside any function deployed with a `fngen` Power, you can access environment variables using Python's standard `os` module:

```python
import os

from fngen.powers import webapp

@webapp(framework='fastapi', compute='server')
def my_app_with_env():
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/secret")
    def get_secret():
        # Accessing an environment variable
        # Updated environment variable prefix
        secret_key = os.environ.get("MY_SUPER_SECRET")
        if not secret_key:
            return {"error": "MY_SUPER_SECRET not set"}, 500
        return {"secret": secret_key}

    return app

# You would set MY_SUPER_SECRET using `fngen set_env my-project .env`
# where .env contains: MY_SUPER_SECRET=its_a_secret!
```

Environment variables are available to all functions within a project, regardless of the Power used.

---

# Authentication and API Keys

To interact with the fngen platform and deploy your code, you need to authenticate your fngen CLI and SDK using an API key. Your API key links your local tools to your fngen account and projects.

## Obtaining Your API Key

Your API key is generated within your fngen account dashboard (details on accessing the dashboard will be provided separately). Treat your API key like a password – keep it secure and do not share it publicly.

## Configuring Authentication

You can configure your API key for the `fngen` CLI and SDK in two primary ways:

1.  **Configuration File (Recommended):**
    *   Create a directory named `.fngen` in your user's home directory (`~/.fngen/`).
    *   Inside this directory, create a file named `credentials.yml`.
    *   Add your API key to this file in the following format:

        ```yaml
        api_key: your_fngen_api_key_here
        ```
    *   Make sure this file has restricted permissions (`chmod 600 ~/.fngen/credentials.yml`) to protect your API key.

2.  **Environment Variable:**
    *   Set the `FNGEN_API_KEY` environment variable in your terminal session or shell profile.

        ```bash
        export FNGEN_API_KEY=your_fngen_api_key_here
        ```
    *   This method is often used in CI/CD pipelines or temporary setups. Note that environment variables can sometimes be less secure than a properly permissioned configuration file.

The `fngen` CLI and SDK will check for the environment variable first, and if not found, will look for the `credentials.yml` file.

## Verifying Your Authentication

Use the `fngen connect` command to verify that your authentication is set up correctly and you can connect to the fngen platform.

```bash
fngen connect
```

If successful, this command will confirm your connection and display the email address associated with your account.


---

# Logging and Monitoring

Observability is key to understanding the behavior of your deployed applications and tasks, diagnosing issues, and monitoring performance. `fngen` provides integrated logging capabilities for all your deployed functions.

## What Gets Logged?

fngen captures standard output (`stdout`) and standard error (`stderr`) from your Python functions. This means any `print()` statements or output from standard Python logging libraries (like `logging`) within your decorated functions will be automatically collected and made available through the fngen platform.

Additionally, fngen platform events related to your project (deployments, task dispatches, scaling events, errors) are also included in the logging stream.

## Accessing Logs via the CLI

The primary way to access logs is using the `fngen logs` command.

```bash
fngen logs [project_name] [options]
```

As detailed in the [CLI section](#fngen-logs-project), this command allows you to view recent logs, follow logs in real-time, and filter by Power, function, task ID, time range, or log level.

**Examples:**

*   View the last 100 lines of logs for your project:
    ```bash
    fngen logs my-project
    ```

*   Stream logs in real-time:
    ```bash
    fngen logs my-project --follow
    ```

*   Filter logs for a specific task worker function:
    ```bash
    fngen logs my-project --power task_worker --function process_order
    ```

*   View logs for a specific web request (details on how to find request IDs coming soon):
    ```bash
    fngen logs my-project --request-id abcdef123456
    ```

*   See errors from the last hour:
    ```bash
    fngen logs my-project --level ERROR --since 1h
    ```

## Using Python's `logging` Module

While `print()` works fine for simple output, using Python's built-in `logging` module provides more structure, severity levels, and context for your logs. fngen fully supports this.

```python
import logging
from fngen.powers import task_worker

# Configure basic logging (optional, but good practice)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task_worker(compute='server')
def process_data(data_payload: dict):
    """
    Processes data received via a task.
    """
    try:
        logger.info(f"Received data payload: {data_payload}")
        # ... processing logic ...
        logger.info("Data processing successful")
        # You can log at different levels:
        # logger.warning("Something unusual happened")
        # logger.error("An error occurred during processing")
    except Exception as e:
        logger.exception(f"Error processing data: {e}") # Logs error and traceback
        raise # Re-raise the exception if needed
```

Logs generated using `logging.info()`, `logging.error()`, etc., will appear in the `fngen logs` output with their respective severity levels.

## Future Monitoring Features

While basic logging is available now, future versions of fngen will include more advanced monitoring features such as:

*   Metrics (request latency, error rates, task queue depth)
*   Distributed tracing
*   Enhanced log searching and filtering in a web dashboard

---

# `fngen` CLI

The fngen Command Line Interface (CLI) is your primary tool for interacting with the fngen platform, managing your projects, and deploying your code.

Ensure you have the fngen CLI installed and configured with your API key before proceeding.

```bash
pip install fngen # Update pip install command
```

## Authentication

The CLI requires authentication to interact with your fngen account. You can configure your credentials in `~/.fngen/credentials.yml` or by setting the `FNGEN_API_KEY` environment variable.

Use the `connect` command to verify your setup.

## Commands

Here are the most commonly used fngen CLI commands:

### `fngen connect`

*   **Purpose:** Verify your authentication credentials and connectivity to the fngen platform.
*   **Usage:**
    ```bash
    fngen connect
    ```
*   **Details:** Checks if your API key (from `~/.fngen/credentials.yml` or `FNGEN_API_KEY`) is valid. If successful, it will return the email address associated with the authenticated account.
*   **Example:**
    ```bash
    fngen connect
    # Output: ✅  Connected [user@example.com]
    ```

### `fngen create [project]`

*   **Purpose:** Create a new fngen project in your account.
*   **Usage:**
    ```bash
    fngen create [project_name]
    ```
*   **Details:** Project names must be unique across your fngen account. Creating a project sets up the necessary infrastructure scaffolding on the platform side.
*   **Example:**
    ```bash
    fngen create my-new-project
    ```

### `fngen projects`

*   **Purpose:** List all fngen projects associated with your account.
*   **Usage:**
    ```bash
    fngen projects
    ```
*   **Details:** Displays a list of your project names.
*   **Example:**
    ```bash
    fngen projects
    # Output:
    # my-new-project
    # another-app
    # marketing-site
    ```

### `fngen push [project] [path/to/code_dir]`

*   **Purpose:** Package and deploy your Python code to a specific project.
*   **Usage:**
    ```bash
    fngen push [project_name] [path/to/code_directory]
    ```
*   **Details:** This command is the core deployment action.
    *   It reads your project configuration (`fngen.yml`), dependencies (`requirements.txt`), and inclusion/exclusion rules (`.gitignore`, `.fnignore`, `.fninclude`).
    *   It packages your code directory.
    *   It uploads the package to the fngen platform.
    *   fngen then builds the necessary environment and deploys your functions according to their defined **Powers**.
    *   If `[path/to/code_directory]` is omitted, it defaults to the current directory (`.`).
*   **Example:**
    ```bash
    # Deploy code from the current directory to 'my-website' project
    fngen push my-website .

    # Deploy code from a specific path to 'another-app' project
    fngen push another-app /home/user/code/another_app
    ```

### `fngen run_task [project] 'function_name' 'payload_json'`

*   **Purpose:** Dispatch a new job execution for a function decorated with `@task_worker`.
*   **Usage:**
    ```bash
    fngen run_task [project_name] 'your_function_name' '{"arg1": "value", "arg2": 123, ...}'
    ```
*   **Details:** The `function_name` must correspond to a function decorated with `@task_worker` in your deployed code. The `payload_json` must be a valid JSON string that maps to the parameters expected by your task worker function.
*   **Example:** (Using the `process_order` example function)
    ```bash
    fngen run_task my-project 'process_order' '{"order_id": 101, "customer_email": "test@example.com", "items": [{"item_id": 5, "qty": 1}]}'
    ```

### `fngen set_env [project] [path/to/.env]`

*   **Purpose:** Securely upload environment variables from a `.env` file to your project.
*   **Usage:**
    ```bash
    fngen set_env [project_name] [path/to/.env_file]
    ```
*   **Details:** Reads key-value pairs from the specified `.env` file (standard format: `KEY=VALUE`). These variables are securely stored on the platform and automatically injected into the runtime environment whenever your project's functions are executed (web requests, tasks, etc.). Existing variables with the same name will be overwritten.
*   **Example:**
    ```bash
    fngen set_env my-project .env
    ```

### `fngen logs [project]`

*   **Purpose:** View logs generated by your deployed functions and the fngen platform for your project.
*   **Usage:**
    ```bash
    fngen logs [project_name] [options]
    ```
*   **Details:** Accesses the centralized logging stream for your project. Useful for debugging, monitoring, and seeing the output of your `print()` statements or logging calls. If `[project_name]` is omitted when run inside a project directory, it defaults to the current project.
*   **Options:**
    *   `--follow`, `-f`: Stream new logs in real-time (like `tail -f`).
    *   `--power [power_name]`: Filter logs to show only those originating from a specific Power (e.g., `webapp`, `task_worker`).
    *   `--function [function_name]`: Filter logs to show only those originating from a specific decorated function name.
    *   `--task-id [task_id]`: Filter logs to show only those associated with a specific task worker job execution ID.
    *   `--since [duration]`: Show logs since a specific time duration (e.g., `10m`, `1h`, `24h`).
    *   `--level [level]`: Filter logs by severity level (e.g., `INFO`, `WARNING`, `ERROR`).
*   **Examples:**
    ```bash
    # Show recent logs for the current project
    fngen logs

    # Follow logs for 'my-website' project
    fngen logs my-website --follow

    # Show logs from webapp functions in the last 30 minutes
    fngen logs my-website --power webapp --since 30m

    # View logs specifically for a failed task
    fngen logs my-project --task-id abc123xyz
    ```

### `fngen destroy [project]`

*   **Purpose:** Permanently delete a project and all associated resources (servers, data, configurations, logs).
*   **Usage:**
    ```bash
    fngen destroy [project_name]
    ```
*   **Details:** This is a **destructive** and irreversible action. You will typically be prompted to confirm before deletion proceeds. Use with caution.
*   **Example:**
    ```bash
    fngen destroy my-old-project
    ```

*(Future: Mention `fngen --help` and `fngen [command] --help` for more detailed CLI help).*

---

# Pricing

fngen pricing is based on the server resources you provision and utilize for your applications and tasks. We aim for simple, predictable costs.

### Server Pricing

When you use `compute='server'` for your `webapp` or `task_worker` Powers, you define a fleet of servers in your `fngen.yml` file based on size and region. You are charged based on the size and duration of these server instances.

The table below shows the available server types, their specifications, and estimated monthly pricing per instance.

| Server Type (`size`) | vCPU | RAM    | Disk   | Transfer | Est. Cost (USD/mo) |
| :------------------- | :--- | :----- | :----- | :------- | :----------------- |
| `xs` | 1    | 0.5 GB | 10 GB  | 0.5 TB   | ~$4                |
| `s`                  | 1    | 1 GB   | 25 GB  | 1 TB     | ~$6                |
| `m`                  | 1    | 2 GB   | 50 GB  | 2 TB     | ~$12               |
| `l`                  | 2    | 2 GB   | 60 GB  | 3 TB     | ~$18               |
| `xl`                 | 2    | 4 GB   | 80 GB  | 4 TB     | ~$24               |
| `2xl`     | 4    | 8 GB   | 160 GB | 5 TB     | ~$48               |
| `3xl`    | 8    | 16 GB  | 320 GB | 6 TB     | ~$96               |

*(Pricing for serverless compute and other future resource types will be added here.)*

### What's Included / No Extra Cost

fngen abstracts away significant infrastructure complexity and management overhead. The following are included as part of the platform fee covered by your server instance costs:

*   **Infrastructure Provisioning:** Setting up servers, networking, etc.
*   **Deployment Pipeline:** Building, packaging, and deploying your code.
*   **Automatic HTTPS:** SSL certificate management and renewal for web applications.
*   **Load Balancing:** Distributing traffic across your `webapp` server fleet.
*   **Task Queuing Infrastructure:** The messaging and queuing system for `@task_worker`.
*   **Basic Monitoring & Logging Access:** Tools to observe your applications (detailed sections on these coming soon).
*   **Bandwidth:** Includes the specified data transfer per server size tier.

You only pay for the server instances you define in your `fngen.yml` or the usage of future metered resources like serverless functions.

---

# FAQ

### Why Python?

There's a great saying that goes:
> "python isn't the best language for anything, but it's the second best language for everything"

So, when building a platform focused on delivering powerful, high-leverage solutions with code, it seems like the best all-purpose language to focus on.

Plus, we just love Python.

P.S., Need other tools? You can often integrate them via a standard Python interface within your `fngen`-activated functions.

---

### Why Python *functions* specifically?

Python functions serve as a versatile and well-defined unit for specifying discrete pieces of logic. By centering `fngen` around functions, we provide a simple, consistent contract for activating various **Powers**. This approach promotes modularity, testability, and allows `fngen` to generate the appropriate execution environment and infrastructure tailored precisely to that function's defined role.

---

### Functional Infra: The Power of Purpose-Built Infrastructure

Building and deploying powerful applications requires more than just writing code. It requires supporting infrastructure – things like servers, networks, load balancers, message queues, and more. Traditionally, setting up and managing this infrastructure has been a complex and time-consuming task for developers.

`fngen` introduces the concept of **Functional Infra**. This refers to the **minimum, pre-packaged infrastructure** automatically provisioned and managed by `fngen` specifically to support a certain Python function and its designated **Power**.

Think of each Power as a blueprint for a specific type of application function, and Functional Infra as the engine and support system needed to make that blueprint a reality in a production environment.

Here are some examples of how Functional Infra pairs with `fngen` Powers:

*   When you use the `@webapp()` Power, `fngen` provisions the **Functional Infra for Web Applications**. This typically includes:
    *   Server instance(s) to run your application code (`compute='server'`).
    *   A load balancer to distribute incoming web traffic across your servers.
    *   Managed DNS and automatic HTTPS/SSL certificates.
    *   Necessary networking and security configurations.
    *   *(For `compute='serverless'` coming soon: Event triggers, scaling configurations, potentially API gateways)*

*   When you use the `@task_worker()` Power, `fngen` provisions the **Functional Infra for Background Tasks**. This typically includes:
    *   A managed message queue to receive and hold incoming task payloads.
    *   Server instance(s) to run your worker function (`compute='server'`).
    *   A management API and routing layer to dispatch payloads to your worker function instances.
    *   *(For `compute='serverless'` coming soon: Event triggers, scaling configurations based on queue depth)*

*   When you use the `@web_form()` Power, `fngen` provisions the **Functional Infra for Interactive Functions**. This typically includes:
    *   A simple web server to host the automatically generated HTML form.
    *   An endpoint to receive form submissions.
    *   The necessary routing to call your Python function with the submitted data.

**The Value of Functional Infra:**

By providing Functional Infra, `fngen` significantly reduces the operational burden on developers. You don't need to become an infrastructure expert to deploy a web app or set up a task queue. You simply define what your function *is* meant to do using a Power, and `fngen` handles provisioning, configuring, and managing the underlying infrastructure required for that purpose.

This allows you to:

*   **Move Faster:** Deploy production-ready features in minutes, not hours or days.
*   **Reduce Complexity:** Avoid managing servers, networking rules, load balancers, and queues yourself.
*   **Focus on Code:** Spend more time writing the Python logic that delivers value, rather than wrangling infrastructure.

As `fngen` grows, we will continue to introduce new Powers, each bringing its own flavor of purpose-built Functional Infra to support a wider range of Python use cases – all while maintaining the simple, function-centric "annotate and push" workflow.

---

# TL;DR

1.  Write a Python function.
2.  Give it a **Power** (decorate it).
3.  `fngen push` it.

`fngen` handles the rest.

---

# Roadmap

This section outlines the current capabilities of `fngen` and provides a look ahead at planned features and enhancements.

## General Roadmap & Future Enhancements

The following areas represent ongoing development and future additions to the `fngen` platform and documentation:

*   **Web Dashboard:** Development of a comprehensive web-based dashboard for project management, log viewing, monitoring, and configuration.
*   **Advanced Monitoring:** Expanding beyond basic logging to include metrics (e.g., request latency, error rates, queue depth), distributed tracing, and enhanced visualization in the dashboard.
*   **CI/CD Integration:** Providing more detailed guidance, examples, and potentially specific features to streamline integration into Continuous Integration and Continuous Deployment pipelines.
*   **Custom Build Environment:** Exploring ways for users to define custom environments, such as specifying OS-level dependencies or providing custom build scripts, for more complex project requirements.
*   **Enhanced Error Handling & Debugging:** Tools and features to make identifying and diagnosing runtime errors easier.
*   **Notifications:** Configuring alerts based on application logs or metrics (e.g., error rate spikes, high latency).
*   **Database & Service Integrations:** Potentially offering managed data services or simplified connections to external databases/services.
*   **Expanded Documentation:** Continuously improving clarity, adding more examples, tutorials, and addressing common use cases.

### Planned Powers (Coming Soon)

These Powers are planned for future releases:

*   **`@web_form()`:** Automatically generate a simple web form UI from your function signature.
*   **`@scheduled_task()`:** Run your function automatically on a recurring schedule (like a cron job).
*   *(Potential future powers for packaging, CLI tools, UI generation, etc.)*

We are actively working on expanding the capabilities of `fngen` to cover a wider range of Python application patterns. Stay tuned for updates!