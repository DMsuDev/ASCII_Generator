from enum import Enum, auto
from typing import Any, Dict

# =================================
#         ENUMERATORS
# =================================


class MODE(Enum):
    """
    Rendering mode for the ASCII engine.

    - RGB: Full ANSI color (24-bit)
    - GRAYSCALE: 256-level ANSI grayscale
    - ASCII: Plain characters (no color)
    """

    RGB = auto()
    GRAYSCALE = auto()
    ASCII = auto()


class GRADIENT(Enum):
    """
    Character sets / ramps used for brightness-to-character mapping.

    The order matters: darker → brighter (left to right)
    """

    BASIC = r"$@B%8&WM# "
    DETAILED = (
        r"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    )
    LIGHT = r"8@$e*+!:. "
    COLOR = r"◍sr*."
    FILLED = r"█▓▒░ "


# =====================================================
#               DEFAULT CONFIGURATION
# =====================================================

DEFAULT_SETTINGS: Dict[str, Any] = {
    # Video / real-time processing
    "fps": 24,  # Target FPS for camera/video modes
    "width": 120,  # Target character width (columns)
    "scale_factor": 0.43,  # Height scaling factor (terminal chars are ~2:1 aspect)
    
    # Rendering options
    "mode": MODE.RGB.name,  # Must be a valid MODE.name (str)
    "gradient": GRADIENT.DETAILED.name,  # Must be a valid GRADIENT.name (str)
    
    # Future / optional settings (can be added later)
    # "invert": False,
    # "mirror": False,
    # "charset_custom": None,
    # "output_dir": "./output",
}
