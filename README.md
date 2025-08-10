# Satellite Flight Operational Procedures (FOPs) in Python
Personal experiments for having a reasonable environment for writting, debugging and running satellite flight operational procedures using python. 

This bundle contains:
- The FOPs project (tracing/retry/sinks + primitives)
- A VS Code extension that shows prompts and returns responses to Python over HTTP
- A Python integration to ask the VS Code extension for input (retry decorator fallback)

## Layout
```
fops_core/                 # tracing, retry, sinks
primitives/                # SendTC, VerifyTM (decorated)
integrations/vscode/       # Python client + retry decorator that uses VS Code prompts
vscode-fops-prompter/      # VS Code extension (TypeScript)
fop.py                     # sample script
```

## Quickstart

### VSCode development environment
1. Install the VSCode extension Dev-Containers
2. Re-open the project using Dev-Containers (F1->Dev-Containers: Reopen ...)
3. Debug fop.py using the python debugger

### VSCode extension
The extension is automatically built by dev-containers, but not installed.
So, in the vscode-fopts-prompter, shoould appear after starting the dev-container the fops-prompter-x.y.z.vsix.

Just install it: 
1. Install it (Right click -> Install)
2. Run the command **FOPs: Open Prompter** to open the UI (F1 -> FOPS: Open Prompter)
5. Keep this host window open while running Python.

## How it works
When defining a new directive, use the standard retry decorator (console prompt) from `fops_core.retry` **or** use the VS Code aware one:
```python
from integrations.vscode.retry_vscode import retry_decorator_with_vscode_fallback

@retry_decorator_with_vscode_fallback
def SendTC(args):
    ...
```
When an exception happens, it will try to prompt via the VS Code extension first; if not available, it falls back to console input.

## Configure port
The VSCode extension listens on `127.0.0.1:5533` by default. You can change it in VS Code Settings → FOPs Prompter: Port and also adjust `EXT_PORT` in `integrations/vscode/prompt_client.py` accordingly.

