from fops_core.trace import trace
from fops_core.retry import retry_decorator
from fops_core.sinks import send_trace_data_local
from integrations.vscode.retry_vscode import retry_decorator_with_vscode_fallback

__all__ = ["SendTC", "VerifyTM"]

#@retry_decorator
@retry_decorator_with_vscode_fallback
@trace(send_trace_data_local, lines=True, calls=True, returns=True, exceptions=True, capture_values=True, maxlen=160)
def SendTC(args):
    if args == 2:
        raise ValueError("Simulated exception in SendTC")
    return f"Sent TC with args: {args}"

@retry_decorator
@trace(send_trace_data_local, lines=True, calls=True, returns=True, exceptions=True, capture_values=True, maxlen=160)
def VerifyTM(args):
    if args == 3:
        raise RuntimeError("Simulated exception in VerifyTM")
    return f"Verified TM with args: {args}"
