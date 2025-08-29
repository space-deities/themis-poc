import requests

#__all__ = ["send_trace_data_local", "send_trace_data_http"]

def send_trace_data_local(function_name, line_number, code_line, event, meta):
    cid = meta.get("corr_id")
    att = meta.get("attempt")
    extras = []
    if "args_preview" in meta:
        extras.append(f"args={meta['args_preview']}")
    if "return_value" in meta:
        extras.append(f"ret={meta['return_value']}")
    if "exception" in meta:
        extras.append(f"exc={meta['exception_type']}: {meta['exception']}")
    extras_str = " | " + " | ".join(extras) if extras else ""
    print(f"[{cid}#{att}] {event.upper()} {function_name}:{line_number} {code_line}{extras_str}")

def send_trace_data_http(function_name, line_number, code_line, event, meta):
    url = "https://www.postb.in/1754159125190-8677816796116"
    payload = {
        "event": event,
        "function": function_name,
        "line_number": line_number,
        "code_line": code_line,
        "meta": meta,
    }
    try:
        r = requests.post(url, json=payload, timeout=5)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send trace data: {e}")
