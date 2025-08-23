# Satellite Flight Operational Procedures (FOPs) in Python

**Status:** Experimental  
This repository contains personal experiments exploring a practical, non-intrusive way to **write, debug, and run Satellite Flight Operational Procedures (FOPs)** using **plain Python**.

The aim is to validate that Python (integrated with a OSS IDE) can support common FOP activities in both development and operational contexts.
The integration must not be intrusive, avoiding any manipulation of the python interpreter and facilitating the evolution of the framework to new releases of python.

---

## Objectives

The experiments aim to **prove or discard** the viability of following features using a combination of OSS tools and custom developments:

1. **Domain specific functions** (e.g. Send, VerifyTM, ...) - Key mechanism for interacting programatically with TM&TC core and the building blocks for proc automation.
2. **Step-by-step execution** — critical for development and testing (e.g., with a simulator).
3. **Syntax highlighting** and **support for domain-specific directives**.
4. **Domain-specific exception handling** — e.g., catch a telecommand send failure and **prompt the operator** to decide how to continue (**cancel**, **skip**, **abort**).
5. **In-UI prompt handling** — respond to FOP prompts **without leaving the main UI**.
6. **Resume on crash** — continue a procedure from the last known safe point.
7. **Attach to a running procedure** — including ones started in the background or by another UI.
8. **Web UI** — for monitoring and control.
9. **Domain-specific displays** — e.g., command verification status, telemetry values.
10. **User Libraries** - extend domain specific functions with reusable pieces of code developed by the user

> Assumption: **VS Code** (or equivalent) is the primary interactive environment to develop and run FOPs.

---

## What’s Included

- **FOPs core** (tracing / retry / sinks) + **domain specific directives**
- A **VS Code extension** that raises prompts and returns operator responses to Python over HTTP
- A **Python integration** that asks the VS Code extension for input (retry decorator with console fallback)

---

## Repository Layout

```text
fops_core/                 # Core: tracing, retry logic, sinks
primitives/                # Domain primitives (e.g., SendTC, VerifyTM with decorators)
integrations/vscode/       # Python client + retry decorator using VS Code prompts
vscode-fops-prompter/      # VS Code extension (TypeScript)
fop.py                     # Example FOP script
```

---

## Quickstart

### VS Code development environment

1. Install the **Dev Containers** extension in VS Code.
2. Reopen the project in a Dev Container:  
   `F1` → **Dev-Containers: Reopen in Container**
3. Use the Python debugger to run **`fop.py`**.

> Tip: Dev Containers requires Docker (or a compatible backend) running on your machine.

### VS Code extension

- The extension is **built automatically** by the Dev Container, but **not installed**.
- After the container starts, a file like **`fops-prompter-x.y.z.vsix`** should appear in **`vscode-fops-prompter/`**.

**Install it:**

1. In `vscode-fops-prompter/`, right-click the `.vsix` → **Install**.
2. Open the prompter UI:  
   `F1` → **FOPs: Open Prompter**
3. **Keep this prompter window open** while running your Python FOPs.

---

## How It Works

Use either:

- the **console-based** retry decorator from `fops_core.retry`, or  
- the **VS Code–aware** retry decorator that first tries the extension prompt, then falls back to console input.

```python
from integrations.vscode.retry_vscode import retry_decorator_with_vscode_fallback

@retry_decorator_with_vscode_fallback
def SendTC(args):
    ...
```

**Behavior on exception:**

1. Attempt to prompt the operator via the **VS Code extension**.
2. If unavailable, **fall back to console** input.

---

## Configuration

### Extension port

- **Default:** `127.0.0.1:5533`
- **Change it in VS Code:** `Settings → FOPs Prompter: Port`
- **Update Python client:** set `EXT_PORT` in `integrations/vscode/prompt_client.py`

---

## Notes & Scope

- This is an **experiment** to assess feasibility and developer experience—**not** a production-ready system.
- The focus is on **interactivity** (prompts, retries, operator choices) and **developer ergonomics** within VS Code.

---

## License

[AGPL](LICENSE)
