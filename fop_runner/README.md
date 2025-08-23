# FOP Runner

**Status:** Experimental  
This experiment puts in practice the viability of running in a fully isolated docker container a "debug ready" python script.
The python script is a FOP selected from a set of FOPs made locally available to the container (this supports multiple enhancements!!! :-) 

---

## Objectives

The aim is to validate that we can run unlimited FOPs and attach to any of them using a regular IDE for "step-by-step" execution

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
