from fops.integrations.vscode.retry_vscode import retry_decorator_with_vscode_fallback
from fops.internal.retry import retry_decorator
from fops.internal.sinks import send_trace_data_local
from fops.internal.trace import trace

#__all__ = ["VerifyTM"]

#@retry_decorator
@retry_decorator_with_vscode_fallback
@trace(send_trace_data_local, lines=True, calls=True, returns=True, exceptions=True, capture_values=True, maxlen=160)
def VerifyTM(args):
    if args == 3:
        raise RuntimeError("Simulated exception in VerifyTM")
    return f"Verified TM with args: {args}"
