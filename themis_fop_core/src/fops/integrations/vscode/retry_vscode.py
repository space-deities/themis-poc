import functools
from .prompt_client import ask_vscode

def retry_decorator_with_vscode_fallback(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Try VS Code prompt first
                try:
                    choice = ask_vscode(f"Exception: {e}\nOptions: retry (r), skip (s), cancel (c)?", ['r','s','c'])
                except Exception:
                    # Fallback to console if VS Code extension not available
                    print(f"Exception occurred: {e}")
                    choice = input("Options: [r]etry, [s]kip, [c]ancel: ").lower()

                choice = (choice or '').strip().lower()
                if choice in ('r','retry'):
                    continue
                elif choice in ('s','skip'):
                    return None
                elif choice in ('c','cancel'):
                    raise
                else:
                    # any custom text -> treat as 'retry'
                    continue
    return wrapper
