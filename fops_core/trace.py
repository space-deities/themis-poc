import sys
import linecache
import functools
import contextvars

# Context shared with retry wrapper (per-attempt metadata)
corr_id_var = contextvars.ContextVar("corr_id", default=None)
attempt_var = contextvars.ContextVar("attempt", default=1)

__all__ = ["trace", "safe_repr", "corr_id_var", "attempt_var"]

def safe_repr(obj, *, maxlen=120):
    try:
        s = repr(obj)
    except Exception as e:
        s = f"<unreprable {type(obj).__name__}: {e}>"
    return (s if len(s) <= maxlen else s[: maxlen - 3] + "...")

def _render_call_args(args, kwargs, *, maxlen=120):
    parts = [safe_repr(a, maxlen=maxlen) for a in args]
    parts += [f"{k}={safe_repr(v, maxlen=maxlen)}" for k, v in kwargs.items()]
    joined = ", ".join(parts)
    return joined if len(joined) <= maxlen else joined[: maxlen - 3] + "..."

def trace(
    sink,
    *,
    lines=True,
    calls=True,
    returns=True,
    exceptions=True,
    capture_values=True,
    maxlen=160,
):
    def decorator(func):
        func_code = func.__code__

        def _emit(frame, event, *, code_line=None, ret_val=None, exc=None):
            code_line = code_line or linecache.getline(
                frame.f_code.co_filename, frame.f_lineno
            ).strip()
            meta = {
                "corr_id": corr_id_var.get(),
                "attempt": attempt_var.get(),
            }
            if capture_values:
                if event == "call":
                    meta["args_preview"] = _render_call_args(
                        frame.f_locals.get("__trace_args__", ()),
                        frame.f_locals.get("__trace_kwargs__", {}),
                        maxlen=maxlen,
                    )
                elif event == "return":
                    meta["return_value"] = safe_repr(ret_val, maxlen=maxlen)
                elif event == "exception":
                    etype, eobj, _tb = exc
                    meta["exception_type"] = getattr(etype, "__name__", str(etype))
                    meta["exception"] = safe_repr(eobj, maxlen=maxlen)
            sink(func.__name__, frame.f_lineno, code_line, event, meta)

        def _tracer(frame, event, arg):
            if frame.f_code is func_code:
                if event == "call" and calls:
                    _emit(frame, "call")
                elif event == "line" and lines:
                    _emit(frame, "line")
                elif event == "return" and returns:
                    _emit(frame, "return", code_line="<return>", ret_val=arg)
                elif event == "exception" and exceptions:
                    _emit(frame, "exception", code_line="<exception>", exc=arg)
                return _tracer
            return _tracer

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            prev = sys.gettrace()
            sys.settrace(_tracer)
            try:
                __trace_args__ = args
                __trace_kwargs__ = kwargs
                return func(*args, **kwargs)
            finally:
                sys.settrace(prev)

        return wrapped

    return decorator
