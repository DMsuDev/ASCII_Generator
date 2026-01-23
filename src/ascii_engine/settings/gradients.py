from enum import Enum, auto

from ..log import get_logger

logger = get_logger(__name__)

class Gradient(Enum):
    BASIC     = auto()
    DETAILED  = auto()
    LIGHT     = auto()
    COLOR     = auto()
    FILLED    = auto()

GRADIENT_RAMP: dict[Gradient, str] = {
    Gradient.BASIC: r"$@B%8&WM# ",
    Gradient.DETAILED: r"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    Gradient.LIGHT: r"8@$e*+!:. ",
    Gradient.COLOR: r"◍sr*.",
    Gradient.FILLED: r"█▓▒░ ",
}

def get_gradient(name: str) -> Gradient:
    """
    Convert gradient name (string) to enum.
    
    Returns DETAILED as fallback.
    """
    name = name.strip().upper()
    try:
        return Gradient[name]
    except KeyError:
        logger.warning(f"Invalid gradient '{name}', using DETAILED as default")
        return Gradient.DETAILED

def get_gradient_ramp(gradient: Gradient) -> str:
    """Get the character string corresponding to the gradient"""
    try:
        return GRADIENT_RAMP[gradient]
    except KeyError:
        logger.warning(f"Gradient '{gradient}' not found, using DETAILED as default")
        return GRADIENT_RAMP[Gradient.DETAILED]