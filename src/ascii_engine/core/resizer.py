from typing import Tuple
from enum import Enum

import cv2

from ..log import get_logger
from .frames_utils import scale_height
from ..utils import get_terminal_size

# ============================================================
#                  INTERPOLATION ENUM & HELPERS
# ============================================================


class INTERPOLATION(Enum):
    """Available interpolation methods for resizing."""

    NEAREST = cv2.INTER_NEAREST  # Fast, pixelated (good for ASCII precision)
    LINEAR = cv2.INTER_LINEAR  # Default, smooth
    CUBIC = cv2.INTER_CUBIC  # Slower, higher quality
    AREA = cv2.INTER_AREA  # Good for downscaling
    LANCZOS4 = cv2.INTER_LANCZOS4  # Best quality for images


class Resizer:
    """Responsibility: compute target sizes and perform resizing.

    Centralizes resizing/interpolation logic so other modules can remain
    focused on higher-level concerns (SRP, Open/Closed).
    """

    def __init__(self, interpolation: str = "AREA"):
        self.logger = get_logger(__name__)
        self.interpolation = self.get_interpolation_method(interpolation)

    def compute_size(
        self, target_width: int, orig_w: int, orig_h: int, scale_factor: float
    ) -> Tuple[int, int]:
        new_w = min(int(target_width), get_terminal_size()[0])
        new_h = scale_height(new_w, orig_w, orig_h, float(scale_factor))
        return new_w, new_h

    def resize(self, image, size: Tuple[int, int]):
        return cv2.resize(image, (size[0], size[1]), interpolation=self.interpolation)

    def get_interpolation_method(self, name: str) -> int:
        """Maps string names to OpenCV interpolation methods."""
        try:
            return INTERPOLATION[name.upper()].value
        except KeyError:
            self.logger.warning(f"Unknown interpolation '{name}', defaulting to INTER_AREA")
            return cv2.INTER_AREA  # Default fallback
