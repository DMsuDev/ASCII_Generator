import shutil
from functools import wraps

def clear_screen(func):
    """Decorator to clear console before executing the wrapped function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        clear_console()
        return func(*args, **kwargs)

    return wrapper


def clear_console() -> None:
    """Clear the terminal/console in a cross-platform way."""
    print("\033c", end="")


def get_terminal_size() -> tuple[int, int]:
    """
    Get current terminal dimensions.
    Returns (columns, lines)
    """
    try:
        size = shutil.get_terminal_size(fallback=(80, 24))
        return size.columns, size.lines
    except Exception:
        return 80, 24  # Safe fallback
