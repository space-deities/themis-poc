from fops.integrations.vscode.prompt_client import ask_vscode
from fops.integrations.vscode.retry_vscode import retry_decorator_with_vscode_fallback
from fops.internal.args import (
    PrimitiveCall,
    PromptType,
    with_args,
)

#from fops.internal.retry import retry_decorator
from fops.internal.sinks import send_trace_data_local
from fops.internal.trace import trace

MODIFIERS = {"Type"}
@retry_decorator_with_vscode_fallback
@trace(send_trace_data_local, lines=True, calls=True, returns=True, exceptions=True, capture_values=True, maxlen=160)
@with_args(allowed_modifiers=MODIFIERS)
def Prompt(call: PrimitiveCall) -> dict:
    
    type    = call.mods.Type
    message = call.spec

    if type is None:
        type = PromptType.OK
    
    response = ask_vscode(f"{message}:\nOptions: Ok (o)?", ['Ok'])
    return {
        "primitive": "Prompt",
        "type": type,
        "modifiers": call.mods,
        "params": call.params,
        "response": response
    }
