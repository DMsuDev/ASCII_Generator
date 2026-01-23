import logging
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler


def setup_logging(
    log_file: str = "app.log",
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> None:
    """
    Configure the root logger with two handlers:
      - RotatingFileHandler (detailed, no colors)
      - RichHandler (nice colors, emojis, readable format in console)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # The handlers will filter

    # Avoid duplicates
    if root_logger.handlers:
        return

    # Clean format for file (with logger name)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)-18s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler for rotating file
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
        delay=True,
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(file_formatter)

    # Handler rich for console (very nice)
    rich_handler = RichHandler(
        level=console_level,
        show_time=True,                # Shows the time
        log_time_format="%H:%M:%S",    # Desired format: 18:30:50
        # log_time_format="%H:%M:%S.%f"[:-3],  # if you want milliseconds (123)
        omit_repeated_times=False,     # does not repeat time if it is the same as the previous one
        show_level=True,
        show_path=False,               # does not show file.py:123
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,                   # allows [bold red] in messages if you want
    )

    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(rich_handler)

    # Reduce noise from third-party libraries (PIL) — only show critical errors
    pil_logger = logging.getLogger("PIL")
    pil_logger.setLevel(logging.CRITICAL)
    # Avoid propagation to root to prevent duplicate logs from PIL
    pil_logger.propagate = False


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger with the given name (or module name if None)."""
    if name is None:
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            module = inspect.getmodule(frame.f_back)
            name = module.__name__ if module else "__main__"
    return logging.getLogger(name)