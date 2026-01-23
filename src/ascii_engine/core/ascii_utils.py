def calc_avg_brightness(r: int, g: int, b: int) -> int:
    """
    Calculate perceived brightness (luminance) using NTSC formula.
    Returns value in [0, 255].
    """
    return int(0.299 * r + 0.587 * g + 0.114 * b)


def get_index_ascii(value: int, ascii_chars: str) -> str:
    """Linear map of luminance → index of ASCII gradient."""
    return ascii_chars[int(value / 255 * (len(ascii_chars) - 1))]

    """
    Convert an RGB color to an ANSI TrueColor code.
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
