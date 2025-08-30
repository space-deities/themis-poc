# Satellite Flight Operational Procedures (FOPs) in Python

**Status:** Experimental  
This repository contains personal experiments exploring a practical, non-intrusive way to **write, debug, and run Satellite Flight Operational Procedures (FOPs)** using **plain Python**.

Space deity code name: **Themis**

The aim is to validate that Python (integrated with a OSS IDE) can support common FOP activities in both development and operational contexts.
The integration must not be intrusive, avoiding any manipulation of the python interpreter and facilitating the evolution of the framework to new releases of python.

---

## Objectives

The experiments aim to **prove or discard** the viability of following features using a combination of OSS tools and custom developments:

1. **Domain specific functions** (e.g. Send, VerifyTM, ...) - Key mechanism for interacting programmatically with TM&TC core and the building blocks for proc automation.
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

- **Themis Core**: A python library implementing themis domain specific directives (Themis Lang), plus helpers for parsing arguments, track the execution of a directive and automatic catch/retry on exceptions (actual Themis Core). These two should be split in the future.
- **Themis Runner**: A container-based solution for running  python scripts. The python is pre-configured with Themis Core, so Themis Lang is enabled for implementing FOPs in python.
- **VS Code extension for Themis** A VS Code extension that creates a panel raising prompts and returning operator responses to the themis script over HTTP.
- **VS Code python integration for Themis** A python extension to Themis Lang that asks the VS Code extension for input (retry decorator with console fallback)

---

## Repository Layout

```text
themis_fop_core/           # Themis Core: Implementation of Themis Lang (domain specific primitives) and support helpers (e.g. tracing, retry logic, sinks, etc.)
fop_runner/                # Themis Runner: Implementation of a script running based on docker containers. Each script runs isolated in a different and unique identified container.
vscode-fops-prompter/      # VS Code extension providing a panel for responding prompts
```

---

## Quickstart

1. Build and try the Themis Core library first (e.g. without integration with VSCode).
See [Themis Core REAME](themis_fop_core/README.md) for details

2. Setup the development environment for VSCode. This will enable the possibility of building and installing the VSCode Themis Panel (for responding prompts)
   1. Install the **Dev Containers** extension in VS Code.
   2. Reopen the project in a Dev Container:  
      `F1` → **Dev-Containers: Reopen in Container**

   > Tip: Dev Containers requires Docker (or a compatible backend) running on your machine.

   > Tip: Dev Containers configuration (.devcontainers in root) installs automatically Themis Core. But:
      * Does not build it!!!! Remember to build it before.
      * If you change it, you will need to re-build the dev container to re-install the new version.


3. Try the VSCode panel for responding prompts
   > Note: The extension is **built automatically** by the Dev Container, but **not installed**.
   >  
   > After the container starts, a file like **`fops-prompter-x.y.z.vsix`** should appear in **`vscode-fops-prompter/`**.

   1. Install the VSCode extension
      1. In `vscode-fops-prompter/`, right-click the `.vsix` → **Install**.
      2. Open the prompter UI:  
      `F1` → **FOPs: Open Prompter**
   2. **Keep this prompter window open**.
   3. Open themis_fop_core/fop2.py
   4. Run it
   5. The execution should stop and prompt for response when sending the command "COMMAND_EX". Respond it using the VSCode panel.


4. Test the Themis Runner
TBW


**** ALL BELOW HERE, TO BE RE-WRITTEN ****
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