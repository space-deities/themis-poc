import functools
import uuid

from .trace import attempt_var, corr_id_var


def retry_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):


        corr = str(uuid.uuid4())  # one correlation ID across all attempts
        attempt = 1
        while True:
            token_corr = corr_id_var.set(corr)
            token_att = attempt_var.set(attempt)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Exception occurred: {e}")
                choice = input("Options: [r]etry, [s]kip, [c]ancel: ").lower()
                if choice == "r":
                    attempt += 1
                    continue
                elif choice == "s":
                    return None
                elif choice == "c":
                    raise
                else:
                    print("Invalid choice. Retrying...")
                    attempt += 1
                    continue
            finally:
                corr_id_var.reset(token_corr)
                attempt_var.reset(token_att)

    return wrapper
