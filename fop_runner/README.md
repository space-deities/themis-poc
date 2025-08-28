# FOP Runner

**Status:** Experimental  
This experiment puts in practice the viability of running in a fully isolated docker container a "debug ready" python script.
The python script is a FOP selected from a set of FOPs made locally available to the container (this supports multiple enhancements!!! :-) 

---

## Objectives

The aim is to validate that we can run unlimited FOPs and attach to any of them using a regular IDE for "step-by-step" execution

A script (FOP) can be:
1. Open: Open a script means starting the container that will wrap the execution of the script. The script could be started in two different modes:
   > Attachable: Means that it will be possible to "attach" a client supporting DAP (Debugger Adapter Protocol), like VSCode or Theia. This is the appropriate mode when the script is started by a person using a IDE. In this mode, the script is always "paused" waiting for the explicit command for "starting" the execution.
   > Non-attachable: Means that the script is launched using a plain python interpreter so no way to attach any IDE for step-by-step execution. In this mode, the script starts the execution automatically as soon as it is opened. 

3. Paused: ....

2. Resumed: A script that is paused (e.g. step-by-step execution) can be resumed. That will run the script without any interruption (unless paused because of explicit request or breakpoint).

3. Step-in:

4. Step-over:

5. Stopped

---

## What’s Included

- **FOPs core** (tracing / retry / sinks) + **domain specific directives**
- A **VS Code extension** that raises prompts and returns operator responses to Python over HTTP
- A **Python integration** that asks the VS Code extension for input (retry decorator with console fallback)

---

## Quickstart

1. Install the **Dev Containers** extension in VS Code.
2. Reopen the project in a Dev Container:  
   `F1` → **Dev-Containers: Reopen in Container**
3. Use the Python debugger to run **`fop.py`**.

> Tip: Dev Containers requires Docker (or a compatible backend) running on your machine.

---

## Configuration

### Supported envs

- **Default:** `127.0.0.1:5533`
- **Change it in VS Code:** `Settings → FOPs Prompter: Port`
- **Update Python client:** set `EXT_PORT` in `integrations/vscode/prompt_client.py`

---
