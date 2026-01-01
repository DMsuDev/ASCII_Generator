from enum import Enum

#=================================
#         ENUMERATORS
#=================================

class MODE(Enum):
    """Modo de renderizado del motor ASCII."""
    RGB = 1
    GRAYSCALE = 2
    ASCII = 3


class GRADIENT(Enum):
    """Gradientes ASCII disponibles para el render."""
    BASIC = "$@B%8&WM# "
    DETAILED = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    LIGHT = "8@$e*+!:.  "
    COLOR = "◍sr*."
    FILLED = "█▓▒░"


#=================================
#             DEFAULTS
#=================================

DEFAULT_SETTINGS: dict = {
    'fps': 24,
    'width': 120,
    'scale_factor': 0.55,
    'mode': MODE.RGB.name,
    'gradient': GRADIENT.BASIC.name,
}
