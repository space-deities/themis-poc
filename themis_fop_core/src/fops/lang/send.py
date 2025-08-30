from fops.integrations.vscode.retry_vscode import retry_decorator_with_vscode_fallback
from fops.internal.args import (
    Modifiers,
    PrimitiveCall,
    normalize_conditions,
    with_args,
)

#from fops.internal.retry import retry_decorator
from fops.internal.sinks import send_trace_data_local
from fops.internal.trace import trace

MODIFIERS = {"Delay", "Tolerance", "OnFailure", "PromptUser", "Confirm", "Notify"}
@retry_decorator_with_vscode_fallback
@trace(send_trace_data_local, lines=True, calls=True, returns=True, exceptions=True, capture_values=True, maxlen=160)
@with_args(allowed_modifiers=MODIFIERS)
def Send(call: PrimitiveCall) -> dict:
    
    # Command can be positional (spec) or keyword param
    command = call.spec or call.params.get("command")

    if command == 'COMMAND_EX':
        raise ValueError("Simulated exception in SendTC")
    
    return {
        "primitive": "Send",
        "command": command,
        "modifiers": call.mods,
        "params": call.params,
    }
