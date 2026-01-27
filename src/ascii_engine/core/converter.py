from typing import Optional
import numpy as np
from ..settings import Mode

# ============================================================
#                  CONVERTER HELPERS
# ============================================================


def calc_avg_brightness(r: int, g: int, b: int) -> int:
    """
    Calculate perceived brightness (luminance) using NTSC formula.
    Returns value in [0, 255].
    """
    return int(0.299 * r + 0.587 * g + 0.114 * b)


def get_index_ascii(value: int, ascii_chars: str) -> str:
    """Linear map of luminance → index of ASCII gradient."""
    return ascii_chars[int(value / 255 * (len(ascii_chars) - 1))]


def rgb_to_ansi(r, g, b, char) -> str:
    """
    Convert an RGB color to an ANSI TrueColor escape sequence.

    - Uses the ANSI format: \033[38;2;R;G;Bm
    - Inserts the RGB values directly (0–255)
    - Appends \033[0m to reset the terminal color
    """
    return f"\033[38;2;{r};{g};{b}m{char}\033[0m"


def gray_to_ansi(gray, char) -> str:
    """
    Map a grayscale value (0–255) to the ANSI 24‑level grayscale range (232–255).

    - Normalize gray to [0,1]
    - Scale to 24 levels (0–23)
    - Convert to ANSI grayscale code: 232 + level
    """
    color_code = 232 + int(gray / 255 * 23)
    return f"\033[38;5;{color_code}m{char}\033[0m"


class Converter:
    """Encapsula la lógica de convertir imágenes (gray + color) a ASCII.

    Objetivo: cambiar la forma de mapear píxeles a caracteres sin tocar
    `Processor` ni la captura de frames.
    """

    def __init__(self):
        pass

    def convert(
        self,
        gray: np.ndarray,
        color_frame: Optional[np.ndarray],
        gradient,
        mode: Mode,
    ) -> str:
        if gray is None or gray.size == 0:
            return ""

        h, w = gray.shape
        ascii_lines = []
        for y in range(h):
            row = []
            for x in range(w):
                pixel_val = int(gray[y, x])
                char = get_index_ascii(pixel_val, gradient)

                if mode == Mode.RGB and color_frame is not None:
                    b, g, r = color_frame[y, x]
                    row.append(rgb_to_ansi(r, g, b, char))
                elif mode == Mode.GRAYSCALE:
                    row.append(gray_to_ansi(pixel_val, char))
                else:
                    row.append(char)
            ascii_lines.append("".join(row))

        return "\n".join(ascii_lines)
