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

# =====================================================
#          HELPER FUNCTIONS FOR CONFIG HANDLING
# =====================================================


def get_mode_from_name(name: str) -> MODE:
    """
    Safely convert string mode name to MODE enum.
    Returns MODE.RGB as fallback on invalid value.
    """
    try:
        return MODE[name.upper()]
    except (KeyError, ValueError):
        print(f"[WARN] Invalid mode '{name}', falling back to RGB")
        return MODE.RGB


def get_gradient_from_name(name: str) -> GRADIENT:
    """
    Safely convert string gradient name to GRADIENT enum.
    Returns GRADIENT.DETAILED as fallback on invalid value.
    """
    try:
        return GRADIENT[name.upper()]
    except (KeyError, ValueError):
        print(f"[WARN] Invalid gradient '{name}', falling back to DETAILED")
        return GRADIENT.DETAILED


def normalize_runtime_settings(raw_settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert raw config (from JSON) to runtime-ready dict with enums.
    Used after ConfigManager.load()
    """
    normalized = raw_settings.copy()

    # Convert string names → enum instances
    if "mode" in normalized:
        normalized["mode"] = get_mode_from_name(normalized["mode"])

    if "gradient" in normalized:
        normalized["gradient"] = get_gradient_from_name(normalized["gradient"])

    # Ensure numeric types (in case JSON loaded them as str)
    for key in ["fps", "width"]:
        if key in normalized:
            try:
                normalized[key] = int(normalized[key])
            except (ValueError, TypeError):
                normalized[key] = DEFAULT_SETTINGS[key]

    for key in ["scale_factor"]:
        if key in normalized:
            try:
                normalized[key] = float(normalized[key])
            except (ValueError, TypeError):
                normalized[key] = DEFAULT_SETTINGS[key]

    return normalized
