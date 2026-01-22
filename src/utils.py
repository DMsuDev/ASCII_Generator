import time
import shutil
from functools import wraps
from pathlib import Path
from typing import Optional

from colorama import Fore, Style
from tkinter import Tk, filedialog


# ============================
#   CONSOLE CLEARING
# ============================


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


# ============================
#   FILE DIALOG UTILITIES
# ============================


def get_source_via_dialog(is_video: bool = False) -> str:
    """
    Open a file dialog to select an image or video file.
    Returns the selected file path or empty string if cancelled.
    """
    root = Tk()
    root.withdraw()  # Hide the main window

    if is_video:
        title: str = "Select Video File"
        file_types: list[tuple[str, str]] = [
            ("Video Files", "*.mp4 *.avi *.mov *.mkv *.webm"),
            ("All Files", "*.*"),
        ]
    else:
        title: str = "Select Image File"
        file_types: list[tuple[str, str]] = [
            ("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("All Files", "*.*"),
        ]

    file_path = filedialog.askopenfilename(
        parent=root,
        title=title,
        filetypes=file_types,
        initialdir=str(Path.home()),  # Better default: user home
    )

    root.destroy()  # Clean up
    return file_path


# ============================
#   TERMINAL UTILITIES
# ============================


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


# ============================
#   FPS / TIMING CONTROL
# ============================


def limit_fps(start_time: float, target_fps: int) -> None:
    """
    Sleep if necessary to maintain target FPS.
    Use inside video/camera processing loops.
    """
    if target_fps <= 0:
        return

    frame_duration = 1.0 / target_fps
    elapsed = time.time() - start_time

    if elapsed < frame_duration:
        time.sleep(frame_duration - elapsed)


# ============================
#   LOGGING HELPERS
# ============================


def log_info(msg: str) -> None:
    """Print info message in cyan."""
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {msg}")


def log_warning(msg: str) -> None:
    """Print warning message in yellow."""
    print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {msg}")


def log_error(msg: str) -> None:
    """Print error message in red."""
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")


# ============================
#   IMAGE / ASCII UTILITIES
# ============================


def scale_height(
    target_width: int,
    original_width: int,
    original_height: int,
    scale_factor: float = 0.43,
) -> int:
    """
    Calculate proportional height for ASCII rendering.
    Uses common terminal aspect ratio correction (~0.43–0.55).
    """
    if original_width == 0:
        return 0
    aspect_ratio = original_height / original_width
    return int(target_width * aspect_ratio * scale_factor)


def calc_avg_brightness(r: int, g: int, b: int) -> int:
    """
    Calculate perceived brightness (luminance) using NTSC formula.
    Returns value in [0, 255].
    """
    return int(0.299 * r + 0.587 * g + 0.114 * b)


def get_index_ascii(value: int, ascii_chars: str) -> str:
    """Linear map of luminance → index of ASCII gradient."""
    return ascii_chars[int(value / 255 * (len(ascii_chars) - 1))]


# ============================
#   CONVERSIÓN DE COLORES
# ============================


def rgb_to_ansi(r, g, b, char) -> str:
    """Convert an RGB color to an ANSI TrueColor code.

    Technical explanation:
    ----------------------
    - Modern terminals support colors in real RGB format (TrueColor).
    - The ANSI format for coloring text is:
          \033[38;2;R;G;Bm
      where:
        38  → indicates that the text color is being changed
        2   → indicates that real RGB values will be used
        R,G,B → values between 0 and 255

    - This function simply inserts the RGB values as-is.
      There is no mathematical transformation: it is a direct mapping of the color vector:
          c = (r, g, b) ∈ ℝ³

    - The string "\033[0m" is added at the end to reset the terminal color.
    """

    return f"\033[38;2;{r};{g};{b}m{char}\033[0m"


def gray_to_ansi(gray, char) -> str:
    """
    Convert a grayscale value (0–255) to an ANSI grayscale color (232–255).

    Mathematical explanation:
    -----------------------
    ANSI terminals have a fixed palette of 24 shades of gray:
        {232, 233, ..., 255}

    To map a grayscale value (0–255) to that discrete range, do:

        1) Normalization:
            n = gray / 255
           (converts the gray to a value between 0 and 1)

        2) Scaling to the range of 24 levels:
            i = n * 23
           (23 because there are 24 shades: 0–23)

        3) Quantization by truncation:
            i = floor(i)

        4) Offset to the actual ANSI range:
            color_code = 232 + i

    Final formula:
        color_code = 232 + floor( (gray / 255) * 23 )

    This implements an affine transformation + quantization,
    equivalent to a discrete luminance shader.
    """
    color_code = 232 + int(gray / 255 * 23)
    return f"\033[38;5;{color_code}m{char}\033[0m"


def render_image(
    ascii_frame: str, save: bool = False, filename: Optional[str] = None
) -> None:
    """
    Print ASCII frame to console.
    Optionally save to file if save=True.
    """
    # This is only for debugging purposes (Uncomment if needed)
    # print(ascii_frame if ascii_frame else "Error: No ASCII frame to render.")
    
    if save:
        output_file = filename or f"ascii_output_{int(time.time())}.txt"
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(ascii_frame)
            log_info(f"Saved to: {output_file}")
        except Exception as e:
            log_error(f"Failed to save file: {e}")
